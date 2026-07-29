# Tally Chatbot

A chatbot your contacts use (hosted on Vercel) that answers questions from your
**live TallyPrime** data via Gemini.

## Architecture

```
Contact browser ──► Vercel (Next.js)                     [public, on your domain]
                     • chat UI + access passcode
                     • server-side GEMINI_API_KEY
                     • Gemini function-calling picks a Tally tool
                          │  HTTPS + Bearer token         [secret, server-side only]
                          ▼
                     Cloudflare quick tunnel  ──►  your laptop
                                                   • proxy/  (FastAPI, READ-ONLY) :8787
                                                        │
                                                        ▼
                                                   TallyPrime gateway :9000  (Bottles)
```

**Security model:** Tally's `:9000` gateway has no auth, so we never expose it
directly. We tunnel a **read-only proxy** that (a) requires a bearer token and
(b) only allows fixed, whitelisted report queries (see `proxy/tally_client.py`).
Use **educational/test company data only** — never real client financials.

## Local side (your laptop)

Prereq: TallyPrime open in Bottles with the gateway on `:9000`
(`Client Server=Server`, `ServerPort=9000` in tally.ini).

```bash
./start-local.sh        # starts proxy + tunnel, prints the public TUNNEL URL
```

Copy the printed `https://xxx.trycloudflare.com` URL — it goes into Vercel as
`TALLY_PROXY_URL`. **It changes each restart** (quick tunnel); update Vercel and
redeploy when it does.

Proxy endpoints (all except `/health` need `Authorization: Bearer <token>`):
`/health` · `/companies` · `/ledgers` · `/ledger?name=` · `/receivables` · `/payables`

## Cloud side (Vercel — built in `web/`, next step)

Env vars to set in Vercel (Project → Settings → Environment Variables):

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | your Google AI Studio key (rotate the one shared in chat!) |
| `TALLY_PROXY_URL` | the tunnel URL from `start-local.sh` |
| `TALLY_PROXY_TOKEN` | matches `proxy/.env` `TALLY_PROXY_TOKEN` |
| `ACCESS_PASSCODE` | a passcode you give to your contacts |

## Status
- [x] Phase 1 — local read-only proxy (tested against live Tally)
- [x] Phase 2 — Cloudflare tunnel (verified end-to-end)
- [ ] Phase 3 — Next.js app (Gemini function-calling + passcode + rate limit)
- [ ] Phase 4 — deploy to Vercel, share with contacts
