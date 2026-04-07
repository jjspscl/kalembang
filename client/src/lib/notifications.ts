import type { ActiveAlarm } from "./api";

let permissionRequested = false;

export function requestNotificationPermission(): void {
  if (permissionRequested) return;
  if (!("Notification" in window)) return;
  if (Notification.permission === "granted") return;
  if (Notification.permission === "denied") return;

  permissionRequested = true;
  Notification.requestPermission();
}

export function sendBrowserNotification(
  alarm: ActiveAlarm,
  onNavigate: (alarmId: number) => void,
): void {
  if (!("Notification" in window)) return;
  if (Notification.permission !== "granted") return;

  const title = `${alarm.name}`;
  const body = `Clock ${alarm.clock_id} ringing`;

  const notification = new Notification(title, {
    body,
    tag: `alarm-${alarm.id}`,
  } as NotificationOptions);

  notification.onclick = () => {
    window.focus();
    onNavigate(alarm.id);
    notification.close();
  };
}
