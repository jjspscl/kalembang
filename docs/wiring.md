# Kalembang Wiring Reference

Quick reference for wiring the L298N motor driver to Orange Pi 5.

## Power Connections

```
Orange Pi 5           L298N
─────────────────────────────
5V (pin 2 or 4)  →   +5V (logic power)
5V (pin 2 or 4)  →   Vs (+12V terminal, we use 5V)
GND (pin 6)      →   GND
```

## Motor Connections

```
L298N                 Clock Motors
───────────────────────────────────
OUT1/OUT2        →   Clock 1 motor
OUT3/OUT4        →   Clock 2 motor
```

## Control Connections

```
Orange Pi 5           L298N
─────────────────────────────────
GPIO (ENA_PIN)   →   ENA (remove jumper!)
GPIO (ENB_PIN)   →   ENB (remove jumper!)
GPIO (IN1_PIN)   →   IN1
GPIO (IN2_PIN)   →   IN2
GPIO (IN3_PIN)   →   IN3
GPIO (IN4_PIN)   →   IN4
```

## STOP Button

```
GPIO (STOP_BTN_PIN)  →  Button  →  GND
```

(Configure GPIO with internal pull-up; button press = LOW)

## Boot Safety Resistors

Add 4.7kΩ pull-down resistors from each control pin to GND:

- ENA → 4.7kΩ → GND
- ENB → 4.7kΩ → GND
- IN1 → 4.7kΩ → GND
- IN2 → 4.7kΩ → GND
- IN3 → 4.7kΩ → GND
- IN4 → 4.7kΩ → GND

This ensures motors stay OFF during boot when GPIO pins are floating.

## Important Notes

1. **Remove ENA/ENB jumper caps** - We control enable via GPIO
2. **Common ground** - All GND connections must be shared
3. **L298N voltage drop** - Expect ~2V drop, so 5V in ≈ 3V to motor
4. **Fan pins reserved** - Keep header pins 4-6 available for fan
