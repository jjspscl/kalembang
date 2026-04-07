import { useRef, useState, useEffect, useCallback } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useStatus } from "./queries";
import type { ActiveAlarm } from "./api";
import type { AlarmToast } from "../components/AlarmNotification";
import {
  requestNotificationPermission,
  sendBrowserNotification,
} from "./notifications";

const AUTO_DISMISS_MS = 10_000;

export function useAlarmNotifications() {
  const { data: status } = useStatus();
  const navigate = useNavigate();
  const prevAlarmIdsRef = useRef<Set<number>>(new Set());
  const [toasts, setToasts] = useState<AlarmToast[]>([]);
  const dismissTimersRef = useRef<Map<number, ReturnType<typeof setTimeout>>>(
    new Map(),
  );

  const dismissToast = useCallback((alarmId: number) => {
    setToasts((prev) => prev.filter((t) => t.alarm.id !== alarmId));
    const timer = dismissTimersRef.current.get(alarmId);
    if (timer) {
      clearTimeout(timer);
      dismissTimersRef.current.delete(alarmId);
    }
  }, []);

  const scheduleAutoDismiss = useCallback(
    (alarmId: number) => {
      const existing = dismissTimersRef.current.get(alarmId);
      if (existing) clearTimeout(existing);

      const timer = setTimeout(() => {
        dismissToast(alarmId);
      }, AUTO_DISMISS_MS);
      dismissTimersRef.current.set(alarmId, timer);
    },
    [dismissToast],
  );

  const navigateToAlarm = useCallback(
    (alarmId: number) => {
      navigate({
        to: "/alarms/$alarmId",
        params: { alarmId: String(alarmId) },
      });
    },
    [navigate],
  );

  useEffect(() => {
    if (!status) return;

    const currentAlarms: ActiveAlarm[] = status.active_alarms ?? [];
    const currentIds = new Set(currentAlarms.map((a) => a.id));
    const prevIds = prevAlarmIdsRef.current;

    const newAlarms = currentAlarms.filter((a) => !prevIds.has(a.id));

    if (newAlarms.length > 0) {
      requestNotificationPermission();

      setToasts((prev) => {
        const existingIds = new Set(prev.map((t) => t.alarm.id));
        const additions = newAlarms
          .filter((a) => !existingIds.has(a.id))
          .map((alarm) => ({ alarm }));
        return [...prev, ...additions];
      });

      for (const alarm of newAlarms) {
        sendBrowserNotification(alarm, navigateToAlarm);
        scheduleAutoDismiss(alarm.id);
      }
    }

    const removedIds = [...prevIds].filter((id) => !currentIds.has(id));
    for (const id of removedIds) {
      dismissToast(id);
    }

    prevAlarmIdsRef.current = currentIds;
  }, [status, navigateToAlarm, scheduleAutoDismiss, dismissToast]);

  useEffect(() => {
    return () => {
      for (const timer of dismissTimersRef.current.values()) {
        clearTimeout(timer);
      }
    };
  }, []);

  return { toasts, dismissToast };
}
