"""
Thin, READ-ONLY client for the TallyPrime HTTP-XML gateway (localhost:9000).

Design rules (security):
- Only builds Export/Collection requests. It NEVER sends TALLYREQUEST=Import,
  so it cannot create or modify vouchers/masters through this client.
- Every request the proxy can trigger is defined here as a fixed template.
  The HTTP layer (main.py) does not accept arbitrary XML from callers.
"""
import os
import re
import xml.etree.ElementTree as ET

import requests

TALLY_URL = os.getenv("TALLY_URL", "http://localhost:9000")
TIMEOUT = float(os.getenv("TALLY_TIMEOUT", "20"))


# ---------------------------------------------------------------------------
# Low-level transport
# ---------------------------------------------------------------------------
def _clean(xml: str) -> str:
    """Tally injects raw control characters and numeric entities (e.g. &#4;)
    that break standard XML parsers. Strip anything below 0x20 except \t \n \r."""
    xml = "".join(ch for ch in xml if ch >= " " or ch in "\t\n\r")
    xml = re.sub(
        r"&#(\d+);",
        lambda m: m.group(0) if int(m.group(1)) >= 32 or int(m.group(1)) in (9, 10, 13) else "",
        xml,
    )
    return xml


def _post(xml: str) -> str:
    resp = requests.post(
        TALLY_URL,
        data=xml.encode("utf-8"),
        headers={"Content-Type": "text/xml; charset=utf-8"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return _clean(resp.content.decode("utf-8", errors="replace"))


def ping() -> tuple[bool, str]:
    """Cheap reachability check for /health."""
    try:
        _post(_COLLECTION("List of Companies", "Company", ["Name"]))
        return True, "gateway responded"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


# ---------------------------------------------------------------------------
# Request builders (READ-ONLY: TALLYREQUEST is always "Export")
# ---------------------------------------------------------------------------
def _COLLECTION(coll_id: str, tally_type: str, fetch: list[str], company: str | None = None) -> str:
    company_var = f"<SVCURRENTCOMPANY>{_esc(company)}</SVCURRENTCOMPANY>" if company else ""
    fetch_xml = "".join(f"<FETCH>{f}</FETCH>" for f in fetch)
    return (
        "<ENVELOPE>"
        "<HEADER><VERSION>1</VERSION><TALLYREQUEST>Export</TALLYREQUEST>"
        f"<TYPE>Collection</TYPE><ID>{coll_id}</ID></HEADER>"
        "<BODY><DESC><STATICVARIABLES>"
        "<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>"
        f"{company_var}"
        "</STATICVARIABLES>"
        "<TDL><TDLMESSAGE>"
        f'<COLLECTION NAME="{coll_id}" ISMODIFY="No" ISFIXED="No" ISINITIALIZE="No">'
        f"<TYPE>{tally_type}</TYPE>{fetch_xml}</COLLECTION>"
        "</TDLMESSAGE></TDL></DESC></BODY></ENVELOPE>"
    )


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def _rows(xml: str, tag: str, fields: list[str]) -> list[dict]:
    """Parse a Tally collection response into a list of dicts.

    Tally quirks handled here:
    - Master name lives in the element's NAME attribute (<LEDGER NAME="Cash">),
      not a child element.
    - The response embeds a CMPINFO block with count elements like
      <LEDGER>0</LEDGER>; those have no NAME attribute and no children, so we
      skip them.
    """
    out: list[dict] = []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return out
    for el in root.iter(tag.upper()):
        name_attr = el.get("NAME")
        if name_attr is None and len(el) == 0:
            continue  # CMPINFO count element, not a real record
        row = {}
        for f in fields:
            if f.lower() == "name":
                val = name_attr
                if not val:
                    nested = el.find(".//NAME")
                    val = nested.text if nested is not None and nested.text else ""
                row[f] = (val or "").strip()
            else:
                child = el.find(f.upper())
                row[f] = (child.text or "").strip() if child is not None and child.text else ""
        out.append(row)
    return out


_company_cache: str | None = None


def current_company() -> str | None:
    """The loaded company name, used as the default when a caller doesn't
    specify one. Cached after first lookup."""
    global _company_cache
    if _company_cache:
        return _company_cache
    for c in list_companies():
        if c.get("Name"):
            _company_cache = c["Name"]
            return _company_cache
    return None


# ---------------------------------------------------------------------------
# Public, whitelisted read operations
# ---------------------------------------------------------------------------
def list_companies() -> list[dict]:
    xml = _post(_COLLECTION("List of Companies", "Company", ["Name", "StartingFrom"]))
    return _rows(xml, "Company", ["Name", "StartingFrom"])


def list_ledgers(company: str | None = None) -> list[dict]:
    company = company or current_company()
    xml = _post(_COLLECTION("List of Ledgers", "Ledger", ["Name", "Parent", "ClosingBalance"], company))
    return _rows(xml, "Ledger", ["Name", "Parent", "ClosingBalance"])


def ledger_balance(name: str, company: str | None = None) -> dict:
    for row in list_ledgers(company):
        if row["Name"].lower() == name.lower():
            return row
    return {"Name": name, "error": "ledger not found"}


def outstanding_by_group(group: str, company: str | None = None) -> list[dict]:
    """Ledgers under a group (e.g. 'Sundry Debtors' = receivables,
    'Sundry Creditors' = payables) with non-zero closing balance."""
    rows = [r for r in list_ledgers(company) if r["Parent"].lower() == group.lower()]
    return [r for r in rows if r["ClosingBalance"] not in ("", "0", "0.00")]
