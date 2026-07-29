"""
Local READ-ONLY proxy in front of the TallyPrime gateway.

Runs on the same VPS as Tally. A firewalled public port exposes ONLY this
proxy to the internet, never Tally's raw :9000 port. The Vercel app calls
these endpoints with a bearer token; Gemini can only reach the fixed,
read-only operations defined in tally_client.py.
"""
import os

from dotenv import load_dotenv

load_dotenv()  # must run before importing tally_client, which reads env vars at import time

from fastapi import Depends, FastAPI, Header, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

import tally_client as tally  # noqa: E402

TOKEN = os.getenv("TALLY_PROXY_TOKEN")

app = FastAPI(title="Tally Read-Only Proxy", version="0.1.0")

# The Vercel app calls server-side, but allow CORS from the deployed origin too.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["GET"],
    allow_headers=["Authorization"],
)


def require_token(authorization: str | None = Header(default=None)) -> None:
    if not TOKEN:
        raise HTTPException(status_code=500, detail="Proxy token not configured on server")
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    ok, detail = tally.ping()
    return {"status": "ok", "tally_reachable": ok, "detail": detail}


@app.get("/companies", dependencies=[Depends(require_token)])
def companies():
    return {"companies": tally.list_companies()}


@app.get("/ledgers", dependencies=[Depends(require_token)])
def ledgers(company: str | None = None):
    return {"ledgers": tally.list_ledgers(company)}


@app.get("/ledger", dependencies=[Depends(require_token)])
def ledger(name: str, company: str | None = None):
    return tally.ledger_balance(name, company)


@app.get("/receivables", dependencies=[Depends(require_token)])
def receivables(company: str | None = None):
    return {"receivables": tally.outstanding_by_group("Sundry Debtors", company)}


@app.get("/payables", dependencies=[Depends(require_token)])
def payables(company: str | None = None):
    return {"payables": tally.outstanding_by_group("Sundry Creditors", company)}
