import { Link } from "@tanstack/react-router";
import { motion, AnimatePresence } from "motion/react";
import { useAlarms, useDeleteAlarm, useToggleAlarm } from "../lib";
import { AlarmItem } from "../components/AlarmItem";

export function AlarmsPage() {
  const { data: alarms, isLoading, error } = useAlarms();
  const deleteAlarm = useDeleteAlarm();
  const toggleAlarm = useToggleAlarm();

  if (isLoading) {
    return (
      <motion.div
        className="loading"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        Loading alarms...
      </motion.div>
    );
  }

  if (error) {
    return <div className="error-message">Failed to load alarms</div>;
  }

  const handleDelete = (id: number) => {
    if (confirm("Delete this alarm?")) {
      deleteAlarm.mutate(id);
    }
  };

  const handleToggle = (id: number, enabled: boolean) => {
    toggleAlarm.mutate({ id, enabled });
  };

  return (
    <div className="alarms-page">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2>Alarms</h2>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Link to="/alarms/new" className="btn btn-primary">
            + New Alarm
          </Link>
        </motion.div>
      </motion.div>

      {alarms && alarms.length === 0 ? (
        <motion.div
          className="empty-state"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <p>No alarms yet</p>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Link to="/alarms/new" className="btn btn-primary">
              Create your first alarm
            </Link>
          </motion.div>
        </motion.div>
      ) : (
        <div className="alarms-list">
          <AnimatePresence mode="popLayout">
            {alarms?.map((alarm, index) => (
              <AlarmItem
                key={alarm.id}
                alarm={alarm}
                index={index}
                onToggle={(enabled: boolean) =>
                  handleToggle(alarm.id!, enabled)
                }
                onDelete={() => handleDelete(alarm.id!)}
              />
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
