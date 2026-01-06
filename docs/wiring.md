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
Orange Pi 5                      L298N
────────────────────────────────────────
Pin 7  (wPi 2,  PWM15)      →   ENA (remove jumper!)
Pin 26 (wPi 16, PWM1)       →   ENB (remove jumper!)
Pin 11 (wPi 5,  CAN1_RX)    →   IN1
Pin 13 (wPi 7,  CAN1_TX)    →   IN2
Pin 15 (wPi 8,  CAN2_RX)    →   IN3
Pin 22 (wPi 13, GPIO2_D4)   →   IN4
```

## STOP Button

```
Pin 12 (wPi 6, CAN2_TX)  →  Button  →  GND
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
