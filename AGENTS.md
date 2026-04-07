# Kalembang

**Kalembang** is a local LAN alarm controller for Orange Pi 5 that drives two clock motors via an L298N dual H-bridge. The name means "bell" or "clang" in Tagalog/Kalinga.

## Tech Stack

| Layer | Stack |
|-------|-------|
| Backend | Python 3, FastAPI, Uvicorn, SQLite, wiringOP GPIO |
| Frontend | React 18, TypeScript, Vite, TanStack Router, TanStack Query, Motion (Framer Motion), Zod, Bun |
| Deploy | systemd on Orange Pi 5 (production), Cloudflare Pages via GitHub Actions (demo) |

## Repository Layout

```
kalembang/
├── api/kalembang/
│   ├── main.py            # FastAPI app + alarm scheduler
│   ├── gpio.py            # Motor + button GPIO control (wiringOP CLI)
│   ├── database.py        # SQLite alarm CRUD
│   ├── config.py          # Pin numbers and settings
│   └── pwm.py             # Software PWM
├── api/systemd/           # kalembang.service + gpio-safety timer
├── api/scripts/           # setup.sh, dev-run.sh, gpio-safety.sh
├── client/src/
│   ├── components/        # ClockCard, AlarmItem, DigitalClock, etc.
│   ├── pages/             # HomePage, AlarmsPage, AlarmEditPage
│   ├── lib/
│   │   ├── api.ts         # API client (auto-switches to demo)
│   │   ├── demo.ts        # Mock API for demo mode
│   │   └── queries.ts     # TanStack Query hooks
│   └── router.tsx         # TanStack Router config
├── .github/workflows/     # deploy-demo.yml (Cloudflare), deploy.yml (OP5)
├── .opencode/
│   ├── agents/            # Custom OpenCode subagents
│   └── docs/              # Full project documentation
└── docs/                  # Pinmap and wiring notes
```

## Code Style

CRITICAL: Do NOT add inline comments (`//` or `#`) or multiline comments (`/* */` or block `#`).
Code must be self-documenting through clear naming.
Only Python docstrings (`"""..."""`) for public functions and classes are allowed.
No JSDoc comments in TypeScript.

## API Contract

```
GET    /api/v1/status
GET    /api/v1/time
POST   /api/v1/clock/{1,2}/on
POST   /api/v1/clock/{1,2}/off
POST   /api/v1/clock/{1,2}/duty     { "duty": 0..100 }
POST   /api/v1/clock/all/off
POST   /api/v1/stop/trigger
POST   /api/v1/stop/clear
GET    /api/v1/alarms
POST   /api/v1/alarms
GET    /api/v1/alarms/{id}
PUT    /api/v1/alarms/{id}
DELETE /api/v1/alarms/{id}
PATCH  /api/v1/alarms/{id}/toggle?enabled={bool}
```

## Frontend Patterns

- All API calls go through TanStack Query hooks in `lib/queries.ts`
- 12-hour AM/PM format for all time displays
- Motion animations for UI transitions
- Zod schemas for form validation
- Demo mode auto-detected via `VITE_DEMO_MODE` env var

## Development Commands

Backend (mock GPIO for dev without hardware):
```bash
cd api && KALEMBANG_MOCK_GPIO=1 uvicorn kalembang.main:app --port 8088 --reload
```

Frontend:
```bash
cd client && bun run dev          # with real API
cd client && bun run dev:demo     # demo mode (mock API)
cd client && bun run build:demo   # production demo build
```

## Hardware Context

- Orange Pi 5 + L298N dual H-bridge controlling two small DC clock motors
- ENA/ENB jumper caps removed; OP5 controls enable lines (digital now, PWM later)
- 4.7k pulldown resistors on all control pins (ENA, ENB, IN1-IN4) for boot safety
- Motors OFF by default at boot; only turn on when commanded
- Physical STOP button: GPIO input with internal pull-up, pressed = LOW, latches all motors off
- Reserve header pins 4-6 for fan; avoid I2C pins 3/5 and UART pins

## Key Constraints

- No authentication (LAN-only deployment)
- No Docker containers
- Single 5V rail powers both OP5 and L298N (common ground required)
- Pin mapping must be verified with `gpio readall` on the target board

## Reference Documentation

Detailed specs live in `.opencode/docs/`. Key references:

- Hardware wiring and pin assignments: `.opencode/docs/01_hardware_wiring.md`
- FastAPI backend spec: `.opencode/docs/02_api_fastapi.md`
- React frontend spec: `.opencode/docs/03_client_vite_react_bun.md`
- Deploy runbook: `.opencode/docs/04_deploy_runbook.md`
- Troubleshooting: `.opencode/docs/05_troubleshooting.md`
- PWA setup guide: `.opencode/docs/pwa.md`

For security auditing, use the `@security-auditor` agent.
For alarm pattern design and implementation, use the `@pattern-designer` agent.
