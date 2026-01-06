import { useState, useRef, useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import { motion, AnimatePresence } from "motion/react";
import { MoreVertical, Pencil, Copy, Trash2 } from "lucide-react";
import type { Alarm } from "../lib";

interface AlarmItemProps {
  alarm: Alarm;
  onToggle: (enabled: boolean) => void;
  onDelete: () => void;
  onDuplicate: () => void;
  index?: number;
}

export function AlarmItem({
  alarm,
  onToggle,
  onDelete,
  onDuplicate,
  index = 0,
}: AlarmItemProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  const hour12 = alarm.hour % 12 || 12;
  const ampm = alarm.hour >= 12 ? "PM" : "AM";
  const timeStr = `${hour12}:${alarm.minute
    .toString()
    .padStart(2, "0")}:${alarm.second.toString().padStart(2, "0")} ${ampm}`;

  const daysLabel = getDaysLabel(alarm.days);

  const handleEdit = () => {
    setMenuOpen(false);
    navigate({ to: "/alarms/$alarmId", params: { alarmId: String(alarm.id) } });
  };

  const handleDuplicate = () => {
    setMenuOpen(false);
    onDuplicate();
  };

  const handleDelete = () => {
    setMenuOpen(false);
    onDelete();
  };

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

      <div className="alarm-info">
        <div className="alarm-time">{timeStr}</div>
        <div className="alarm-meta">
          <span className="alarm-name">{alarm.name}</span>
          <span className="alarm-days">{daysLabel}</span>
          <span className="alarm-clock">Clock {alarm.clock_id}</span>
        </div>
      </div>

      <div className="alarm-menu-container" ref={menuRef}>
        <motion.button
          className="btn btn-icon btn-menu"
          onClick={() => setMenuOpen(!menuOpen)}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <MoreVertical size={20} />
        </motion.button>

        <AnimatePresence>
          {menuOpen && (
            <motion.div
              className="alarm-dropdown"
              initial={{ opacity: 0, scale: 0.9, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -10 }}
              transition={{ duration: 0.15 }}
            >
              <button className="dropdown-item" onClick={handleEdit}>
                <Pencil size={16} />
                Edit
              </button>
              <button className="dropdown-item" onClick={handleDuplicate}>
                <Copy size={16} />
                Duplicate
              </button>
              <button className="dropdown-item dropdown-item-danger" onClick={handleDelete}>
                <Trash2 size={16} />
                Delete
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
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
