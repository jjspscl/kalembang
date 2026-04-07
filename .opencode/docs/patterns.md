# Kalembang Pattern System Research & Implementation Plan

## Overview

This document outlines the research and implementation plan for adding iOS-like haptic feedback pattern generation to Kalembang. Instead of phone vibration motors, we control two physical clock motors (Clock 1 & Clock 2) via L298N motor driver.

---

## iOS Core Haptics Concepts

### Event Types
- **Transient**: Short impulse/tap (like a click) - ~0.1s duration
- **Continuous**: Sustained vibration for a specified duration (up to 30s)

### Event Parameters
| Parameter | Description | Range |
|-----------|-------------|-------|
| `relativeTime` | When the event starts (seconds from pattern start) | 0.0 - ∞ |
| `duration` | How long the event lasts | 0.0 - 30.0 |
| `intensity` | Strength of vibration | 0.0 - 1.0 |
| `sharpness` | Feel/texture of vibration | 0.0 - 1.0 |

### AHAP File Format (Apple Haptic Audio Pattern)

Apple uses JSON-like files to define haptic patterns:

```json
{
  "Version": 1.0,
  "Pattern": [
    {
      "Event": {
        "Time": 0.0,
        "EventType": "HapticTransient",
        "EventParameters": [
          {"ParameterID": "HapticIntensity", "ParameterValue": 1.0},
          {"ParameterID": "HapticSharpness", "ParameterValue": 0.5}
        ]
      }
    },
    {
      "Event": {
        "Time": 0.5,
        "EventType": "HapticContinuous",
        "EventDuration": 1.0,
        "EventParameters": [
          {"ParameterID": "HapticIntensity", "ParameterValue": 0.8},
          {"ParameterID": "HapticSharpness", "ParameterValue": 0.3}
        ]
      }
    }
  ]
}
```

---

## Kalembang Adaptation

### Concept: Two-Track Pattern System

Instead of one vibration motor with intensity/sharpness, we have **two clock motors** with PWM duty cycle control:

```
┌─────────────────────────────────────────────────────────────┐
│  Pattern Timeline (30 seconds)                              │
├─────────────────────────────────────────────────────────────┤
│  Clock 1 ████░░░░░░██████████░░░░░███████████████████       │
├─────────────────────────────────────────────────────────────┤
│  Clock 2 ░░░░░░░████████░░░░░░░░░░░░███████████████████     │
└─────────────────────────────────────────────────────────────┘
│  0s      5s      10s     15s     20s     25s     30s        │
```

### Kalembang Pattern Format

```typescript
interface PatternEvent {
  clock: 1 | 2;           // Which motor to control
  time: number;           // Start time in seconds (relative to pattern start)
  duration: number;       // How long to run (seconds)
  duty: number;           // PWM duty cycle (0-100, maps to intensity)
}

interface Pattern {
  name: string;
  version: number;
  totalDuration: number;  // Total pattern length in seconds
  events: PatternEvent[];
}
```

### Example Pattern

```json
{
  "name": "Gentle Wake",
  "version": 1,
  "totalDuration": 30,
  "events": [
    { "clock": 1, "time": 0.0, "duration": 0.5, "duty": 30 },
    { "clock": 2, "time": 1.0, "duration": 0.5, "duty": 30 },
    { "clock": 1, "time": 2.0, "duration": 0.8, "duty": 50 },
    { "clock": 2, "time": 3.0, "duration": 0.8, "duty": 50 },
    { "clock": 1, "time": 4.5, "duration": 1.0, "duty": 70 },
    { "clock": 2, "time": 5.5, "duration": 1.0, "duty": 70 },
    { "clock": 1, "time": 7.0, "duration": 2.0, "duty": 100 },
    { "clock": 2, "time": 7.0, "duration": 2.0, "duty": 100 }
  ]
}
```

---

## Alarm Mode Options

Each alarm now has 3 modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Clock 1** | Only Clock 1 rings for specified duration | Simple single-clock alarm |
| **Clock 2** | Only Clock 2 rings for specified duration | Simple single-clock alarm |
| **Pattern** | Execute a pattern with both clocks | Complex, customizable wake-up experience |

### Database Schema Changes

