# Kalembang Troubleshooting

## Motors run at boot

Likely causes:
- ENA/ENB still effectively HIGH (jumper caps left on, or pulled up)
- IN pins floating high

Fix:
- Confirm ENA/ENB caps removed
- Add 4.7k pulldowns to ENA/ENB + IN pins
- Ensure server sets ENA/ENB low immediately on start
- If still occurs, consider device-tree gpio-hog later

## Motor does not run

- Confirm L298N power:
  - Measure 5V at Vs/+12V and +5V pins, and ground continuity
- Confirm ENA/ENB actually toggling:
  - Use multimeter on ENA/ENB relative to GND
- Confirm IN pin direction:
  - Try swapping motor leads on OUT terminals or swap IN high/low

## Weird buzzing or “brake” behavior

- Avoid INx=INy=HIGH on a channel (brake mode)
- Use fixed direction IN1=1 IN2=0 etc.
- Prefer switching enable (ENA/ENB) for ON/OFF

## GPIO mapping confusion

- Always start with `gpio readall` and record mapping to physical pins
- Keep config in one place (`api/kalembang/config.py`)
- Provide a `scripts/pinmap.md` in docs with the final chosen pins
