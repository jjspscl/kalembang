import { Link } from "@tanstack/react-router";
import { motion } from "motion/react";
import type { Alarm } from "../lib";

interface AlarmItemProps {
  alarm: Alarm;
  onToggle: (enabled: boolean) => void;
  onDelete: () => void;
  index?: number;
}

export function AlarmItem({
  alarm,
  onToggle,
  onDelete,
  index = 0,
}: AlarmItemProps) {

  const hour12 = alarm.hour % 12 || 12;
  const ampm = alarm.hour >= 12 ? "PM" : "AM";
  const timeStr = `${hour12}:${alarm.minute
    .toString()
    .padStart(2, "0")}:${alarm.second.toString().padStart(2, "0")} ${ampm}`;

  const daysLabel = getDaysLabel(alarm.days);

  return (
    <motion.div
      className={`alarm-item ${!alarm.enabled ? "disabled" : ""}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.25, delay: index * 0.05 }}
      layout
    >
      <div className="alarm-toggle">
        <label className="toggle">
          <input
            type="checkbox"
            checked={alarm.enabled}
            onChange={(e) => onToggle(e.target.checked)}
          />
          <motion.span
            className="toggle-slider"
            animate={{ backgroundColor: alarm.enabled ? "#4ade80" : "#475569" }}
            transition={{ duration: 0.2 }}
          />
        </label>
      </div>

      <Link
        to="/alarms/$alarmId"
        params={{ alarmId: String(alarm.id) }}
        className="alarm-info"
      >
        <div className="alarm-time">{timeStr}</div>
        <div className="alarm-meta">
          <span className="alarm-name">{alarm.name}</span>
          <span className="alarm-days">{daysLabel}</span>
          <span className="alarm-clock">Clock {alarm.clock_id}</span>
        </div>
      </Link>

      <motion.button
        className="btn btn-icon btn-danger"
        onClick={onDelete}
        title="Delete alarm"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        ✕
      </motion.button>
    </motion.div>
  );
}

function getDaysLabel(days: string): string {
  switch (days) {
    case "daily":
      return "Every day";
    case "once":
      return "Once";
    case "mon,tue,wed,thu,fri":
      return "Weekdays";
    case "sat,sun":
      return "Weekends";
    default:
      return days
        .split(",")
        .map((d) => d.charAt(0).toUpperCase() + d.slice(1, 3))
        .join(", ");
  }
}
