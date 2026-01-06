# Hardware Pin Mapping

This file should contain the output of `gpio readall` from your Orange Pi 5.

## Instructions

1. SSH into your Orange Pi 5
2. Run: `gpio readall`
3. Paste the output below
4. Update `api/kalembang/config.py` with the correct pin numbers

## Current Pin Mapping

```
 +------+-----+----------+--------+---+   OPI5   +---+--------+----------+-----+------+
 | GPIO | wPi |   Name   |  Mode  | V | Physical | V |  Mode  | Name     | wPi | GPIO |
 +------+-----+----------+--------+---+----++----+---+--------+----------+-----+------+
 |      |     |     3.3V |        |   |  1 || 2  |   |        | 5V       |     |      |
 |   47 |   0 |    SDA.5 |     IN | 1 |  3 || 4  |   |        | 5V       |     |      |
 |   46 |   1 |    SCL.5 |     IN | 1 |  5 || 6  |   |        | GND      |     |      |
 |   54 |   2 |    PWM15 |     IN | 1 |  7 || 8  | 0 | IN     | RXD.0    | 3   | 131  |
 |      |     |      GND |        |   |  9 || 10 | 0 | IN     | TXD.0    | 4   | 132  |
 |  138 |   5 |  CAN1_RX |     IN | 1 | 11 || 12 | 1 | IN     | CAN2_TX  | 6   | 29   |
 |  139 |   7 |  CAN1_TX |     IN | 1 | 13 || 14 |   |        | GND      |     |      |
 |   28 |   8 |  CAN2_RX |     IN | 1 | 15 || 16 | 1 | IN     | SDA.1    | 9   | 59   |
 |      |     |     3.3V |        |   | 17 || 18 | 1 | IN     | SCL.1    | 10  | 58   |
 |   49 |  11 | SPI4_TXD |     IN | 1 | 19 || 20 |   |        | GND      |     |      |
 |   48 |  12 | SPI4_RXD |     IN | 1 | 21 || 22 | 0 | OUT    | GPIO2_D4 | 13  | 92   |
 |   50 |  14 | SPI4_CLK |     IN | 1 | 23 || 24 | 1 | IN     | SPI4_CS1 | 15  | 52   |
 |      |     |      GND |        |   | 25 || 26 | 0 | OUT    | PWM1     | 16  | 35   |
 +------+-----+----------+--------+---+----++----+---+--------+----------+-----+------+
 | GPIO | wPi |   Name   |  Mode  | V | Physical | V |  Mode  | Name     | wPi | GPIO |
 +------+-----+----------+--------+---+   OPI5   +---+--------+----------+-----+------+
```

## Selected Pins

| Function | wiringOP Pin | Physical Pin | Notes                        |
| -------- | ------------ | ------------ | ---------------------------- |
| ENA      | 2            | 7            | Motor A enable (PWM15)       |
| ENB      | 16           | 26           | Motor B enable (PWM1)        |
| IN1      | 5            | 11           | Motor A direction (CAN1_RX)  |
| IN2      | 7            | 13           | Motor A direction (CAN1_TX)  |
| IN3      | 8            | 15           | Motor B direction (CAN2_RX)  |
| IN4      | 13           | 22           | Motor B direction (GPIO2_D4) |
| STOP BTN | 6            | 12           | Input with pull-up (CAN2_TX) |

**Note:** Pin mapping updated from `gpio readall` output on Orange Pi 5.
