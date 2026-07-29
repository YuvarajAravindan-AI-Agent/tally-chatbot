// Server-side client for the local read-only Tally proxy (reached via the
// Cloudflare tunnel). Never imported into client components — the token stays
// on the server.

const BASE = process.env.TALLY_PROXY_URL || "";
const TOKEN = process.env.TALLY_PROXY_TOKEN || "";

async function call(path: string): Promise<unknown> {
  if (!BASE || !TOKEN) throw new Error("Tally proxy not configured");
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      // Bypass ngrok's free-tier browser-warning interstitial for server calls.
      "ngrok-skip-browser-warning": "true",
    },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Tally proxy ${path} -> HTTP ${res.status}`);
  return res.json();
}

export const tally = {
  companies: () => call("/companies"),
  ledgers: () => call("/ledgers"),
  ledger: (name: string) => call(`/ledger?name=${encodeURIComponent(name)}`),
  receivables: () => call("/receivables"),
  payables: () => call("/payables"),
};
