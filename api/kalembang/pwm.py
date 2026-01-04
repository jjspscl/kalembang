"""
Kalembang Software PWM

Provides software-based PWM control for motor "volume" adjustment.
This is optional for MVP - can be implemented later.

Note: Software PWM has limitations:
- Not as precise as hardware PWM
- Can have timing jitter under load
- Recommended frequency: 200-1000 Hz
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SoftwarePWM:
    """
    Software PWM controller for a single GPIO pin.
    
    Uses asyncio for non-blocking operation.
    """

    def __init__(
        self,
        pin: int,
        write_func: callable,
        frequency: int = 500,
    ):
        """
        Initialize software PWM.
        
        Args:
            pin: GPIO pin number
            write_func: Function to write to GPIO (write_func(pin, value))
            frequency: PWM frequency in Hz
        """
        self.pin = pin
        self.write = write_func
        self.frequency = frequency
        self.duty = 0  # 0-100
        self._running = False
        self._task: Optional[asyncio.Task] = None

    @property
    def period(self) -> float:
        """PWM period in seconds."""
        return 1.0 / self.frequency

    async def _pwm_loop(self) -> None:
        """Main PWM loop - toggles pin based on duty cycle."""
        period = self.period
        
        while self._running:
            if self.duty <= 0:
                self.write(self.pin, 0)
                await asyncio.sleep(period)
            elif self.duty >= 100:
                self.write(self.pin, 1)
                await asyncio.sleep(period)
            else:
                on_time = period * (self.duty / 100.0)
                off_time = period - on_time
                
                self.write(self.pin, 1)
                await asyncio.sleep(on_time)
                
                if self._running:  # Check again after sleep
                    self.write(self.pin, 0)
                    await asyncio.sleep(off_time)

    def start(self) -> None:
        """Start the PWM loop."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._pwm_loop())
        logger.debug(f"PWM started on pin {self.pin} at {self.frequency}Hz")

    def stop(self) -> None:
        """Stop the PWM loop and set pin LOW."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        self.write(self.pin, 0)
        logger.debug(f"PWM stopped on pin {self.pin}")

    def set_duty(self, duty: int) -> None:
        """
        Set duty cycle (0-100).
        
        Args:
            duty: Duty cycle percentage (0=off, 100=full on)
        """
        self.duty = max(0, min(100, duty))
        logger.debug(f"PWM pin {self.pin} duty set to {self.duty}%")

    def set_frequency(self, frequency: int) -> None:
        """
        Set PWM frequency.
        
        Args:
            frequency: Frequency in Hz (recommended: 200-1000)
        """
        self.frequency = max(1, min(10000, frequency))
        logger.debug(f"PWM pin {self.pin} frequency set to {self.frequency}Hz")

class PWMManager:
    """
    Manages multiple software PWM channels.
    
    Usage:
        manager = PWMManager(write_func)
        manager.add_channel("clock1", pin=4)
        manager.add_channel("clock2", pin=5)
        manager.start_all()
        manager.set_duty("clock1", 50)
    """

    def __init__(self, write_func: callable, default_frequency: int = 500):
        """
        Initialize PWM manager.
        
        Args:
            write_func: Function to write to GPIO (write_func(pin, value))
            default_frequency: Default PWM frequency for new channels
        """
        self.write_func = write_func
        self.default_frequency = default_frequency
        self._channels: dict[str, SoftwarePWM] = {}

    def add_channel(
        self,
        name: str,
        pin: int,
        frequency: Optional[int] = None,
    ) -> None:
        """
        Add a PWM channel.
        
        Args:
            name: Channel identifier (e.g., "clock1")
            pin: GPIO pin number
            frequency: PWM frequency (uses default if None)
        """
        freq = frequency or self.default_frequency
        self._channels[name] = SoftwarePWM(pin, self.write_func, freq)
        logger.info(f"PWM channel '{name}' added on pin {pin}")

    def start_all(self) -> None:
        """Start PWM on all channels."""
        for channel in self._channels.values():
            channel.start()

    def stop_all(self) -> None:
        """Stop PWM on all channels."""
        for channel in self._channels.values():
            channel.stop()

    def set_duty(self, name: str, duty: int) -> None:
        """
        Set duty cycle for a channel.
        
        Args:
            name: Channel identifier
            duty: Duty cycle percentage (0-100)
        """
        if name in self._channels:
            self._channels[name].set_duty(duty)
        else:
            logger.warning(f"Unknown PWM channel: {name}")

    def get_duty(self, name: str) -> Optional[int]:
        """Get current duty cycle for a channel."""
        if name in self._channels:
            return self._channels[name].duty
        return None
