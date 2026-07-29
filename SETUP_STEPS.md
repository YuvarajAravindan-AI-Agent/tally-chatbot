# Tally Chatbot - Complete Setup & Startup Steps

## Overview

The Tally Chatbot is a 3-part system:

```
┌─────────────────┐     ┌──────────────────────┐     ┌────────────────┐
│  Vercel Chatbot │────▶│ ngrok Tunnel         │────▶│  Local Proxy   │
│ (Public Web UI) │     │ (Public Internet)    │     │  (Port 8787)   │
└─────────────────┘     └──────────────────────┘     └────────────────┘
                                                              │
                                                              ▼
                                                      ┌────────────────┐
                                                      │  TallyPrime    │
                                                      │  (Port 9000)   │
                                                      │  via Bottles   │
                                                      └────────────────┘
```

---

## Quick Start (3 Simple Steps)

### 1. Open TallyPrime
```bash
# Open Tally via Bottles (Soda runner)
~/.local/share/applications/TallyPrime.desktop

# Or from terminal:
bottles run -p Soda "C:\\Program Files\\Tally.ERP9\\bin\\TALLY.EXE"
```

**Verify it's working:**
```bash
ss -tln | grep 9000  # Should see 127.0.0.1:9000 LISTEN
```

### 2. Start Proxy & Tunnel
```bash
cd ~/Projects/tally-chatbot
bash start
```

**Expected output:**
```
✓ Tally Chatbot is ready!

Local Services:
  Proxy:    http://127.0.0.1:8787 (internal)
  Tunnel:   https://headset-slighting-heave.ngrok-free.dev (public)

Access Chatbot:
  https://tally-chatbot.vercel.app
```

### 3. Use the Chatbot
- Open: https://tally-chatbot.vercel.app
- Enter passcode (set in Vercel environment)
- Ask questions like: "What's my total receivables?"

---

## Detailed Setup (First Time Only)

### Prerequisites Installation

#### 1. Install Python Dependencies
```bash
cd ~/Projects/tally-chatbot/proxy

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install required packages
pip install uvicorn fastapi requests

# Deactivate
deactivate
```

#### 2. Install ngrok
```bash
# Download from https://ngrok.com/download

# Or if you have wget/curl:
mkdir -p ~/bin
cd ~/bin

# Download latest ngrok (check website for latest URL)
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3.x.x-linux-amd64.tgz

# Extract
tar xzf ngrok-v3.x.x-linux-amd64.tgz

# Make executable
chmod +x ngrok

# Verify
./ngrok version
```

#### 3. Verify TallyPrime Setup
```bash
# Check Bottles is installed
bottles --help

# List available runners
bottles list-runtimes

# Verify TallyPrime can launch
bottles run -p Soda "C:\\Program Files\\Tally.ERP9\\bin\\TALLY.EXE" &
```

#### 4. Set Vercel Environment Variables
Go to: https://vercel.com/projects/ai-agentic-accounting/tally-chatbot

Environment Variables needed:
```
TALLY_PROXY_URL = https://headset-slighting-heave.ngrok-free.dev
TALLY_COMPANY_NAME = Yuvaraj
TALLY_PASSCODE = <your-secret-passcode>
```

---

## Daily Usage

### Start Everything
```bash
cd ~/Projects/tally-chatbot
bash start
```

### Stop Everything
```bash
cd ~/Projects/tally-chatbot
bash stop
```

Or manually:
```bash
pkill ngrok        # Stop tunnel
pkill -f uvicorn   # Stop proxy
```

---

## How It Works (Technical)

### Step 1: User Enters Question
- User opens: https://tally-chatbot.vercel.app
- Enters passcode
- Asks: "What's my total receivables?"
- Frontend sends to Vercel backend

### Step 2: Vercel Backend (Google Gemini)
- Receives question
- Calls Google Gemini AI with the question
- Gemini routes query to TALLY_PROXY_URL
- Environment variable points to: https://headset-slighting-heave.ngrok-free.dev

