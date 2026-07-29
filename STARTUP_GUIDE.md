# Tally Chatbot Startup Guide

## Quick Start

Run this command from the tally-chatbot directory:

```bash
bash start-local.sh
```

**Important**: Use `bash` NOT `sh` — the script requires bash features.

## What Gets Started

When you run `start-local.sh`, it automatically starts:

1. **Read-only Proxy** (uvicorn on port 8787)
   - Forwards requests to TallyPrime via Bottles gateway
   - Location: `./proxy` directory
   - Log file: `/tmp/tally-proxy.log`

2. **ngrok Tunnel** (on stable domain)
   - Tunnels the proxy to public internet
   - Domain: `https://headset-slighting-heave.ngrok-free.dev`
   - Log file: `/tmp/tally-ngrok.log`

## Prerequisites Before Starting

✅ **TallyPrime Must Be Running**
- Open TallyPrime via Bottles (Soda runner)
- Gateway must be accessible on `localhost:9000`
- Launch: `~/.local/share/applications/TallyPrime.desktop`

✅ **Dependencies Installed**
- Python venv in `./proxy/.venv` (with uvicorn)
- ngrok binary at `~/bin/ngrok`

✅ **Environment Variables Set** (Vercel)
- `TALLY_PROXY_URL=https://headset-slighting-heave.ngrok-free.dev`
- `TALLY_COMPANY_NAME=Yuvaraj`
- `TALLY_PASSCODE=<your-passcode>`

## After Startup

Once both services are running, the chatbot works:

1. **Local Setup Active**
   - Proxy: `http://127.0.0.1:8787` (internal only)
   - Tunnel: `https://headset-slighting-heave.ngrok-free.dev` (public)

2. **Vercel Chatbot**
   - Access: `https://tally-chatbot.vercel.app`
   - Queries go through the tunnel to your local proxy
   - Proxy reads from TallyPrime via Bottles gateway

3. **Test It**
   - Open the chatbot URL
   - Enter the passcode
   - Ask: "What's my total receivables?"
   - Should connect and return data

## Troubleshooting

### "Illegal option -o pipefail" error
**Solution**: Run with `bash` instead of `sh`
```bash
bash start-local.sh        # ✅ Correct
sh start-local.sh          # ❌ Wrong
```

### Proxy fails to start (port 8787 in use)
```bash
# Check what's using port 8787
lsof -i :8787

# Kill the existing proxy
pkill -f "uvicorn"

# Then retry
bash start-local.sh
```

### ngrok tunnel fails
```bash
# Check ngrok log
cat /tmp/tally-ngrok.log

# Verify ngrok is installed
~/bin/ngrok version

# Check if ngrok is already running
pgrep ngrok
```

### TallyPrime connection fails (HTTP 404)
1. Verify TallyPrime is open in Bottles
2. Check it's listening on port 9000:
   ```bash
   ss -tln | grep 9000
   ```
3. Verify proxy can reach it:
   ```bash
   curl http://127.0.0.1:9000
   ```

## Logs

All services log to `/tmp/`:

```bash
# Watch proxy in real-time
tail -f /tmp/tally-proxy.log

# Watch tunnel in real-time
tail -f /tmp/tally-ngrok.log
```

## Stopping Services

```bash
# Stop ngrok tunnel
pkill ngrok

# Stop proxy
pkill -f "uvicorn"

# Stop both
bash stop-services.sh  # (optional script)
```

## Project Structure

```
tally-chatbot/
├── proxy/              # Read-only FastAPI proxy
│   └── .venv/          # Python environment with uvicorn
├── web/                # Next.js chatbot (deployed to Vercel)
├── start-local.sh      # Startup script (THIS FILE)
├── STARTUP_GUIDE.md    # Documentation (THIS FILE)
└── README.md           # Project overview
```

## Summary

The chatbot requires:
- **Local**: proxy + tunnel running (start-local.sh)
- **Online**: Vercel hosting (already deployed)
- **Backend**: TallyPrime in Bottles (on localhost:9000)

Once all three are running, the flow is:
```
Chatbot UI → Vercel → ngrok tunnel → Local proxy → TallyPrime
```
