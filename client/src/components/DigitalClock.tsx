import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";

export function DigitalClock() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const hours24 = time.getHours();
  const hours12 = hours24 % 12 || 12;
  const ampm = hours24 >= 12 ? "PM" : "AM";
  const hours = hours12.toString().padStart(2, "0");
  const minutes = time.getMinutes().toString().padStart(2, "0");
  const seconds = time.getSeconds().toString().padStart(2, "0");

  const dateStr = time.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  return (
    <motion.div
      className="digital-clock"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      <div className="clock-time">
        <span className="clock-hours">{hours}</span>
        <span className="clock-separator">:</span>
        <span className="clock-minutes">{minutes}</span>
        <span className="clock-sub">
          <AnimatePresence mode="popLayout">
            <motion.span
              key={seconds}
              className="clock-seconds"
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 0.7, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              transition={{ duration: 0.15 }}
            >
              {seconds}
            </motion.span>
          </AnimatePresence>
          <span className="clock-ampm">{ampm}</span>
        </span>
      </div>
      <div className="clock-date">{dateStr}</div>
    </motion.div>
  );
}