```sql
-- Add mode column (default to existing behavior)
ALTER TABLE alarms ADD COLUMN mode TEXT NOT NULL DEFAULT 'clock1';
-- Possible values: 'clock1', 'clock2', 'pattern'

-- Add pattern column (JSON string for pattern mode)
ALTER TABLE alarms ADD COLUMN pattern TEXT;
-- Contains pattern JSON when mode='pattern', NULL otherwise

-- Note: When mode='clock1' or 'clock2', use existing clock_id and duration fields
-- When mode='pattern', pattern JSON contains full timing/duration info
```

---

## Preset Patterns

### Built-in Pattern Library

```typescript
const PRESET_PATTERNS = {
  gentle: {
    name: "Gentle Wake",
    description: "Gradual intensity increase, alternating clocks",
    totalDuration: 30,
    events: [
      // Soft start
      { clock: 1, time: 0, duration: 0.3, duty: 20 },
      { clock: 2, time: 1, duration: 0.3, duty: 20 },
      { clock: 1, time: 2, duration: 0.5, duty: 30 },
      { clock: 2, time: 3, duration: 0.5, duty: 30 },
      // Medium buildup
      { clock: 1, time: 5, duration: 1.0, duty: 50 },
      { clock: 2, time: 6.5, duration: 1.0, duty: 50 },
      { clock: 1, time: 8, duration: 1.5, duty: 70 },
      { clock: 2, time: 10, duration: 1.5, duty: 70 },
      // Full intensity
      { clock: 1, time: 12, duration: 18, duty: 100 },
      { clock: 2, time: 12, duration: 18, duty: 100 }
    ]
  },

  urgent: {
    name: "Urgent",
    description: "Rapid alternating pulses at full intensity",
    totalDuration: 30,
    events: [
      // Rapid fire alternating
      { clock: 1, time: 0, duration: 0.2, duty: 100 },
      { clock: 2, time: 0.25, duration: 0.2, duty: 100 },
      { clock: 1, time: 0.5, duration: 0.2, duty: 100 },
      { clock: 2, time: 0.75, duration: 0.2, duty: 100 },
      { clock: 1, time: 1.0, duration: 0.2, duty: 100 },
      { clock: 2, time: 1.25, duration: 0.2, duty: 100 },
      // Pattern repeats...
    ]
  },

  alternating: {
    name: "Alternating",
    description: "Clock 1 and Clock 2 take turns",
    totalDuration: 30,
    events: [
      { clock: 1, time: 0, duration: 1.5, duty: 100 },
      { clock: 2, time: 2, duration: 1.5, duty: 100 },
      { clock: 1, time: 4, duration: 1.5, duty: 100 },
      { clock: 2, time: 6, duration: 1.5, duty: 100 },
      // Continues alternating...
    ]
  },

  heartbeat: {
    name: "Heartbeat",
    description: "Mimics heartbeat rhythm (thump-thump, pause)",
    totalDuration: 30,
    events: [
      // Beat 1
      { clock: 1, time: 0, duration: 0.15, duty: 100 },
      { clock: 1, time: 0.2, duration: 0.1, duty: 70 },
      // Pause ~0.7s
      // Beat 2
      { clock: 1, time: 1.0, duration: 0.15, duty: 100 },
      { clock: 1, time: 1.2, duration: 0.1, duty: 70 },
      // Continues...
    ]
  },

  crescendo: {
    name: "Crescendo",
    description: "Both clocks increase intensity together",
    totalDuration: 30,
    events: [
      { clock: 1, time: 0, duration: 5, duty: 20 },
      { clock: 2, time: 0, duration: 5, duty: 20 },
      { clock: 1, time: 5, duration: 5, duty: 40 },
      { clock: 2, time: 5, duration: 5, duty: 40 },
      { clock: 1, time: 10, duration: 5, duty: 60 },
      { clock: 2, time: 10, duration: 5, duty: 60 },
      { clock: 1, time: 15, duration: 5, duty: 80 },
      { clock: 2, time: 15, duration: 5, duty: 80 },
      { clock: 1, time: 20, duration: 10, duty: 100 },
      { clock: 2, time: 20, duration: 10, duty: 100 }
    ]
  },

  sos: {
    name: "SOS",
    description: "Morse code SOS pattern (· · · — — — · · ·)",
    totalDuration: 30,
    events: [
      // S: · · ·
      { clock: 1, time: 0, duration: 0.2, duty: 100 },
      { clock: 1, time: 0.4, duration: 0.2, duty: 100 },
      { clock: 1, time: 0.8, duration: 0.2, duty: 100 },
      // O: — — —
      { clock: 2, time: 1.5, duration: 0.6, duty: 100 },
      { clock: 2, time: 2.3, duration: 0.6, duty: 100 },
      { clock: 2, time: 3.1, duration: 0.6, duty: 100 },
      // S: · · ·
      { clock: 1, time: 4.2, duration: 0.2, duty: 100 },
      { clock: 1, time: 4.6, duration: 0.2, duty: 100 },
      { clock: 1, time: 5.0, duration: 0.2, duty: 100 },
      // Repeat pattern...
    ]
  }
};
```

