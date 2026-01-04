"""
Kalembang GPIO Configuration

Pin numbers use wiringOP numbering scheme.
Run `gpio readall` on your Orange Pi 5 to verify the mapping.

IMPORTANT: Update these values based on your actual wiring and
the output of `gpio readall` on your specific OP5 image.
"""

ENA_PIN = 4   # Physical pin 16 (PWM-capable, verify with gpio readall)
IN1_PIN = 0   # Physical pin 11
IN2_PIN = 2   # Physical pin 13

ENB_PIN = 5   # Physical pin 18 (PWM-capable, verify with gpio readall)
IN3_PIN = 3   # Physical pin 15
IN4_PIN = 6   # Physical pin 22

STOP_BTN_PIN = 1  # Physical pin 12 (verify with gpio readall)

MOTOR_A_DIRECTION = (1, 0)  # (IN1, IN2)
MOTOR_B_DIRECTION = (1, 0)  # (IN3, IN4)

STOP_LATCH = True

DEFAULT_DUTY = 100

PWM_FREQUENCY = 500

BUTTON_DEBOUNCE_TIME = 0.05

API_HOST = "0.0.0.0"
API_PORT = 8088

DATABASE_PATH = "data/kalembang.db"

GPIO_BACKEND = "wiringop"
