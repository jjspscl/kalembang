"""
Kalembang FastAPI Application

Local LAN alarm controller for Orange Pi 5.
Controls clock motors via L298N motor driver.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import API_HOST, API_PORT, BUTTON_DEBOUNCE_TIME, STOP_BUTTON_ENABLED
from .gpio import get_controller, GPIOError
from .database import get_db, close_db, Alarm
from .patterns import (
    get_preset_patterns,
    get_preset_pattern,
    get_pattern_player,
    Pattern,
    PRESET_PATTERNS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class DutyRequest(BaseModel):
    """Request body for setting motor duty cycle."""
    duty: int = Field(..., ge=0, le=100, description="Duty cycle percentage (0-100)")

class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    clock1: dict[str, bool | int]
    clock2: dict[str, bool | int]
    stop_button_pressed: bool | None

class MessageResponse(BaseModel):
    """Generic response with a message."""
    message: str
    success: bool = True

class AlarmRequest(BaseModel):
    """Request body for creating/updating an alarm."""
    name: str = Field(..., min_length=1, max_length=100)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)
    clock_id: int = Field(default=1, ge=1, le=2)
    enabled: bool = True
    days: str = Field(default="daily")
    duration: int = Field(default=30, ge=0)
    mode: str = Field(default="clock1", pattern="^(clock1|clock2|pattern)$")
    pattern: Optional[str] = Field(default=None)

class AlarmResponse(BaseModel):
    """Response model for alarm endpoints."""
    id: int
    name: str
    hour: int
    minute: int
    second: int
    clock_id: int
    enabled: bool
    days: str
    duration: int
    mode: str
    pattern: Optional[str]
    created_at: Optional[str]
    last_triggered: Optional[str]

class TimeResponse(BaseModel):
    """Response model for time endpoint."""
    timestamp: str
    hour: int
    minute: int
    second: int
    day_of_week: str

async def stop_button_monitor():
    """
    Background task to monitor the STOP button.

    When pressed, immediately stops all motors.
    """
    controller = get_controller()
    button_was_pressed = False

    logger.info("STOP button monitor started")

    while True:
        try:
            button_pressed = controller.read_stop_button()

            if button_pressed and not button_was_pressed:
                logger.warning("STOP button pressed - stopping all motors!")
                controller.trigger_stop()

            button_was_pressed = button_pressed

            await asyncio.sleep(BUTTON_DEBOUNCE_TIME)

        except GPIOError as e:
            logger.error("GPIO error in stop button monitor: %s", e)
            await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            logger.info("STOP button monitor stopped")
            raise
        except (OSError, RuntimeError) as e:
            logger.exception("Unexpected error in stop button monitor: %s", e)
            await asyncio.sleep(1.0)

_alarm_off_tasks: dict[int, asyncio.Task[None]] = {}
_pattern_tasks: dict[int, asyncio.Task[None]] = {}

async def alarm_scheduler():
    """
    Background task to check and trigger alarms.

    Runs every second and checks if any enabled alarm matches the current time.
    Supports three modes: clock1, clock2, and pattern.
    """
    logger.info("Alarm scheduler started")

    while True:
        try:
            now = datetime.now()
            db = get_db()
            controller = get_controller()

            enabled_alarms = db.get_enabled_alarms()
            for alarm in enabled_alarms:
                if alarm.id is None:
                    continue
                alarm_id = alarm.id
                if alarm.matches_time(now):
                    logger.info("Triggering alarm: %s (mode=%s)", alarm.name, alarm.mode)

                    db.mark_triggered(alarm_id)

                    if alarm.days == "once":
                        db.disable_once_alarm(alarm_id)

                    if alarm.mode == "pattern" and alarm.pattern:
                        if alarm_id in _pattern_tasks:
                            _pattern_tasks[alarm_id].cancel()

                        async def play_pattern(aid: int, pattern_json: str) -> None:
                            try:
                                player = get_pattern_player(controller)
                                await player.play_json(pattern_json)
                            except Exception as e:
                                logger.error("Pattern playback error for alarm %d: %s", aid, e)
                            finally:
                                _pattern_tasks.pop(aid, None)

                        task = asyncio.create_task(play_pattern(alarm_id, alarm.pattern))
                        _pattern_tasks[alarm_id] = task

                    else:
                        clock_id = 1 if alarm.mode == "clock1" else 2

                        if clock_id == 1:
                            controller.clock1_on()
                        else:
                            controller.clock2_on()

                        if alarm.duration > 0:
                            if alarm_id in _alarm_off_tasks:
                                _alarm_off_tasks[alarm_id].cancel()

                            async def auto_off(cid: int, aid: int, dur: int) -> None:
                                await asyncio.sleep(dur)
                                ctrl = get_controller()
                                if cid == 1:
                                    ctrl.clock1_off()
                                else:
                                    ctrl.clock2_off()
                                logger.info("Alarm %d auto-off after %ds", aid, dur)
                                _alarm_off_tasks.pop(aid, None)

                            task = asyncio.create_task(auto_off(clock_id, alarm_id, alarm.duration))
                            _alarm_off_tasks[alarm_id] = task

            await asyncio.sleep(1.0 - (datetime.now().microsecond / 1_000_000))

        except asyncio.CancelledError:
            logger.info("Alarm scheduler stopped")
            raise
        except (OSError, RuntimeError, GPIOError) as e:
            logger.exception("Error in alarm scheduler: %s", e)
            await asyncio.sleep(1.0)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    logger.info("Kalembang starting up...")

    use_mock = os.environ.get("KALEMBANG_MOCK_GPIO", "").lower() in ("1", "true", "yes")

    tasks: list[asyncio.Task[None]] = []

    try:
        controller = get_controller(use_mock=use_mock)
        controller.initialize()

        get_db()

        if STOP_BUTTON_ENABLED:
            monitor_task = asyncio.create_task(stop_button_monitor())
            tasks.append(monitor_task)

        scheduler_task = asyncio.create_task(alarm_scheduler())
        tasks.append(scheduler_task)

        logger.info("Kalembang ready on %s:%d", API_HOST, API_PORT)

    except GPIOError as e:
        logger.error("GPIO initialization failed: %s", e)
        logger.info("Tip: Set KALEMBANG_MOCK_GPIO=1 to run without hardware")
        raise

    yield

    logger.info("Kalembang shutting down...")

    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    for task in _alarm_off_tasks.values():
        task.cancel()
    _alarm_off_tasks.clear()

    for task in _pattern_tasks.values():
        task.cancel()
    _pattern_tasks.clear()

    close_db()
    controller.cleanup()
    logger.info("Kalembang shutdown complete")

app = FastAPI(
    title="Kalembang",
    description="Local LAN alarm controller for Orange Pi 5",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # LAN-only, no auth for MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/status", response_model=StatusResponse)
async def get_status():
    """Get current status of all clocks and controls."""
    controller = get_controller()
    return controller.get_status()

@app.post("/api/v1/clock/1/on", response_model=MessageResponse)
async def clock1_on():
    """Turn on Clock 1."""
    controller = get_controller()
    controller.clock1_on()
    return MessageResponse(message="Clock 1 is ON")

@app.post("/api/v1/clock/1/off", response_model=MessageResponse)
async def clock1_off():
    """Turn off Clock 1."""
    controller = get_controller()
    controller.clock1_off()
    return MessageResponse(message="Clock 1 is OFF")

@app.post("/api/v1/clock/2/on", response_model=MessageResponse)
async def clock2_on():
    """Turn on Clock 2."""
    controller = get_controller()
    controller.clock2_on()
    return MessageResponse(message="Clock 2 is ON")

@app.post("/api/v1/clock/2/off", response_model=MessageResponse)
async def clock2_off():
    """Turn off Clock 2."""
    controller = get_controller()
    controller.clock2_off()
    return MessageResponse(message="Clock 2 is OFF")

@app.post("/api/v1/clock/all/off", response_model=MessageResponse)
async def all_off():
    """Turn off all clocks immediately."""
    controller = get_controller()
    controller.all_off()
    return MessageResponse(message="All clocks are OFF")

@app.post("/api/v1/clock/1/duty", response_model=MessageResponse)
async def set_clock1_duty(request: DutyRequest):
    """Set duty cycle (0-100) for Clock 1."""
    controller = get_controller()
    controller.set_clock1_duty(request.duty)
    return MessageResponse(message=f"Clock 1 duty set to {request.duty}%")

@app.post("/api/v1/clock/2/duty", response_model=MessageResponse)
async def set_clock2_duty(request: DutyRequest):
    """Set duty cycle (0-100) for Clock 2."""
    controller = get_controller()
    controller.set_clock2_duty(request.duty)
    return MessageResponse(message=f"Clock 2 duty set to {request.duty}%")

@app.post("/api/v1/stop/trigger", response_model=MessageResponse)
async def trigger_stop():
    """Manually trigger emergency stop (same as pressing STOP button)."""
    controller = get_controller()
    controller.trigger_stop()
    return MessageResponse(message="STOP triggered - all clocks OFF")

@app.get("/api/v1/time", response_model=TimeResponse)
async def get_time():
    """Get the current server time."""
    now = datetime.now()
    day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    return TimeResponse(
        timestamp=now.isoformat(),
        hour=now.hour,
        minute=now.minute,
        second=now.second,
        day_of_week=day_names[now.weekday()],
    )

def _alarm_to_response(alarm: Alarm) -> AlarmResponse:
    \"\"\"Convert Alarm dataclass to AlarmResponse.\"\"\"\n    if alarm.id is None:\n        raise ValueError(\"Alarm must have an id\")\n    return AlarmResponse(\n        id=alarm.id,\n        name=alarm.name,\n        hour=alarm.hour,\n        minute=alarm.minute,\n        second=alarm.second,\n        clock_id=alarm.clock_id,\n        enabled=alarm.enabled,\n        days=alarm.days,\n        duration=alarm.duration,\n        mode=alarm.mode,\n        pattern=alarm.pattern,\n        created_at=alarm.created_at,\n        last_triggered=alarm.last_triggered,\n    )

@app.get("/api/v1/alarms", response_model=list[AlarmResponse])
async def list_alarms():
    """Get all alarms."""
    db = get_db()
    alarms = db.get_all_alarms()
    return [_alarm_to_response(a) for a in alarms]

@app.post("/api/v1/alarms", response_model=AlarmResponse)
async def create_alarm(request: AlarmRequest):
    """Create a new alarm."""
    db = get_db()

    alarm = Alarm(
        id=None,
        name=request.name,
        hour=request.hour,
        minute=request.minute,
        second=request.second,
        clock_id=request.clock_id,
        enabled=request.enabled,
        days=request.days,
        duration=request.duration,
        mode=request.mode,
        pattern=request.pattern,
    )

    created = db.create_alarm(alarm)
    return _alarm_to_response(created)

@app.get("/api/v1/alarms/{alarm_id}", response_model=AlarmResponse)
async def get_alarm(alarm_id: int):
    """Get an alarm by ID."""
    db = get_db()
    alarm = db.get_alarm(alarm_id)

    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")

    return _alarm_to_response(alarm)

@app.put("/api/v1/alarms/{alarm_id}", response_model=AlarmResponse)
async def update_alarm(alarm_id: int, request: AlarmRequest):
    """Update an existing alarm."""
    db = get_db()

    existing = db.get_alarm(alarm_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Alarm not found")

    alarm = Alarm(
        id=alarm_id,
        name=request.name,
        hour=request.hour,
        minute=request.minute,
        second=request.second,
        clock_id=request.clock_id,
        enabled=request.enabled,
        days=request.days,
        duration=request.duration,
        mode=request.mode,
        pattern=request.pattern,
        created_at=existing.created_at,
        last_triggered=existing.last_triggered,
    )

    updated = db.update_alarm(alarm)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update alarm")
    return _alarm_to_response(updated)

@app.delete("/api/v1/alarms/{alarm_id}", response_model=MessageResponse)
async def delete_alarm(alarm_id: int):
    """Delete an alarm."""
    db = get_db()

    deleted = db.delete_alarm(alarm_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alarm not found")

    return MessageResponse(message=f"Alarm {alarm_id} deleted")

@app.patch("/api/v1/alarms/{alarm_id}/toggle", response_model=AlarmResponse)
async def toggle_alarm(alarm_id: int, enabled: bool):
    """Enable or disable an alarm."""
    db = get_db()

    alarm = db.toggle_alarm(alarm_id, enabled)
    if alarm is None:
        raise HTTPException(status_code=404, detail="Alarm not found")

    return _alarm_to_response(alarm)

class PatternEventModel(BaseModel):
    clock: int = Field(..., ge=1, le=2)
    time: float = Field(..., ge=0)
    duration: float = Field(..., gt=0)
    duty: int = Field(..., ge=0, le=100)

class PatternModel(BaseModel):
    name: str = Field(default="Custom Pattern")
    totalDuration: float = Field(..., gt=0)
    events: list[PatternEventModel]

class PatternResponse(BaseModel):
    id: str
    name: str
    description: str
    totalDuration: float
    events: list[dict]

class PatternTestRequest(BaseModel):
    pattern: PatternModel

@app.get("/api/v1/patterns/presets", response_model=list[PatternResponse])
async def list_preset_patterns():
    """Get all preset patterns."""
    presets = get_preset_patterns()
    return [
        PatternResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            totalDuration=p.total_duration,
            events=p.events,
        )
        for p in presets
    ]

@app.get("/api/v1/patterns/presets/{pattern_id}", response_model=PatternResponse)
async def get_preset(pattern_id: str):
    """Get a specific preset pattern by ID."""
    preset = get_preset_pattern(pattern_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return PatternResponse(
        id=preset.id,
        name=preset.name,
        description=preset.description,
        totalDuration=preset.total_duration,
        events=preset.events,
    )

@app.post("/api/v1/patterns/test", response_model=MessageResponse)
async def test_pattern(request: PatternTestRequest):
    """Test play a pattern immediately."""
    controller = get_controller()
    player = get_pattern_player(controller)

    pattern = Pattern(
        id="test",
        name=request.pattern.name,
        description="Test pattern",
        total_duration=request.pattern.totalDuration,
        events=[e.model_dump() for e in request.pattern.events],
    )

    asyncio.create_task(player.play(pattern))
    return MessageResponse(message=f"Pattern '{pattern.name}' started")

@app.post("/api/v1/patterns/stop", response_model=MessageResponse)
async def stop_pattern():
    """Stop any currently playing pattern."""
    controller = get_controller()
    player = get_pattern_player(controller)
    await player.stop()
    return MessageResponse(message="Pattern stopped")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

CLIENT_DIR = Path(__file__).parent.parent.parent / "client-dist"

if CLIENT_DIR.exists():
    app.mount("/assets", StaticFiles(directory=CLIENT_DIR / "assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_spa(_request: Request, path: str):
        """Serve the SPA for all non-API routes."""
        file_path = CLIENT_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(CLIENT_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