---

## UI Design

### Alarm Edit Page - Mode Selection

```
┌───────────────────────────────────────────────────────────────┐
│ Alarm Mode                                                    │
│                                                               │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│ │   Clock 1   │  │   Clock 2   │  │   Pattern   │            │
│ │     🔔      │  │     🔔      │  │     📊      │            │
│ │  (simple)   │  │  (simple)   │  │  (custom)   │            │
│ └─────────────┘  └─────────────┘  └─────────────┘            │
│       ✓                                                       │
│                                                               │
│ Duration: [____30____] seconds                                │
│ ℹ️ 0 = ring until manually stopped                            │
└───────────────────────────────────────────────────────────────┘
```

### Pattern Mode Selection

```
┌───────────────────────────────────────────────────────────────┐
│ Select Pattern                                                │
│                                                               │
│ ┌───────────────────────────────────────────────────────────┐│
│ │ ▼ Gentle Wake                                             ││
│ │   ─────────────────────────────────────────────────────   ││
│ │   Urgent                                                  ││
│ │   Alternating                                             ││
│ │   Heartbeat                                               ││
│ │   Crescendo                                               ││
│ │   SOS                                                     ││
│ │   ─────────────────────────────────────────────────────   ││
│ │   + Create Custom Pattern                                 ││
│ └───────────────────────────────────────────────────────────┘│
│                                                               │
│ Preview:                                                      │
│ ┌───────────────────────────────────────────────────────────┐│
│ │ Clock 1  ░██░░░░██░░░░░████░░░░░░░████████████████████░░░ ││
│ │ Clock 2  ░░░░██░░░░██░░░░░████░░░░████████████████████░░░ ││
│ │          0s     5s     10s    15s    20s    25s    30s    ││
│ └───────────────────────────────────────────────────────────┘│
│                                                               │
│ [▶ Test Pattern]                                              │
└───────────────────────────────────────────────────────────────┘
```

### Pattern Editor (Future Enhancement)