### Step 3: ngrok Tunnel
- Public HTTPS endpoint
- Routes traffic to local proxy on port 8787
- Keeps connection open even if IP changes

### Step 4: Local Proxy (FastAPI)
- Running on http://127.0.0.1:8787
- Receives proxied requests from ngrok
- Reads from TallyPrime on port 9000
- Returns read-only data (never modifies)
- Sends response back through tunnel

### Step 5: Response to User
- Proxy → Tunnel → Vercel → Gemini → Chatbot UI
- User sees answer to their question

---

## File Structure

```
tally-chatbot/
├── start                    # ⭐ Use this to start everything
├── stop                     # ⭐ Use this to stop everything
├── start-local.sh          # Original startup (use 'bash' not 'sh')
├── STARTUP_GUIDE.md        # Beginner-friendly guide
├── SETUP_STEPS.md          # This file - detailed setup
│
├── proxy/                  # FastAPI read-only gateway
│   ├── main.py             # Proxy logic
│   ├── .venv/              # Python environment
│   ├── requirements.txt    # Python dependencies
│   └── README.md
│
├── web/                    # Next.js chatbot UI (deployed to Vercel)
│   ├── app/                # React components
│   ├── pages/              # Next.js pages
│   ├── package.json
│   └── vercel.json
│
└── README.md               # Project overview
```

---

## Troubleshooting

### Error: "Illegal option -o pipefall"
**Cause**: Using `sh` instead of `bash`
**Fix**: 
```bash
bash start-local.sh    # ✅ Correct
sh start-local.sh      # ❌ Wrong
bash start             # ✅ Better (modern wrapper)
```

### Error: "Port 8787 already in use"
```bash
# Find what's using it
lsof -i :8787

# Kill it
pkill -f uvicorn

# Try again
bash start
```

### Error: "TallyPrime not accessible on port 9000"
```bash
# 1. Verify TallyPrime is open
ps aux | grep -i tally

# 2. Check if it's listening
ss -tln | grep 9000

# 3. If not, open it:
~/.local/share/applications/TallyPrime.desktop

# 4. Give it a few seconds to start
sleep 5
```

### Error: "ngrok tunnel failed"
```bash
# Check the error log
cat /tmp/tally-ngrok.log

# Common fixes:
# 1. Verify ngrok is installed
ls -la ~/bin/ngrok

# 2. Check if ngrok is already running
pgrep ngrok

# 3. Kill old ngrok and retry
pkill ngrok
sleep 2
bash start
```

### Chatbot still says "HTTP 404 error"
```bash
# 1. Verify all 3 services are running
ss -tln | grep -E '8787|9000'  # Both should show LISTEN

pgrep ngrok                     # Should show ngrok PID
pgrep -f uvicorn               # Should show proxy PID

# 2. Test the proxy directly
curl http://127.0.0.1:8787

# 3. Test through the tunnel
curl https://headset-slighting-heave.ngrok-free.dev

# 4. Check logs for errors
tail -20 /tmp/tally-proxy.log
tail -20 /tmp/tally-ngrok.log
```

---

## Support Files

- **STARTUP_GUIDE.md** - Beginner-friendly quick start
- **SETUP_STEPS.md** - This file (detailed everything)
- **README.md** - Project overview
- **proxy/README.md** - Proxy-specific details

---

## One-Liner Quick Reference

```bash
# Start
cd ~/Projects/tally-chatbot && bash start

# Stop
cd ~/Projects/tally-chatbot && bash stop

# Check logs
tail -f /tmp/tally-proxy.log
tail -f /tmp/tally-ngrok.log

# Manual service checks
ss -tln | grep -E '8787|9000'
pgrep ngrok
pgrep -f uvicorn
```

---

## Next Steps

1. ✅ Install prerequisites (if first time)
2. ✅ Open TallyPrime
3. ✅ Run `bash start`
4. ✅ Open chatbot at https://tally-chatbot.vercel.app
5. ✅ Enter passcode and ask a question

That's it! The chatbot should now work.
