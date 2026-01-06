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

from .config import API_HOST, API_PORT, STOP_LATCH, BUTTON_DEBOUNCE_TIME
from .gpio import get_controller, GPIOError
from .database import get_db, close_db, Alarm

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
    clock1: dict
    clock2: dict
    stop_latched: bool
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
    
    When pressed, immediately stops all motors and sets the latch.
    """
    controller = get_controller()
    button_was_pressed = False
    
    logger.info("STOP button monitor started")
    
    while True:
        try:
            button_pressed = controller.read_stop_button()
            
            if button_pressed and not button_was_pressed:
                logger.warning("STOP button pressed!")
                controller.trigger_stop()
            
            button_was_pressed = button_pressed
            
            await asyncio.sleep(BUTTON_DEBOUNCE_TIME)
            
        except GPIOError as e:
            logger.error(f"GPIO error in stop button monitor: {e}")
            await asyncio.sleep(1.0)  # Back off on error
        except asyncio.CancelledError:
            logger.info("STOP button monitor stopped")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in stop button monitor: {e}")
            await asyncio.sleep(1.0)

_alarm_off_tasks: dict[int, asyncio.Task] = {}

async def alarm_scheduler():
    """
    Background task to check and trigger alarms.
    
    Runs every second and checks if any enabled alarm matches the current time.
    """
    logger.info("Alarm scheduler started")
    
    while True:
        try:
            now = datetime.now()
            db = get_db()
            controller = get_controller()
            
            if controller._stop_latched:
                await asyncio.sleep(1.0)
                continue
            
            enabled_alarms = db.get_enabled_alarms()
            for alarm in enabled_alarms:
                if alarm.matches_time(now):
                    logger.info(f"Triggering alarm: {alarm.name} (clock {alarm.clock_id})")
                    
                    if alarm.clock_id == 1:
                        controller.clock1_on()
                    else:
                        controller.clock2_on()
                    
                    db.mark_triggered(alarm.id)
                    
                    if alarm.days == "once":
                        db.disable_once_alarm(alarm.id)
                    
                    if alarm.duration > 0:
                        if alarm.id in _alarm_off_tasks:
                            _alarm_off_tasks[alarm.id].cancel()
                        
                        async def auto_off(clock_id: int, alarm_id: int, duration: int):
                            await asyncio.sleep(duration)
                            ctrl = get_controller()
                            if clock_id == 1:
                                ctrl.clock1_off()
                            else:
                                ctrl.clock2_off()
                            logger.info(f"Alarm {alarm_id} auto-off after {duration}s")
                            _alarm_off_tasks.pop(alarm_id, None)
                        
                        task = asyncio.create_task(auto_off(alarm.clock_id, alarm.id, alarm.duration))
                        _alarm_off_tasks[alarm.id] = task
            
            await asyncio.sleep(1.0 - (datetime.now().microsecond / 1_000_000))
            
        except asyncio.CancelledError:
            logger.info("Alarm scheduler stopped")
            raise
        except Exception as e:
            logger.exception(f"Error in alarm scheduler: {e}")
            await asyncio.sleep(1.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Initializes GPIO and database on startup and cleans up on shutdown.
    """
    logger.info("Kalembang starting up...")
    
    use_mock = os.environ.get("KALEMBANG_MOCK_GPIO", "").lower() in ("1", "true", "yes")
    
    try:
        controller = get_controller(use_mock=use_mock)
        controller.initialize()
        
        db = get_db()
        
        tasks = []
        
        if STOP_LATCH:
            monitor_task = asyncio.create_task(stop_button_monitor())
            tasks.append(monitor_task)
        
        scheduler_task = asyncio.create_task(alarm_scheduler())
        tasks.append(scheduler_task)
        
        logger.info(f"Kalembang ready on {API_HOST}:{API_PORT}")
        
    except GPIOError as e:
        logger.error(f"GPIO initialization failed: {e}")
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
    
    if controller._stop_latched:
        raise HTTPException(
            status_code=409,
            detail="STOP is latched. Clear the latch first with POST /api/v1/stop/clear",
        )
    
    success = controller.clock1_on()
    if not success:
        raise HTTPException(status_code=409, detail="Clock 1 could not be turned on")
    
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
    
    if controller._stop_latched:
        raise HTTPException(
            status_code=409,
            detail="STOP is latched. Clear the latch first with POST /api/v1/stop/clear",
        )
    
    success = controller.clock2_on()
    if not success:
        raise HTTPException(status_code=409, detail="Clock 2 could not be turned on")
    
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
    
    if controller._stop_latched and request.duty > 0:
        raise HTTPException(
            status_code=409,
            detail="STOP is latched. Clear the latch first with POST /api/v1/stop/clear",
        )
    
    success = controller.set_clock1_duty(request.duty)
    if not success:
        raise HTTPException(status_code=409, detail="Could not set Clock 1 duty")
    
    return MessageResponse(message=f"Clock 1 duty set to {request.duty}%")

@app.post("/api/v1/clock/2/duty", response_model=MessageResponse)
async def set_clock2_duty(request: DutyRequest):
    """Set duty cycle (0-100) for Clock 2."""
    controller = get_controller()
    
    if controller._stop_latched and request.duty > 0:
        raise HTTPException(
            status_code=409,
            detail="STOP is latched. Clear the latch first with POST /api/v1/stop/clear",
        )
    
    success = controller.set_clock2_duty(request.duty)
    if not success:
        raise HTTPException(status_code=409, detail="Could not set Clock 2 duty")
    
    return MessageResponse(message=f"Clock 2 duty set to {request.duty}%")

@app.post("/api/v1/stop/trigger", response_model=MessageResponse)
async def trigger_stop():
    """Manually trigger emergency stop (same as pressing STOP button)."""
    controller = get_controller()
    controller.trigger_stop()
    return MessageResponse(message="STOP triggered - all clocks OFF, latch active")

@app.post("/api/v1/stop/clear", response_model=MessageResponse)
async def clear_stop():
    """Clear the STOP latch, allowing clocks to be turned on again."""
    controller = get_controller()
    controller.clear_stop_latch()
    return MessageResponse(message="STOP latch cleared")

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
    """Convert Alarm dataclass to AlarmResponse."""
    return AlarmResponse(
        id=alarm.id,
        name=alarm.name,
        hour=alarm.hour,
        minute=alarm.minute,
        second=alarm.second,
        clock_id=alarm.clock_id,
        enabled=alarm.enabled,
        days=alarm.days,
        duration=alarm.duration,
        created_at=alarm.created_at,
        last_triggered=alarm.last_triggered,
    )

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
        created_at=existing.created_at,
        last_triggered=existing.last_triggered,
    )
    
    updated = db.update_alarm(alarm)
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
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    return _alarm_to_response(alarm)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

CLIENT_DIR = Path(__file__).parent.parent.parent / "client-dist"

if CLIENT_DIR.exists():
    app.mount("/assets", StaticFiles(directory=CLIENT_DIR / "assets"), name="assets")
    
    @app.get("/{path:path}")
    async def serve_spa(request: Request, path: str):
        file_path = CLIENT_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(CLIENT_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
