# Kalembang Hardware — L298N + Orange Pi 5 wiring

## Goal

- Two clock motors controlled by L298N:
  - Clock #1 motor on OUT1/OUT2 (Motor A)
  - Clock #2 motor on OUT3/OUT4 (Motor B)
- ENA/ENB caps removed so OP5 controls enable (and future PWM)

---

## L298N pin meaning (practical)

- **Motor A**: OUT1 / OUT2, controlled by IN1/IN2, enabled by ENA
- **Motor B**: OUT3 / OUT4, controlled by IN3/IN4, enabled by ENB
- Board terminals often label motor supply as “+12V” but it is really **Vs** (motor supply). We feed **5V** for this project.

---

## Power wiring (single 5V rail)

Use a breadboard rail or direct wiring:

- OP5 **5V** → L298N **Vs** (often “+12V”) AND L298N **+5V logic**
- OP5 **GND** → L298N **GND**
- All grounds must be common (OP5, L298N, button, any buck converters)

Notes:
- Many L298N boards have a “5V regulator enable” jumper. For this project, prefer supplying 5V logic directly.
- L298N has voltage drop; feeding 5V often yields ~3V at the motor under load.

---

## Control wiring (recommended signal plan)

We will use:
- ENA/ENB = enable (digital now; PWM later)
- IN1–IN4 = direction

### Recommended pin selection (physical header pins)

Because Orange Pi pin mapping differs by OS image, these physical pins are *recommendations* that must be verified with `gpio readall` (see below).

Choose:
- ENA: a PWM-capable pin (candidate: physical pin **16**)
- ENB: a PWM-capable pin (candidate: physical pin **18**)
- IN1/IN2/IN3/IN4: any stable GPIO pins (avoid I2C pins 3/5 and UART pins unless you know you won't use them)

Button input:
- STOP button: choose a GPIO input pin (candidate: physical pin **15**)

If your pinout differs, update the config file in the repo (see `api/kalembang/config.py` in the software docs).

---

## Boot-safe hardware defaults (strongly recommended)

To keep motors OFF on boot while pins float:

Add pulldown resistors to GND:
- ENA → 4.7k → GND
- ENB → 4.7k → GND
- IN1 → 4.7k → GND
- IN2 → 4.7k → GND
- IN3 → 4.7k → GND
- IN4 → 4.7k → GND

Why 4.7k:
- Strong enough to beat weak onboard pull-ups / float conditions
- Still safe for a GPIO to drive HIGH later

Direction for MVP:
- We'll set IN pins in software to a fixed direction:
  - Motor A: IN1=1, IN2=0
  - Motor B: IN3=1, IN4=0

ENA/ENB:
- OFF = 0
- ON  = 1
- PWM later: duty 0–100%

---

## STOP button wiring

Use the simplest robust pattern:

- Button one side → selected GPIO input pin
- Button other side → GND
- Configure the GPIO with internal pull-up in software
- Pressed = LOW

Optional (hardware debounce):
- Add 0.1µF capacitor across button OR handle debounce in software.

---

## Pin mapping checklist (must-do)

Run these on the OP5:

1) Install wiringOP (or any pin utility available on your image):
- If wiringOP exists: `gpio readall`

2) Record the mapping:
- Which physical pins correspond to which GPIO numbers
- Save the output to `docs/pinmap.txt`

3) Update `api/kalembang/config.py`:
- Set the GPIO identifiers used by the backend.

We will not guess `gpiochip/line` in code until pinmap is confirmed.
