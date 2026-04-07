import { useState, useCallback } from "react";
import { motion } from "motion/react";
import { Navigate } from "@tanstack/react-router";
import { Copy, Check, Smartphone, Terminal } from "lucide-react";
import { isDemo } from "../lib/api";

const BASE_URL = window.location.origin;

function CopyButton({ text, label }: { text: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    let success = false;
    try {
      await navigator.clipboard.writeText(text);
      success = true;
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      success = document.execCommand("copy");
      document.body.removeChild(textarea);
    }
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [text]);

  return (
    <motion.button
      className="copy-btn"
      onClick={handleCopy}
      whileTap={{ scale: 0.95 }}
      title={`Copy ${label || "to clipboard"}`}
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
      <span>{copied ? "Copied" : label || "Copy"}</span>
    </motion.button>
  );
}

interface Endpoint {
  name: string;
  method: "GET" | "POST";
  path: string;
  body?: string;
}

const ENDPOINTS: Endpoint[] = [
  { name: "Ring Clock 1", method: "POST", path: "/api/v1/clock/1/on" },
  { name: "Ring Clock 2", method: "POST", path: "/api/v1/clock/2/on" },
  { name: "Stop Clock 1", method: "POST", path: "/api/v1/clock/1/off" },
  { name: "Stop Clock 2", method: "POST", path: "/api/v1/clock/2/off" },
  { name: "Stop All Clocks", method: "POST", path: "/api/v1/clock/all/off" },
  { name: "Emergency Stop", method: "POST", path: "/api/v1/stop/trigger" },
  { name: "Check Status", method: "GET", path: "/api/v1/status" },
];

const SHORTCUT_STEPS = [
  "Open the Shortcuts app on your iPhone or iPad",
  'Tap the "+" button to create a new shortcut',
  'Search for and add the "Get Contents of URL" action',
  "Paste the full endpoint URL from the list above",
  'Tap "Method" and change it to POST (for control actions)',
  'Tap the shortcut name at the top to rename it (e.g. "Ring Alarm")',
  'Tap "Done" to save — run it from Shortcuts, Siri, or your Home Screen',
];

export function ConnectPage() {
  if (isDemo) {
    return <Navigate to="/" />;
  }

  const baseUrl = BASE_URL;

  return (
    <div className="connect-page">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2>Connect</h2>
        <p className="connect-subtitle">
          Integrate Kalembang with iOS Shortcuts, automations, or any tool that
          can make HTTP requests.
        </p>
      </motion.div>

      <motion.section
        className="connect-section"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.05 }}
      >
        <h3 className="connect-section-title">Your Device URL</h3>
        <div className="connect-url-card">
          <code className="connect-url-value">{baseUrl}</code>
          <CopyButton text={baseUrl} label="URL" />
        </div>
        <p className="connect-note">
          Use this address from any device on the same Wi-Fi network.
        </p>
      </motion.section>

      <motion.section
        className="connect-section"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <h3 className="connect-section-title">Quick Actions</h3>
        <div className="endpoint-list">
          {ENDPOINTS.map((ep) => (
            <div key={ep.path} className="endpoint-card">
              <div className="endpoint-header">
                <span className="endpoint-name">{ep.name}</span>
                <span
                  className={`endpoint-method ${ep.method === "GET" ? "method-get" : "method-post"}`}
                >
                  {ep.method}
                </span>
              </div>
              <div className="endpoint-url-row">
                <code className="endpoint-path">{ep.path}</code>
                <CopyButton text={`${baseUrl}${ep.path}`} label="URL" />
              </div>
            </div>
          ))}
        </div>
      </motion.section>

      <motion.section
        className="connect-section"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.15 }}
      >
        <div className="connect-section-header">
          <Smartphone size={18} />
          <h3 className="connect-section-title">iOS Shortcuts</h3>
        </div>
        <ol className="steps-list">
          {SHORTCUT_STEPS.map((step, i) => (
            <li key={i} className="step-item">
              <span className="step-number">{i + 1}</span>
              <span className="step-text">{step}</span>
            </li>
          ))}
        </ol>
        <div className="connect-tip">
          For GET endpoints like Check Status, leave the method as GET. Only
          control actions (on/off/stop) need POST.
        </div>
      </motion.section>

      <motion.section
        className="connect-section"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <div className="connect-section-header">
          <Terminal size={18} />
          <h3 className="connect-section-title">curl Examples</h3>
        </div>
        <div className="code-block-group">
          <div className="code-block-item">
            <div className="code-block-label">Ring Clock 1</div>
            <div className="code-block">
              <code>curl -X POST {baseUrl}/api/v1/clock/1/on</code>
              <CopyButton text={`curl -X POST ${baseUrl}/api/v1/clock/1/on`} />
            </div>
          </div>
          <div className="code-block-item">
            <div className="code-block-label">Stop All Clocks</div>
            <div className="code-block">
              <code>curl -X POST {baseUrl}/api/v1/clock/all/off</code>
              <CopyButton
                text={`curl -X POST ${baseUrl}/api/v1/clock/all/off`}
              />
            </div>
          </div>
          <div className="code-block-item">
            <div className="code-block-label">Check Status</div>
            <div className="code-block">
              <code>curl {baseUrl}/api/v1/status</code>
              <CopyButton text={`curl ${baseUrl}/api/v1/status`} />
            </div>
          </div>
        </div>
        <div className="connect-tip">
          These commands work in Terminal, and the same URLs work with Home
          Assistant REST commands, Tasker HTTP Request, Node-RED HTTP nodes, or
          any automation tool that supports HTTP.
        </div>
      </motion.section>
    </div>
  );
}
