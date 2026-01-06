# 🔔 Kalembang

Local LAN alarm controller for Orange Pi 5 with L298N motor driver.

**Kalembang** (Kalinga: "bell" / "alarm") controls two clock motors via a web interface accessible on your local network.

## ✨ Features

- **Two clock motors** controlled via L298N dual H-bridge
- **Alarm scheduling** with daily/weekday/weekend/custom day support
- **12-hour AM/PM time display** with animated digital clock
- **Physical STOP button** for emergency shutdown with latch
- **Auto-off timers** for alarms (configurable duration)
- **PWM duty cycle** control for motor speed
- **Demo mode** for showcasing UI without hardware
- **Cloudflare Pages** deployment with GitHub Actions

## 🖥️ Tech Stack

**Backend:**
- Python 3 + FastAPI + Uvicorn
- SQLite database for alarm persistence
- wiringOP GPIO control

**Frontend:**
- React 18 + TypeScript + Vite
- TanStack Router (client-side routing)
- TanStack Query (server state management)
- Motion (Framer Motion) animations
- Zod form validation
- Bun package manager

## 🚀 Quick Start

### Development (on your Mac)

```bash
./scripts/dev-setup.sh

cd api && ./scripts/dev-run.sh

cd client && bun run dev
```

### Demo Mode (no hardware needed)

```bash
cd client && bun run dev:demo
```

### Production (on Orange Pi 5)

```bash
sudo ./api/scripts/setup.sh
```

## 📁 Project Structure

```
kalembang/
├── api/                    # FastAPI backend
│   ├── kalembang/
│   │   ├── main.py         # FastAPI app + alarm scheduler
│   │   ├── gpio.py         # Motor control
│   │   ├── database.py     # SQLite alarm storage
│   │   └── config.py       # Pin configuration
│   └── systemd/            # Service files
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Route pages
│   │   ├── lib/            # API + queries + demo
│   │   └── router.tsx      # TanStack Router config
│   └── dist/               # Built demo (gitignored)
├── .github/workflows/      # CI/CD
│   └── deploy-demo.yml     # Cloudflare Pages deployment
└── docs/                   # Hardware documentation
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/status` | Get clock states and stop status |
| GET | `/api/v1/time` | Get server time |
| POST | `/api/v1/clock/{1,2}/on` | Turn on clock motor |
| POST | `/api/v1/clock/{1,2}/off` | Turn off clock motor |
| POST | `/api/v1/clock/{1,2}/duty` | Set duty cycle (0-100) |
| POST | `/api/v1/clock/all/off` | Emergency all off |
| POST | `/api/v1/stop/trigger` | Trigger emergency stop |
| POST | `/api/v1/stop/clear` | Clear stop latch |
| GET | `/api/v1/alarms` | List all alarms |
| POST | `/api/v1/alarms` | Create alarm |
| GET | `/api/v1/alarms/{id}` | Get alarm by ID |
| PUT | `/api/v1/alarms/{id}` | Update alarm |
| DELETE | `/api/v1/alarms/{id}` | Delete alarm |
| PATCH | `/api/v1/alarms/{id}/toggle` | Enable/disable alarm |

## 🎮 Demo

Live demo: [kalembang.pages.dev](https://kalembang.pages.dev)

The demo uses simulated data and runs entirely in the browser.

## 🛠️ Hardware Requirements

- Orange Pi 5 with GPIO headers
- L298N dual H-bridge motor driver
- Two small DC motors (clock motors)
- Momentary push button (STOP)
- 4.7kΩ pulldown resistors (x6)
- 5V/4A power supply

## 🍊 Orange Pi 5 Setup

### Prerequisites

Install required packages on your Orange Pi 5:

```bash
sudo apt update && sudo apt install -y python3.11-venv
```

### Self-Hosted Runner Permissions

The GitHub Actions self-hosted runner needs passwordless sudo for systemctl commands. Run as root:

```bash
sudo tee /etc/sudoers.d/kalembang-deploy > /dev/null << 'EOF'
orangepi ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop kalembang.service
orangepi ALL=(ALL) NOPASSWD: /usr/bin/systemctl start kalembang.service
orangepi ALL=(ALL) NOPASSWD: /usr/bin/systemctl enable kalembang.service
orangepi ALL=(ALL) NOPASSWD: /usr/bin/systemctl status kalembang.service
orangepi ALL=(ALL) NOPASSWD: /usr/bin/systemctl daemon-reload
orangepi ALL=(ALL) NOPASSWD: /usr/bin/systemctl enable kalembang-gpio-safety.timer
orangepi ALL=(ALL) NOPASSWD: /usr/bin/systemctl start kalembang-gpio-safety.timer
orangepi ALL=(ALL) NOPASSWD: /bin/cp * /etc/systemd/system/*
orangepi ALL=(ALL) NOPASSWD: /usr/bin/journalctl -u kalembang *
EOF
sudo chmod 440 /etc/sudoers.d/kalembang-deploy
```

### GPIO Safety Monitor

A systemd timer runs every 60 seconds to ensure GPIO pins are LOW when the main service isn't running:

```bash
sudo systemctl status kalembang-gpio-safety.timer
```

You can also manually reset pins:

```bash
/home/orangepi/kalembang/api/scripts/gpio-safety.sh reset
```

### GPIO Access

Ensure the `orangepi` user has access to GPIO. wiringOP should be pre-installed on Orange Pi OS.

```bash
gpio readall
```

See [docs/pinmap.md](docs/pinmap.md) for pin mapping and [docs/wiring.md](docs/wiring.md) for wiring reference.

## 📄 License

MIT
