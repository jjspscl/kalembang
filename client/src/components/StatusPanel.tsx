import type { Status } from "../lib";

interface StatusPanelProps {
  status: Status | null;
}

export function StatusPanel({ status }: StatusPanelProps) {
  if (!status) {
    return null;
  }

  return (
    <div className="card">
      <h2>Status</h2>
      <div className="status-panel">
        <div className="status-row">
          <span className="status-label">Clock 1</span>
          <span
            className={`status-value ${status.clock1.enabled ? "on" : "off"}`}
          >
            {status.clock1.enabled ? "ON" : "OFF"} ({status.clock1.duty}%)
          </span>
        </div>
        <div className="status-row">
          <span className="status-label">Clock 2</span>
          <span
            className={`status-value ${status.clock2.enabled ? "on" : "off"}`}
          >
            {status.clock2.enabled ? "ON" : "OFF"} ({status.clock2.duty}%)
          </span>
        </div>
        <div className="status-row">
          <span className="status-label">STOP Button</span>
          <span
            className={`status-value ${
              status.stop_button_pressed ? "warning" : "off"
            }`}
          >
            {status.stop_button_pressed === null
              ? "N/A"
              : status.stop_button_pressed
              ? "PRESSED"
              : "Released"}
          </span>
        </div>
      </div>
    </div>
  );
}

export default StatusPanel;
