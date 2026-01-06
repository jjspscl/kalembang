import { useState } from "react";
import { motion } from "motion/react";
import { useClockOn, useClockOff, useClockDuty } from "../lib";

interface ClockCardProps {
  clockId: 1 | 2;
  title: string;
  enabled: boolean;
  duty: number;
}

export function ClockCard({
  clockId,
  title,
  enabled,
  duty,
}: ClockCardProps) {
  const [localDuty, setLocalDuty] = useState(duty);
  const clockOn = useClockOn(clockId);
  const clockOff = useClockOff(clockId);
  const clockDuty = useClockDuty(clockId);
  if (duty !== localDuty && !clockDuty.isPending) {
    setLocalDuty(duty);
  }

  const handleDutyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalDuty(parseInt(e.target.value, 10));
  };

  const handleDutyCommit = () => {
    if (localDuty !== duty) {
      clockDuty.mutate(localDuty);
    }
  };

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <h2>{title}</h2>

      <div className="clock-controls">
        <motion.button
          className="btn btn-on"
          onClick={() => clockOn.mutate()}
          disabled={enabled || clockOn.isPending}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          transition={{ duration: 0.1 }}
        >
          ON
        </motion.button>
        <motion.button
          className="btn btn-off"
          onClick={() => clockOff.mutate()}
          disabled={!enabled || clockOff.isPending}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          transition={{ duration: 0.1 }}
        >
          OFF
        </motion.button>
        <motion.span
          className={`status-indicator ${enabled ? "on" : "off"}`}
          animate={{ opacity: enabled ? 1 : 0.6 }}
          transition={{ duration: 0.2 }}
        >
          {enabled ? "● Running" : "○ Stopped"}
        </motion.span>
      </div>

      <div className="duty-control">
        <span>Duty:</span>
        <input
          type="range"
          min="0"
          max="100"
          value={localDuty}
          onChange={handleDutyChange}
          onMouseUp={handleDutyCommit}
          onTouchEnd={handleDutyCommit}
        />
        <span className="duty-value">{localDuty}%</span>
      </div>
    </motion.div>
  );
}

export default ClockCard;
