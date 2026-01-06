import { motion } from "motion/react";
import { useStopTrigger } from "../lib";

export function StopSection() {
  const stopTrigger = useStopTrigger();

  return (
    <motion.div
      className="stop-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
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
