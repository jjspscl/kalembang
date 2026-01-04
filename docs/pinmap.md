# Hardware Pin Mapping

This file should contain the output of `gpio readall` from your Orange Pi 5.

## Instructions

1. SSH into your Orange Pi 5
2. Run: `gpio readall`
3. Paste the output below
4. Update `api/kalembang/config.py` with the correct pin numbers

## Current Pin Mapping

```
[ Paste gpio readall output here ]
```

## Selected Pins

| Function | wiringOP Pin | Physical Pin | Notes |
|----------|--------------|--------------|-------|
| ENA      | 4            | 16           | Motor A enable (PWM) |
| ENB      | 5            | 18           | Motor B enable (PWM) |
| IN1      | 0            | 11           | Motor A direction |
| IN2      | 2            | 13           | Motor A direction |
| IN3      | 3            | 15           | Motor B direction |
| IN4      | 6            | 22           | Motor B direction |
| STOP BTN | 1            | 12           | Input with pull-up |

**Note:** These are placeholder values. Update after running `gpio readall` on your OP5.
