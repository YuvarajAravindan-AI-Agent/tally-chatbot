#!/usr/bin/env bash
# Starts the local side of the Tally chatbot: the read-only proxy + the ngrok
# tunnel on a FIXED domain. Because the domain is static, the URL never changes
# on restart — no need to touch Vercel again.
#
# Prereq: TallyPrime open in Bottles (gateway on :9000).
# IMPORTANT: Run with `bash start-local.sh` NOT `sh start-local.sh`
set -euo pipefail
cd "$(dirname "$0")"

NGROK_DOMAIN="headset-slighting-heave.ngrok-free.dev"
PROXY_LOG=/tmp/tally-proxy.log
TUNNEL_LOG=/tmp/tally-ngrok.log

# 1. Read-only proxy (only if not already up on 8787)
if ! ss -tln 2>/dev/null | grep -q ':8787'; then
  setsid ./proxy/.venv/bin/uvicorn --app-dir ./proxy main:app \
    --host 127.0.0.1 --port 8787 >"$PROXY_LOG" 2>&1 < /dev/null &
  sleep 2
  echo "proxy: started (log: $PROXY_LOG)"
else
  echo "proxy: already running on :8787"
fi

# 2. ngrok tunnel on the fixed domain (kill any existing ngrok first, by name)
for p in $(pgrep -x ngrok 2>/dev/null || true); do kill "$p" 2>/dev/null || true; done
sleep 1
setsid "$HOME/bin/ngrok" http 8787 --url="https://$NGROK_DOMAIN" \
  --log="$TUNNEL_LOG" --log-format=logfmt >/dev/null 2>&1 < /dev/null &
sleep 4

if grep -q "started tunnel" "$TUNNEL_LOG" 2>/dev/null; then
  echo
  echo "============================================================"
  echo "  TUNNEL UP (stable):  https://$NGROK_DOMAIN"
  echo "  Vercel TALLY_PROXY_URL already points here — nothing to update."
  echo "  Chatbot: https://tally-chatbot.vercel.app"
  echo "============================================================"
else
  echo "!! ngrok did not start cleanly — check $TUNNEL_LOG"
fi
