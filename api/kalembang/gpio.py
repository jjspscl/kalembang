"""
Kalembang GPIO Control

Controls L298N motor driver via wiringOP CLI commands.
Supports two clock motors with enable (ENA/ENB) and direction (IN1-IN4) pins.
"""

import subprocess
import logging
from typing import Optional, Any

from .config import (
    ENA_PIN, ENB_PIN,
    IN1_PIN, IN2_PIN, IN3_PIN, IN4_PIN,
    STOP_BTN_PIN,
    MOTOR_A_DIRECTION, MOTOR_B_DIRECTION,
    GPIO_BACKEND,
    PWM_FREQUENCY,
)
from .pwm import SoftwarePWM

logger = logging.getLogger(__name__)

class GPIOError(Exception):
    """Raised when GPIO operations fail."""

class WiringOPBackend:
    """GPIO backend using wiringOP CLI commands."""

    @staticmethod
    def _run_gpio_cmd(args: list[str]) -> str:
        cmd = ["gpio"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode != 0:
                raise GPIOError(f"gpio command failed: {result.stderr}")
            return result.stdout
        except FileNotFoundError as exc:
            raise GPIOError("wiringOP 'gpio' command not found. Install wiringOP first.") from exc
        except subprocess.TimeoutExpired as exc:
            raise GPIOError("gpio command timed out") from exc

    def setup_pin_output(self, pin: int) -> None:
        self._run_gpio_cmd(["mode", str(pin), "out"])
        logger.debug("Pin %d configured as output", pin)

    def setup_pin_input_pullup(self, pin: int) -> None:
        self._run_gpio_cmd(["mode", str(pin), "in"])
        self._run_gpio_cmd(["mode", str(pin), "up"])
        logger.debug("Pin %d configured as input with pull-up", pin)

    def write(self, pin: int, value: int) -> None:
        """Write a digital value (0 or 1) to a pin."""
        self._run_gpio_cmd(["write", str(pin), str(value)])

    def read(self, pin: int) -> int:
        """Read a digital value from a pin."""
        output = self._run_gpio_cmd(["read", str(pin)])
        return int(output.strip())

class MockBackend:
    """Mock GPIO backend for development/testing without hardware."""

    def __init__(self):
        self._pins: dict[int, int] = {}
        self._modes: dict[int, str] = {}
        logger.warning("Using MOCK GPIO backend - no actual hardware control!")

    def setup_pin_output(self, pin: int) -> None:
        self._modes[pin] = "out"
        self._pins[pin] = 0
        logger.debug("[MOCK] Pin %d configured as output", pin)

    def setup_pin_input_pullup(self, pin: int) -> None:
        self._modes[pin] = "in"
        self._pins[pin] = 1  # Pull-up means HIGH when not pressed
        logger.debug("[MOCK] Pin %d configured as input with pull-up", pin)

    def write(self, pin: int, value: int) -> None:
        self._pins[pin] = value
        logger.debug("[MOCK] Pin %d = %d", pin, value)

    def read(self, pin: int) -> int:
        return self._pins.get(pin, 1)

class MotorController:
    """
    Controls two clock motors via L298N motor driver.
    
    Motor A (Clock 1): ENA, IN1, IN2
    Motor B (Clock 2): ENB, IN3, IN4
    """

    def __init__(self, use_mock: bool = False):
        """
        Initialize motor controller.
        
        Args:
            use_mock: If True, use mock backend (for dev without hardware)
        """
        if use_mock:
            self._backend = MockBackend()
        elif GPIO_BACKEND == "wiringop":
            self._backend = WiringOPBackend()
        else:
            raise GPIOError(f"Unknown GPIO backend: {GPIO_BACKEND}")

        self._clock1_enabled = False
        self._clock2_enabled = False
        self._clock1_duty = 100
        self._clock2_duty = 100

        self._pwm1: Optional[SoftwarePWM] = None
        self._pwm2: Optional[SoftwarePWM] = None

        self._initialized = False

    def initialize(self) -> None:
        """
        Initialize all GPIO pins.
        
        MUST be called before any motor operations.
        Sets all motors to OFF state.
        """
        if self._initialized:
            return

        logger.info("Initializing GPIO pins...")

        self._backend.setup_pin_output(ENA_PIN)
        self._backend.setup_pin_output(ENB_PIN)

        self._backend.setup_pin_output(IN1_PIN)
        self._backend.setup_pin_output(IN2_PIN)
        self._backend.setup_pin_output(IN3_PIN)
        self._backend.setup_pin_output(IN4_PIN)

        self._backend.setup_pin_input_pullup(STOP_BTN_PIN)

        self.all_off()

        in1, in2 = MOTOR_A_DIRECTION
        in3, in4 = MOTOR_B_DIRECTION
        self._backend.write(IN1_PIN, in1)
        self._backend.write(IN2_PIN, in2)
        self._backend.write(IN3_PIN, in3)
        self._backend.write(IN4_PIN, in4)

        self._pwm1 = SoftwarePWM(ENA_PIN, self._backend.write, PWM_FREQUENCY)
        self._pwm2 = SoftwarePWM(ENB_PIN, self._backend.write, PWM_FREQUENCY)

        self._initialized = True
        logger.info("GPIO initialization complete - all motors OFF")

    def _ensure_initialized(self) -> None:
        """Ensure GPIO is initialized before operations."""
        if not self._initialized:
            raise GPIOError("MotorController not initialized. Call initialize() first.")

    def clock1_on(self) -> None:
        self._ensure_initialized()
        if self._pwm1 is None:
            raise GPIOError("PWM not initialized")
        if self._clock1_duty < 100:
            self._pwm1.set_duty(self._clock1_duty)
            self._pwm1.start()
        else:
            self._pwm1.stop()
            self._backend.write(ENA_PIN, 1)
        self._clock1_enabled = True
        logger.info("Clock 1 ON (duty: %d%%)", self._clock1_duty)

    def clock1_off(self) -> None:
        self._ensure_initialized()
        if self._pwm1 is None:
            raise GPIOError("PWM not initialized")
        self._pwm1.stop()
        self._backend.write(ENA_PIN, 0)
        self._clock1_enabled = False
        logger.info("Clock 1 OFF")

    def clock2_on(self) -> None:
        self._ensure_initialized()
        if self._pwm2 is None:
            raise GPIOError("PWM not initialized")
        if self._clock2_duty < 100:
            self._pwm2.set_duty(self._clock2_duty)
            self._pwm2.start()
        else:
            self._pwm2.stop()
            self._backend.write(ENB_PIN, 1)
        self._clock2_enabled = True
        logger.info("Clock 2 ON (duty: %d%%)", self._clock2_duty)

    def clock2_off(self) -> None:
        self._ensure_initialized()
        if self._pwm2 is None:
            raise GPIOError("PWM not initialized")
        self._pwm2.stop()
        self._backend.write(ENB_PIN, 0)
        self._clock2_enabled = False
        logger.info("Clock 2 OFF")

    def all_off(self) -> None:
        if self._pwm1:
            self._pwm1.stop()
        if self._pwm2:
            self._pwm2.stop()
        self._backend.write(ENA_PIN, 0)
        self._backend.write(ENB_PIN, 0)
        self._clock1_enabled = False
        self._clock2_enabled = False
        logger.info("All clocks OFF")

    def set_clock1_duty(self, duty: int) -> None:
        """Set duty cycle for Clock 1 (0-100)."""
        self._ensure_initialized()
        if self._pwm1 is None:
            raise GPIOError("PWM not initialized")
        self._clock1_duty = max(0, min(100, duty))

        if self._clock1_enabled:
            if self._clock1_duty == 0:
                self.clock1_off()
            elif self._clock1_duty == 100:
                self._pwm1.stop()
                self._backend.write(ENA_PIN, 1)
            else:
                self._pwm1.set_duty(self._clock1_duty)
                if not self._pwm1.is_running:
                    self._pwm1.start()

        logger.info("Clock 1 duty set to %d%%", self._clock1_duty)

    def set_clock2_duty(self, duty: int) -> None:
        """Set duty cycle for Clock 2 (0-100)."""
        self._ensure_initialized()
        if self._pwm2 is None:
            raise GPIOError("PWM not initialized")
        self._clock2_duty = max(0, min(100, duty))

        if self._clock2_enabled:
            if self._clock2_duty == 0:
                self.clock2_off()
            elif self._clock2_duty == 100:
                self._pwm2.stop()
                self._backend.write(ENB_PIN, 1)
            else:
                self._pwm2.set_duty(self._clock2_duty)
                if not self._pwm2.is_running:
                    self._pwm2.start()

        logger.info("Clock 2 duty set to %d%%", self._clock2_duty)

    def read_stop_button(self) -> bool:
        """
        Read the STOP button state.
        
        Returns:
            True if button is pressed (active LOW)
        """
        self._ensure_initialized()
        return self._backend.read(STOP_BTN_PIN) == 0

    def trigger_stop(self) -> None:
        """Trigger emergency stop - turns off all motors."""
        self.all_off()
        logger.warning("STOP triggered - all motors OFF")

    def get_status(self) -> dict[str, Any]:
        return {
            "clock1": {
                "enabled": self._clock1_enabled,
                "duty": self._clock1_duty,
            },
            "clock2": {
                "enabled": self._clock2_enabled,
                "duty": self._clock2_duty,
            },
            "stop_button_pressed": self.read_stop_button() if self._initialized else None,
        }

    def cleanup(self) -> None:
        if self._initialized:
            if self._pwm1:
                self._pwm1.stop()
            if self._pwm2:
                self._pwm2.stop()
            self.all_off()
            logger.info("GPIO cleanup complete")


class _ControllerHolder:
    instance: Optional[MotorController] = None


def get_controller(use_mock: bool = False) -> MotorController:
    if _ControllerHolder.instance is None:
        _ControllerHolder.instance = MotorController(use_mock=use_mock)
    return _ControllerHolder.instance
