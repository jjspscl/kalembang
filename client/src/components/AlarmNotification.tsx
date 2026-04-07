import { motion, AnimatePresence } from "motion/react";
import { useNavigate } from "@tanstack/react-router";
import type { ActiveAlarm } from "../lib/api";

export interface AlarmToast {
  alarm: ActiveAlarm;
}

interface AlarmNotificationProps {
  toasts: AlarmToast[];
  onDismiss: (alarmId: number) => void;
}

export function AlarmNotification({
  toasts,
  onDismiss,
}: AlarmNotificationProps) {
  const navigate = useNavigate();

  if (toasts.length === 0) return null;

  return (
    <div className="alarm-notification-container">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <motion.div
            key={toast.alarm.id}
            className="alarm-notification"
            initial={{ opacity: 0, y: -60, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -40, scale: 0.95 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            onClick={() => {
              onDismiss(toast.alarm.id);
              navigate({
                to: "/alarms/$alarmId",
                params: { alarmId: String(toast.alarm.id) },
              });
            }}
            layout
          >
            <div className="alarm-notification-pulse" />
            <div className="alarm-notification-content">
              <div className="alarm-notification-icon">🔔</div>
              <div className="alarm-notification-text">
                <span className="alarm-notification-title">
                  {toast.alarm.name}
                </span>
                <span className="alarm-notification-subtitle">
                  Clock {toast.alarm.clock_id} ringing
                </span>
              </div>
              <div className="alarm-notification-badge">Tap to view</div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
