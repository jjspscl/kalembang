# Kalembang API (FastAPI) — detailed build instructions

## MVP behavior

- On boot/service start:
  - Export/init the GPIO backend
  - Force ENA=0, ENB=0 (motors OFF)
  - Set IN pins for fixed direction
- Expose REST endpoints for:
  - clock1 on/off
  - clock2 on/off
  - all off
  - set duty 0–100 (stub or basic software PWM)
- Monitor STOP button:
  - When pressed: immediately set ENA=0 and ENB=0
  - Latch-off until user explicitly turns on again (MVP recommended)

---

## GPIO backend choices (pick one)

### Option A: wiringOP `gpio` command (most reliable mapping for OP boards)

Pros: you can target physical/header mapping easily via `gpio readall`.
Cons: shelling out from Python (still fine for MVP).

### Option B: libgpiod Python (cleaner, but requires correct gpiochip/line mapping)

Pros: modern, fast, direct control.
Cons: mapping can be tricky on OP5 images.

For MVP speed, implement **Option A first**, then add Option B later.

---

## api/ folder structure

- `api/kalembang/`
  - `main.py` — FastAPI app
  - `gpio.py` — motor + button control
  - `config.py` — pin numbers and tuning
  - `pwm.py` — software PWM helper (optional MVP)
  - `__init__.py`
- `api/systemd/`
  - `kalembang.service`
- `api/scripts/`
  - `setup.sh` — install dependencies and enable service
  - `dev-run.sh` — run server in dev
- `api/requirements.txt` or `pyproject.toml`

---

## MVP endpoints (spec)

- `POST /api/v1/clock/1/on`
- `POST /api/v1/clock/1/off`
- `POST /api/v1/clock/2/on`
- `POST /api/v1/clock/2/off`
- `POST /api/v1/clock/all/off`
- `POST /api/v1/clock/1/duty`  body: `{ "duty": 0..100 }`
- `POST /api/v1/clock/2/duty`  body: `{ "duty": 0..100 }`
- `GET  /api/v1/status`        returns current states

Button:
- Not an endpoint; internal watchdog loop.

---

## Example: wiringOP-based GPIO control

Implement `gpio.py` with helpers that call the `gpio` CLI:

- `gpio mode <PIN> out`
- `gpio write <PIN> 0|1`
- `gpio mode <PIN> up` for input pull-up if supported, else use `gpio mode` + logic.

Kalembang configuration is in `config.py`:

- `ENA_PIN`, `ENB_PIN`, `IN1_PIN`, `IN2_PIN`, `IN3_PIN`, `IN4_PIN`, `STOP_BTN_PIN`
- `STOP_LATCH = True`
- `DEFAULT_DUTY = 100` (digital full enable)

---

## Software PWM (later / optional)

For “volume”:
- Use a periodic loop toggling ENA/ENB at 200–1000 Hz.
- Keep IN pins static.
- Duty cycle 0–100 controls average power.

This can be done in Python using `asyncio` tasks per channel.

---

## systemd service (must)

Provide:
- `kalembang.service` runs after network + ensures GPIO initialized
- Uses `Restart=always`
- Runs on a fixed port (e.g. 8088) bound to LAN

Also provide a oneshot “gpio-safeoff” step in ExecStartPre if possible:
- Ensure ENA/ENB set LOW before server starts accepting requests.

---

## Security posture (MVP)

- Bind to LAN IP only (or 0.0.0.0 but firewall to LAN)
- No auth for now
- Keep it separate from tahanan-dashboard
