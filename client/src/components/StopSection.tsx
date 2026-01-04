import { motion, AnimatePresence } from "motion/react";
import { useStopTrigger, useStopClear } from "../lib";

interface StopSectionProps {
  isLatched: boolean;
}

export function StopSection({ isLatched }: StopSectionProps) {
  const stopTrigger = useStopTrigger();
  const stopClear = useStopClear();

  return (
    <motion.div
      className="stop-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      <AnimatePresence>
        {isLatched && (
          <motion.div
            className="latch-warning"
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{
              opacity: 1,
              scale: 1,
              y: 0,
              x: [0, -4, 4, -4, 4, 0],
            }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.4, x: { duration: 0.4, delay: 0.1 } }}
          >
            <p>⚠️ STOP is latched — clocks cannot be turned on</p>
            <motion.button
              className="btn btn-warning"
              onClick={() => stopClear.mutate()}
              disabled={stopClear.isPending}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
            >
              Clear Latch
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        className="btn btn-stop"
        onClick={() => stopTrigger.mutate()}
        disabled={stopTrigger.isPending}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.98 }}
        transition={{ duration: 0.1 }}
      >
        🛑 STOP ALL
      </motion.button>
    </motion.div>
  );
}
