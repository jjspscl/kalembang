"""
Kalembang Database Layer (sqlite3)

Handles alarm persistence with sqlite3 (compatible with libsql).
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

from .config import DATABASE_PATH

logger = logging.getLogger(__name__)

@dataclass
class Alarm:
    """Alarm data model."""
    id: Optional[int]
    name: str
    hour: int  # 0-23
    minute: int  # 0-59
    second: int  # 0-59 (default 0)
    clock_id: int  # 1 or 2 (which clock to trigger)
    enabled: bool
    days: str  # Comma-separated days: "mon,tue,wed,thu,fri,sat,sun" or "daily" or "once"
    duration: int  # How long to ring in seconds (0 = until manually stopped)
    created_at: Optional[str] = None
    last_triggered: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def matches_time(self, now: datetime) -> bool:
        """Check if this alarm should trigger at the given time."""
        if not self.enabled:
            return False
        
        if now.hour != self.hour or now.minute != self.minute or now.second != self.second:
            return False
        
        day_map = {
            0: "mon", 1: "tue", 2: "wed", 3: "thu",
            4: "fri", 5: "sat", 6: "sun"
        }
        current_day = day_map[now.weekday()]
        
        if self.days == "daily":
            return True
        elif self.days == "once":
            return True  # Will be disabled after triggering
        else:
            allowed_days = [d.strip().lower() for d in self.days.split(",")]
            return current_day in allowed_days

class Database:
    """Database manager for alarms."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Connect to the database and initialize schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_schema()
        logger.info(f"Database connected: {self.db_path}")

    def _init_schema(self) -> None:
        """Initialize database schema."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hour INTEGER NOT NULL CHECK(hour >= 0 AND hour <= 23),
                minute INTEGER NOT NULL CHECK(minute >= 0 AND minute <= 59),
                second INTEGER NOT NULL DEFAULT 0 CHECK(second >= 0 AND second <= 59),
                clock_id INTEGER NOT NULL DEFAULT 1 CHECK(clock_id IN (1, 2)),
                enabled INTEGER NOT NULL DEFAULT 1,
                days TEXT NOT NULL DEFAULT 'daily',
                duration INTEGER NOT NULL DEFAULT 30,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                last_triggered TEXT
            )
        """)
        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def create_alarm(self, alarm: Alarm) -> Alarm:
        """Create a new alarm."""
        cursor = self._conn.execute("""
            INSERT INTO alarms (name, hour, minute, second, clock_id, enabled, days, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alarm.name, alarm.hour, alarm.minute, alarm.second,
            alarm.clock_id, int(alarm.enabled), alarm.days, alarm.duration
        ))
        self._conn.commit()
        
        alarm.id = cursor.lastrowid
        
        row = self._conn.execute(
            "SELECT created_at FROM alarms WHERE id = ?", (alarm.id,)
        ).fetchone()
        alarm.created_at = row[0] if row else None
        
        logger.info(f"Created alarm: {alarm.name} at {alarm.hour:02d}:{alarm.minute:02d}:{alarm.second:02d}")
        return alarm

    def get_alarm(self, alarm_id: int) -> Optional[Alarm]:
        """Get an alarm by ID."""
        row = self._conn.execute(
            "SELECT * FROM alarms WHERE id = ?", (alarm_id,)
        ).fetchone()
        
        if row:
            return self._row_to_alarm(row)
        return None

    def get_all_alarms(self) -> list[Alarm]:
        """Get all alarms."""
        rows = self._conn.execute(
            "SELECT * FROM alarms ORDER BY hour, minute, second"
        ).fetchall()
        return [self._row_to_alarm(row) for row in rows]

    def get_enabled_alarms(self) -> list[Alarm]:
        """Get all enabled alarms."""
        rows = self._conn.execute(
            "SELECT * FROM alarms WHERE enabled = 1 ORDER BY hour, minute, second"
        ).fetchall()
        return [self._row_to_alarm(row) for row in rows]

    def update_alarm(self, alarm: Alarm) -> Optional[Alarm]:
        """Update an existing alarm."""
        if alarm.id is None:
            return None
        
        self._conn.execute("""
            UPDATE alarms SET
                name = ?, hour = ?, minute = ?, second = ?,
                clock_id = ?, enabled = ?, days = ?, duration = ?
            WHERE id = ?
        """, (
            alarm.name, alarm.hour, alarm.minute, alarm.second,
            alarm.clock_id, int(alarm.enabled), alarm.days, alarm.duration,
            alarm.id
        ))
        self._conn.commit()
        
        logger.info(f"Updated alarm {alarm.id}: {alarm.name}")
        return self.get_alarm(alarm.id)

    def delete_alarm(self, alarm_id: int) -> bool:
        """Delete an alarm."""
        cursor = self._conn.execute("DELETE FROM alarms WHERE id = ?", (alarm_id,))
        self._conn.commit()
        
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Deleted alarm {alarm_id}")
        return deleted

    def toggle_alarm(self, alarm_id: int, enabled: bool) -> Optional[Alarm]:
        """Enable or disable an alarm."""
        self._conn.execute(
            "UPDATE alarms SET enabled = ? WHERE id = ?",
            (int(enabled), alarm_id)
        )
        self._conn.commit()
        return self.get_alarm(alarm_id)

    def mark_triggered(self, alarm_id: int) -> None:
        """Mark an alarm as triggered (update last_triggered timestamp)."""
        self._conn.execute(
            "UPDATE alarms SET last_triggered = datetime('now') WHERE id = ?",
            (alarm_id,)
        )
        self._conn.commit()

    def disable_once_alarm(self, alarm_id: int) -> None:
        """Disable a 'once' alarm after it triggers."""
        self._conn.execute(
            "UPDATE alarms SET enabled = 0 WHERE id = ? AND days = 'once'",
            (alarm_id,)
        )
        self._conn.commit()

    def _row_to_alarm(self, row) -> Alarm:
        """Convert a database row to an Alarm object."""
        return Alarm(
            id=row[0],
            name=row[1],
            hour=row[2],
            minute=row[3],
            second=row[4],
            clock_id=row[5],
            enabled=bool(row[6]),
            days=row[7],
            duration=row[8],
            created_at=row[9],
            last_triggered=row[10],
        )

_db: Optional[Database] = None

def get_db() -> Database:
    """Get or create the global database instance."""
    global _db
    if _db is None:
        _db = Database()
        _db.connect()
    return _db

def close_db() -> None:
    """Close the global database connection."""
    global _db
    if _db:
        _db.close()
        _db = None
