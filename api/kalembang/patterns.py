"""
Kalembang Pattern System

Defines pattern structures, preset patterns, and the pattern player
for executing complex alarm sequences on both clocks.
"""

import asyncio
import json
import logging
from typing import TypedDict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PatternEvent(TypedDict):
    clock: int
    time: float
    duration: float
    duty: int


@dataclass
class Pattern:
    id: str
    name: str
    description: str
    total_duration: float
    events: list[PatternEvent]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "totalDuration": self.total_duration,
            "events": self.events,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pattern":
        return cls(
            id=data.get("id", "custom"),
            name=data.get("name", "Custom Pattern"),
            description=data.get("description", ""),
            total_duration=data.get("totalDuration", 30),
            events=data.get("events", []),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Pattern":
        return cls.from_dict(json.loads(json_str))


PRESET_PATTERNS: dict[str, Pattern] = {
    "gentle": Pattern(
        id="gentle",
        name="Gentle Wake",
        description="Gradual intensity increase, alternating clocks",
        total_duration=30,
        events=[
            {"clock": 1, "time": 0, "duration": 0.3, "duty": 20},
            {"clock": 2, "time": 1, "duration": 0.3, "duty": 20},
            {"clock": 1, "time": 2, "duration": 0.5, "duty": 30},
            {"clock": 2, "time": 3, "duration": 0.5, "duty": 30},
            {"clock": 1, "time": 5, "duration": 1.0, "duty": 50},
            {"clock": 2, "time": 6.5, "duration": 1.0, "duty": 50},
            {"clock": 1, "time": 8, "duration": 1.5, "duty": 70},
            {"clock": 2, "time": 10, "duration": 1.5, "duty": 70},
            {"clock": 1, "time": 12, "duration": 18, "duty": 100},
            {"clock": 2, "time": 12, "duration": 18, "duty": 100},
        ],
    ),
    "urgent": Pattern(
        id="urgent",
        name="Urgent",
        description="Rapid alternating pulses at full intensity",
        total_duration=30,
        events=[
            {"clock": 1, "time": 0, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 0.3, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 0.6, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 0.9, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 1.2, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 1.5, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 1.8, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 2.1, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 2.4, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 2.7, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 3.0, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 3.3, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 3.6, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 3.9, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 4.2, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 4.5, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 5, "duration": 25, "duty": 100},
            {"clock": 2, "time": 5, "duration": 25, "duty": 100},
        ],
    ),
    "alternating": Pattern(
        id="alternating",
        name="Alternating",
        description="Clock 1 and Clock 2 take turns",
        total_duration=30,
        events=[
            {"clock": 1, "time": 0, "duration": 1.5, "duty": 100},
            {"clock": 2, "time": 2, "duration": 1.5, "duty": 100},
            {"clock": 1, "time": 4, "duration": 1.5, "duty": 100},
            {"clock": 2, "time": 6, "duration": 1.5, "duty": 100},
            {"clock": 1, "time": 8, "duration": 1.5, "duty": 100},
            {"clock": 2, "time": 10, "duration": 1.5, "duty": 100},
            {"clock": 1, "time": 12, "duration": 1.5, "duty": 100},
            {"clock": 2, "time": 14, "duration": 1.5, "duty": 100},
            {"clock": 1, "time": 16, "duration": 1.5, "duty": 100},
            {"clock": 2, "time": 18, "duration": 1.5, "duty": 100},
            {"clock": 1, "time": 20, "duration": 10, "duty": 100},
            {"clock": 2, "time": 20, "duration": 10, "duty": 100},
        ],
    ),
    "heartbeat": Pattern(
        id="heartbeat",
        name="Heartbeat",
        description="Mimics heartbeat rhythm (thump-thump, pause)",
        total_duration=30,
        events=[
            {"clock": 1, "time": 0, "duration": 0.15, "duty": 100},
            {"clock": 1, "time": 0.25, "duration": 0.1, "duty": 70},
            {"clock": 1, "time": 1.0, "duration": 0.15, "duty": 100},
            {"clock": 1, "time": 1.25, "duration": 0.1, "duty": 70},
            {"clock": 1, "time": 2.0, "duration": 0.15, "duty": 100},
            {"clock": 1, "time": 2.25, "duration": 0.1, "duty": 70},
            {"clock": 1, "time": 3.0, "duration": 0.15, "duty": 100},
            {"clock": 1, "time": 3.25, "duration": 0.1, "duty": 70},
            {"clock": 1, "time": 4.0, "duration": 0.15, "duty": 100},
            {"clock": 1, "time": 4.25, "duration": 0.1, "duty": 70},
            {"clock": 1, "time": 5.0, "duration": 0.15, "duty": 100},
            {"clock": 1, "time": 5.25, "duration": 0.1, "duty": 70},
            {"clock": 2, "time": 6.0, "duration": 0.15, "duty": 100},
            {"clock": 2, "time": 6.25, "duration": 0.1, "duty": 70},
            {"clock": 2, "time": 7.0, "duration": 0.15, "duty": 100},
            {"clock": 2, "time": 7.25, "duration": 0.1, "duty": 70},
            {"clock": 2, "time": 8.0, "duration": 0.15, "duty": 100},
            {"clock": 2, "time": 8.25, "duration": 0.1, "duty": 70},
            {"clock": 1, "time": 10, "duration": 20, "duty": 100},
            {"clock": 2, "time": 10, "duration": 20, "duty": 100},
        ],
    ),
    "crescendo": Pattern(
        id="crescendo",
        name="Crescendo",
        description="Both clocks increase intensity together",
        total_duration=30,
        events=[
            {"clock": 1, "time": 0, "duration": 5, "duty": 20},
            {"clock": 2, "time": 0, "duration": 5, "duty": 20},
            {"clock": 1, "time": 5, "duration": 5, "duty": 40},
            {"clock": 2, "time": 5, "duration": 5, "duty": 40},
            {"clock": 1, "time": 10, "duration": 5, "duty": 60},
            {"clock": 2, "time": 10, "duration": 5, "duty": 60},
            {"clock": 1, "time": 15, "duration": 5, "duty": 80},
            {"clock": 2, "time": 15, "duration": 5, "duty": 80},
            {"clock": 1, "time": 20, "duration": 10, "duty": 100},
            {"clock": 2, "time": 20, "duration": 10, "duty": 100},
        ],
    ),
    "sos": Pattern(
        id="sos",
        name="SOS",
        description="Morse code SOS pattern (· · · — — — · · ·)",
        total_duration=30,
        events=[
            {"clock": 1, "time": 0, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 0.4, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 0.8, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 1.5, "duration": 0.6, "duty": 100},
            {"clock": 2, "time": 2.3, "duration": 0.6, "duty": 100},
            {"clock": 2, "time": 3.1, "duration": 0.6, "duty": 100},
            {"clock": 1, "time": 4.2, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 4.6, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 5.0, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 6.5, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 6.9, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 7.3, "duration": 0.2, "duty": 100},
            {"clock": 2, "time": 8.0, "duration": 0.6, "duty": 100},
            {"clock": 2, "time": 8.8, "duration": 0.6, "duty": 100},
            {"clock": 2, "time": 9.6, "duration": 0.6, "duty": 100},
            {"clock": 1, "time": 10.7, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 11.1, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 11.5, "duration": 0.2, "duty": 100},
            {"clock": 1, "time": 13, "duration": 17, "duty": 100},
            {"clock": 2, "time": 13, "duration": 17, "duty": 100},
        ],
    ),
}


def get_preset_patterns() -> list[Pattern]:
    return list(PRESET_PATTERNS.values())


def get_preset_pattern(pattern_id: str) -> Optional[Pattern]:
    return PRESET_PATTERNS.get(pattern_id)


class PatternPlayer:
    def __init__(self, controller: Any):
        self._controller = controller
        self._running = False
        self._tasks: list[asyncio.Task[None]] = []
        self._play_task: Optional[asyncio.Task[None]] = None

    @property
    def is_running(self) -> bool:
        return self._running

    async def play(self, pattern: Pattern) -> None:
        if self._running:
            await self.stop()

        self._running = True
        logger.info(f"Starting pattern: {pattern.name} ({len(pattern.events)} events)")

        try:
            for event in pattern.events:
                if not self._running:
                    break
                task = asyncio.create_task(self._schedule_event(event))
                self._tasks.append(task)

            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
        except asyncio.CancelledError:
            logger.info("Pattern playback cancelled")
        finally:
            self._running = False
            self._tasks.clear()
            logger.info(f"Pattern finished: {pattern.name}")

    async def play_json(self, pattern_json: str) -> None:
        pattern = Pattern.from_json(pattern_json)
        await self.play(pattern)

    async def _schedule_event(self, event: PatternEvent) -> None:
        await asyncio.sleep(event["time"])

        if not self._running:
            return

        clock_id = event["clock"]
        duty = event["duty"]
        duration = event["duration"]

        logger.debug(f"Event: clock={clock_id}, duty={duty}%, duration={duration}s")

        try:
            if clock_id == 1:
                self._controller.set_clock1_duty(duty)
                self._controller.clock1_on()
                await asyncio.sleep(duration)
                if self._running:
                    self._controller.clock1_off()
            else:
                self._controller.set_clock2_duty(duty)
                self._controller.clock2_on()
                await asyncio.sleep(duration)
                if self._running:
                    self._controller.clock2_off()
        except Exception as e:
            logger.error(f"Error executing pattern event: {e}")

    async def stop(self) -> None:
        logger.info("Stopping pattern playback")
        self._running = False

        for task in self._tasks:
            if not task.done():
                task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks.clear()
        self._controller.all_off()


_player: Optional[PatternPlayer] = None


def get_pattern_player(controller: Any) -> PatternPlayer:
    global _player
    if _player is None:
        _player = PatternPlayer(controller)
    return _player