```
┌───────────────────────────────────────────────────────────────┐
│ Pattern Editor: "My Custom Pattern"                           │
│                                                               │
│ Total Duration: [____30____] seconds                          │
│                                                               │
│ Timeline                                                      │
│ ┌───────────────────────────────────────────────────────────┐│
│ │ Clock 1  │▓▓▓│   │▓▓▓▓▓│      │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│     ││
│ ├──────────┼───┴───┴─────┴──────┴─────────────────────┴─────┤│
│ │ Clock 2  │   │▓▓▓│     │▓▓▓▓▓│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│       ││
│ └──────────┴───────────────────────────────────────────────┘ │
│            0    5    10   15   20   25   30                   │
│                                                               │
│ Events:                                                       │
│ ┌─────┬────────┬──────────┬──────────┬───────┬─────────────┐ │
│ │  #  │ Clock  │  Start   │ Duration │ Duty  │   Actions   │ │
│ ├─────┼────────┼──────────┼──────────┼───────┼─────────────┤ │
│ │  1  │   1    │   0.0s   │   0.5s   │  30%  │  ✏️  🗑️     │ │
│ │  2  │   2    │   1.0s   │   0.5s   │  30%  │  ✏️  🗑️     │ │
│ │  3  │   1    │   2.0s   │   1.0s   │  50%  │  ✏️  🗑️     │ │
│ │ ... │  ...   │   ...    │   ...    │  ...  │  ...        │ │
│ └─────┴────────┴──────────┴──────────┴───────┴─────────────┘ │
│                                                               │
│ [+ Add Event]  [▶ Preview]  [💾 Save]                         │
└───────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Backend (Python/FastAPI)

1. **Database Migration**
   - Add `mode` column to alarms table
   - Add `pattern` column to alarms table

2. **Update Alarm Model**
   ```python
   @dataclass
   class Alarm:
       # ... existing fields ...
       mode: str = "clock1"  # "clock1", "clock2", "pattern"
       pattern: Optional[str] = None  # JSON string
   ```

3. **Create Pattern Player**
   ```python
   class PatternPlayer:
       async def play(self, pattern_json: str) -> None:
           """Execute a pattern asynchronously."""
           pattern = json.loads(pattern_json)
           events = sorted(pattern["events"], key=lambda e: e["time"])
           # Schedule each event at the correct time
           # Handle overlapping events for both clocks
   ```

4. **Update Alarm Scheduler**
   - Check alarm mode
   - If `pattern`, use PatternPlayer instead of simple on/off

5. **Add API Endpoints**
   - `GET /api/v1/patterns/presets` - List preset patterns
   - `POST /api/v1/patterns/test` - Test play a pattern

### Phase 2: Frontend (React/TypeScript)

1. **Update API Types**
   ```typescript
   interface Alarm {
     // ... existing fields ...
     mode: "clock1" | "clock2" | "pattern";
     pattern?: string;
   }
   ```

2. **Update AlarmEditPage**
   - Add mode selector (radio buttons or segmented control)
   - Show duration picker for clock1/clock2 modes
   - Show pattern selector for pattern mode

3. **Create Pattern Components**
   - `PatternSelector` - Dropdown with presets
   - `PatternPreview` - Visual timeline of pattern
   - `PatternEditor` (future) - Full editor UI

### Phase 3: Enhancements (Future)

1. **Custom Pattern Editor**
   - Visual timeline editor
   - Drag & drop event blocks
   - Real-time preview

2. **Pattern Library**
   - Save custom patterns
   - Share patterns
   - Import/export patterns

3. **Audio Sync (Advanced)**
   - Sync patterns to audio files
   - Auto-generate patterns from audio

---

## API Reference

### Pattern Presets Endpoint

```
GET /api/v1/patterns/presets

Response:
{
  "presets": [
    {
      "id": "gentle",
      "name": "Gentle Wake",
      "description": "Gradual intensity increase",
      "totalDuration": 30,
      "events": [...]
    },
    ...
  ]
}
```

### Test Pattern Endpoint

```
POST /api/v1/patterns/test
Content-Type: application/json

{
  "pattern": {
    "name": "Test",
    "totalDuration": 5,
    "events": [
      { "clock": 1, "time": 0, "duration": 1, "duty": 100 },
      { "clock": 2, "time": 1.5, "duration": 1, "duty": 100 }
    ]
  }
}

Response:
{
  "message": "Pattern started",
  "success": true
}
```

---

## Technical Considerations

### Event Scheduling

The pattern player needs to handle:
1. **Precise timing** - Use asyncio scheduling
2. **Overlapping events** - Both clocks can run simultaneously
3. **Duty cycle changes** - Smooth transitions between duty levels
4. **Cancellation** - Stop pattern immediately on user request

### Example Implementation

```python
import asyncio
import json
from typing import TypedDict

class PatternEvent(TypedDict):
    clock: int
    time: float
    duration: float
    duty: int

class PatternPlayer:
    def __init__(self, controller: MotorController):
        self._controller = controller
        self._running = False
        self._tasks: list[asyncio.Task] = []

    async def play(self, pattern_json: str) -> None:
        if self._running:
            await self.stop()

        pattern = json.loads(pattern_json)
        events: list[PatternEvent] = pattern["events"]
        self._running = True

        for event in events:
            task = asyncio.create_task(
                self._schedule_event(event)
            )
            self._tasks.append(task)

        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._running = False

    async def _schedule_event(self, event: PatternEvent) -> None:
        await asyncio.sleep(event["time"])

        if not self._running:
            return

        clock_id = event["clock"]
        duty = event["duty"]
        duration = event["duration"]

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

    async def stop(self) -> None:
        self._running = False
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
        self._controller.all_off()
```

---

## Summary

This pattern system transforms Kalembang from a simple "clock on/off" alarm into a sophisticated wake-up experience system, similar to how iOS Core Haptics transformed simple phone vibrations into rich tactile feedback.

**Key Benefits:**
- ✅ More engaging wake-up experience
- ✅ Customizable alarm "feel"
- ✅ Visual pattern editor (future)
- ✅ Preset patterns for quick setup
- ✅ Compatible with existing simple alarm mode
