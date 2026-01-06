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
from typing import Optional, Callable

logger = logging.getLogger(__name__)

WriteFunc = Callable[[int, int], None]


class SoftwarePWM:

    def __init__(
        self,
        pin: int,
        write_func: WriteFunc,
        frequency: int = 500,
    ):
        self.pin = pin
        self.write: WriteFunc = write_func
        self.frequency = frequency
        self.duty = 0
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None

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

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._pwm_loop())
        logger.debug("PWM started on pin %d at %dHz", self.pin, self.frequency)

    def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        self.write(self.pin, 0)
        logger.debug("PWM stopped on pin %d", self.pin)

    def set_duty(self, duty: int) -> None:
        self.duty = max(0, min(100, duty))
        logger.debug("PWM pin %d duty set to %d%%", self.pin, self.duty)

    def set_frequency(self, frequency: int) -> None:
        self.frequency = max(1, min(10000, frequency))
        logger.debug("PWM pin %d frequency set to %dHz", self.pin, self.frequency)

class PWMManager:

    def __init__(self, write_func: WriteFunc, default_frequency: int = 500):
        self.write_func: WriteFunc = write_func
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
        logger.info("PWM channel '%s' added on pin %d", name, pin)

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
            logger.warning("Unknown PWM channel: %s", name)

    def get_duty(self, name: str) -> Optional[int]:
        """Get current duty cycle for a channel."""
        if name in self._channels:
            return self._channels[name].duty
        return None
