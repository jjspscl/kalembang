import { Outlet, Link, useLocation } from "@tanstack/react-router";
import { motion } from "motion/react";
import { isDemo } from "../lib/api";
import { useAlarmNotifications } from "../lib/useAlarmNotifications";
import { AlarmNotification } from "../components/AlarmNotification";

export function RootLayout() {
  const location = useLocation();
  const isHome = location.pathname === "/";
  const isAlarms = location.pathname.startsWith("/alarms");
  const { toasts, dismissToast } = useAlarmNotifications();

  return (
    <div className="app">
      <AlarmNotification toasts={toasts} onDismiss={dismissToast} />
      {isDemo && (
        <motion.div
          className="demo-banner"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          🎮 Demo Mode — Using simulated data
        </motion.div>
      )}
      <motion.header
        className="header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <h1>🔔 Kalembang</h1>
        <nav className="nav">
          <Link to="/" className={`nav-link ${isHome ? "active" : ""}`}>
            Home
            {isHome && (
              <motion.div
                className="nav-indicator"
                layoutId="nav-indicator"
                transition={{ type: "spring", stiffness: 500, damping: 35 }}
              />
            )}
          </Link>
          <Link to="/alarms" className={`nav-link ${isAlarms ? "active" : ""}`}>
            Alarms
            {isAlarms && (
              <motion.div
                className="nav-indicator"
                layoutId="nav-indicator"
                transition={{ type: "spring", stiffness: 500, damping: 35 }}
              />
            )}
          </Link>
        </nav>
      </motion.header>

      <main className="main">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  );
}
