# Kalembang Deploy & Runbook

## Deployment Options

### 1. Demo Mode (Cloudflare Pages)
- Automatic via GitHub Actions on push to `main`
- Live at: `https://kalembang-demo.pages.dev`
- Uses mock API with in-memory state

### 2. Production (Orange Pi 5)
- FastAPI as systemd service
- Client via Vite dev server or static build

---

## GitHub Actions CI/CD

Push to `main` triggers automatic demo deployment.

**Required Secrets:**
- `CLOUDFLARE_API_TOKEN` - Pages edit permission  
- `CLOUDFLARE_ACCOUNT_ID` - Your account ID

---

## Orange Pi 5 Setup

```bash
cd /opt/kalembang/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
sudo cp systemd/kalembang.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kalembang
```

---

## Environment Variables

**API:** `KALEMBANG_MOCK_GPIO=0` (set 1 for dev without hardware)

**Client:** `VITE_DEMO_MODE=false` (true for demo build)

---

## Quick Checklist

1. Wire L298N + motors + common ground
2. Remove ENA/ENB jumper caps
3. Add pulldowns (4.7k) to ENA/ENB and IN pins
4. Run `gpio readall` and verify pins
5. Start API: `sudo systemctl start kalembang`
6. Test: `curl http://localhost:8088/api/v1/status`
7. Start client: `bun run dev`
8. Test STOP button latch-off
