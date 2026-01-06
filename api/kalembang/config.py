"""
Kalembang GPIO Configuration

Pin numbers use wiringOP numbering scheme.
Run `gpio readall` on your Orange Pi 5 to verify the mapping.

IMPORTANT: Update these values based on your actual wiring and
the output of `gpio readall` on your specific OP5 image.
"""

ENA_PIN = 2   # Physical pin 7 (PWM15)
IN1_PIN = 5   # Physical pin 11 (CAN1_RX)
IN2_PIN = 7   # Physical pin 13 (CAN1_TX)

ENB_PIN = 16  # Physical pin 26 (PWM1)
IN3_PIN = 8   # Physical pin 15 (CAN2_RX)
IN4_PIN = 13  # Physical pin 22 (GPIO2_D4)

STOP_BTN_PIN = 6  # Physical pin 12 (CAN2_TX)

MOTOR_A_DIRECTION = (1, 0)  # (IN1, IN2)
MOTOR_B_DIRECTION = (1, 0)  # (IN3, IN4)

STOP_BUTTON_ENABLED = True

DEFAULT_DUTY = 100

PWM_FREQUENCY = 500

BUTTON_DEBOUNCE_TIME = 0.05

API_HOST = "0.0.0.0"
API_PORT = 8088

DATABASE_PATH = "data/kalembang.db"

GPIO_BACKEND = "wiringop"
