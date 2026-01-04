# Kalembang

🔔 Local LAN alarm controller for Orange Pi 5 with L298N motor driver.

**Kalembang** (Tagalog: "bell" / "ringing sound") controls two clock motors via a web interface accessible on your local network.

## Features

- **Two clock motors** controlled via L298N dual H-bridge
- **ON/OFF control** with future PWM "volume" support
- **Physical STOP button** for emergency shutdown
- **Web UI** built with React + Vite
- **FastAPI backend** with GPIO control
- **Boot-safe** with hardware pulldowns and systemd service

## Quick Start

### Development (on your Mac)

```bash
# Setup everything
./scripts/dev-setup.sh

# Run API with mock GPIO
cd api && ./scripts/dev-run.sh

# In another terminal, run the UI
cd client && bun run dev
```

Open http://localhost:5173 to see the UI.

### Production (on Orange Pi 5)

1. Wire up the L298N module (see `docs/wiring.md`)
2. Run `gpio readall` and update `api/kalembang/config.py`
3. Install and start the service:

```bash
sudo ./api/scripts/setup.sh
```

## Project Structure

```
kalembang/
├── api/                    # FastAPI backend
│   ├── kalembang/          # Python package
│   │   ├── main.py         # FastAPI app
│   │   ├── gpio.py         # Motor control
│   │   ├── config.py       # Pin configuration
│   │   └── pwm.py          # Software PWM (optional)
│   ├── systemd/            # Service files
│   ├── scripts/            # Setup & dev scripts
│   └── requirements.txt
├── client/                 # Vite + React UI
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   └── components/
│   └── package.json
├── scripts/                # Project-level helpers
└── docs/                   # Wiring & pin mapping
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/status` | Get current status |
| POST | `/api/v1/clock/1/on` | Turn on Clock 1 |
| POST | `/api/v1/clock/1/off` | Turn off Clock 1 |
| POST | `/api/v1/clock/2/on` | Turn on Clock 2 |
| POST | `/api/v1/clock/2/off` | Turn off Clock 2 |
| POST | `/api/v1/clock/all/off` | Turn off all clocks |
| POST | `/api/v1/clock/1/duty` | Set Clock 1 duty (0-100) |
| POST | `/api/v1/clock/2/duty` | Set Clock 2 duty (0-100) |
| POST | `/api/v1/stop/trigger` | Trigger emergency stop |
| POST | `/api/v1/stop/clear` | Clear stop latch |

## Hardware Requirements

- Orange Pi 5 with GPIO headers
- L298N dual H-bridge motor driver
- Two small DC motors (clock motors)
- Momentary push button (STOP)
- 4.7kΩ resistors (x6, for boot safety)
- 5V/4A power supply (USB-C)
- Breadboard and jumper wires

## Configuration

Update pin numbers in `api/kalembang/config.py` after running `gpio readall` on your OP5.

## License

MIT
