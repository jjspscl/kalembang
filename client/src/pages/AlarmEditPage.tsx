import { useState, useEffect, useMemo } from "react";
import { useNavigate, useParams } from "@tanstack/react-router";
import { z } from "zod";
import {
  useAlarm,
  useCreateAlarm,
  useUpdateAlarm,
  type AlarmCreate,
} from "../lib";

const useIsMobile = () => {
  return useMemo(() => {
    if (typeof window === "undefined") return false;
    return (
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      ) ||
      ("ontouchstart" in window && window.innerWidth < 768)
    );
  }, []);
};
const alarmFormSchema = z.object({
  name: z.string().max(100, "Name must be 100 characters or less").optional(),
  hour12: z
    .number()
    .min(1, "Hour must be between 1 and 12")
    .max(12, "Hour must be between 1 and 12"),
  ampm: z.enum(["AM", "PM"]),
  minute: z
    .number()
    .min(0, "Minute must be between 0 and 59")
    .max(59, "Minute must be between 0 and 59"),
  second: z
    .number()
    .min(0, "Second must be between 0 and 59")
    .max(59, "Second must be between 0 and 59"),
  clockId: z.number().min(1).max(2),
  days: z.string().min(1, "Please select when the alarm should repeat"),
  duration: z
    .number()
    .min(0, "Duration must be 0 or greater")
    .max(3600, "Duration must be 1 hour or less"),
});

type AlarmFormData = z.infer<typeof alarmFormSchema>;
type FormErrors = Partial<Record<keyof AlarmFormData, string>>;

const DAYS_OPTIONS = [
  { value: "daily", label: "Every day" },
  { value: "once", label: "Once" },
  { value: "mon,tue,wed,thu,fri", label: "Weekdays" },
  { value: "sat,sun", label: "Weekends" },
  { value: "custom", label: "Custom..." },
];

const DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function AlarmEditPage() {
  const navigate = useNavigate();
  const params = useParams({ strict: false });
  const alarmId = params.alarmId ? parseInt(params.alarmId) : null;
  const isEditing = alarmId !== null;

  const { data: existingAlarm, isLoading } = useAlarm(alarmId!, {
    enabled: isEditing,
  });

  const createAlarm = useCreateAlarm();
  const updateAlarm = useUpdateAlarm();
  const isMobile = useIsMobile();
  const [name, setName] = useState("");
  const [hour12, setHour12] = useState(7);
  const [ampm, setAmpm] = useState<"AM" | "PM">("AM");
  const [minute, setMinute] = useState(0);
  const [second, setSecond] = useState(0);
  const [clockId, setClockId] = useState(1);
  const [days, setDays] = useState("daily");
  const [customDays, setCustomDays] = useState<string[]>([]);
  const [duration, setDuration] = useState(30);
  const [showCustomDays, setShowCustomDays] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const to12Hour = (hour24: number) => {
    const h = hour24 % 12 || 12;
    const ap = hour24 >= 12 ? "PM" : "AM";
    return { hour12: h, ampm: ap as "AM" | "PM" };
  };
  const to24Hour = (h12: number, ap: "AM" | "PM") => {
    if (ap === "AM") {
      return h12 === 12 ? 0 : h12;
    } else {
      return h12 === 12 ? 12 : h12 + 12;
    }
  };

  const getNativeTimeValue = () => {
    const h24 = to24Hour(hour12, ampm);
    return `${h24.toString().padStart(2, "0")}:${minute
      .toString()
      .padStart(2, "0")}:${second.toString().padStart(2, "0")}`;
  };

  const handleNativeTimeChange = (value: string) => {
    const parts = value.split(":");
    const h24 = parseInt(parts[0]) || 0;
    const m = parseInt(parts[1]) || 0;
    const s = parts[2] ? parseInt(parts[2]) : second;
    const { hour12: h, ampm: ap } = to12Hour(h24);
    setHour12(h);
    setAmpm(ap);
    setMinute(m);
    setSecond(s);
    setErrors((prev) => ({
      ...prev,
      hour12: undefined,
      minute: undefined,
      second: undefined,
    }));
  };
  useEffect(() => {
    if (existingAlarm) {
      setName(existingAlarm.name);
      const { hour12: h, ampm: ap } = to12Hour(existingAlarm.hour);
      setHour12(h);
      setAmpm(ap);
      setMinute(existingAlarm.minute);
      setSecond(existingAlarm.second);
      setClockId(existingAlarm.clock_id);
      setDuration(existingAlarm.duration);
      const daysValue = existingAlarm.days;
      if (
        ["daily", "once", "mon,tue,wed,thu,fri", "sat,sun"].includes(daysValue)
      ) {
        setDays(daysValue);
        setShowCustomDays(false);
      } else {
        setDays("custom");
        setCustomDays(daysValue.split(","));
        setShowCustomDays(true);
      }
    }
  }, [existingAlarm]);

  const handleDaysChange = (value: string) => {
    setDays(value);
    setShowCustomDays(value === "custom");
    if (value !== "custom") {
      setCustomDays([]);
    }
  };

  const toggleCustomDay = (day: string) => {
    setCustomDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
  };

  const validateForm = (): boolean => {
    const finalDays = days === "custom" ? customDays.join(",") : days;

    const result = alarmFormSchema.safeParse({
      name: name || undefined,
      hour12,
      ampm,
      minute,
      second,
      clockId,
      days: finalDays,
      duration,
    });

    if (!result.success) {
      const newErrors: FormErrors = {};
      const issues = result.error.issues;
      for (const issue of issues) {
        const field = issue.path[0] as keyof AlarmFormData;
        newErrors[field] = issue.message;
      }
      setErrors(newErrors);
      return false;
    }

    setErrors({});
    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const finalDays = days === "custom" ? customDays.join(",") : days;
    const hour24 = to24Hour(hour12, ampm);

    const alarmData: AlarmCreate = {
      name:
        name ||
        `Alarm ${hour12.toString().padStart(2, "0")}:${minute
          .toString()
          .padStart(2, "0")} ${ampm}`,
      hour: hour24,
      minute,
      second,
      clock_id: clockId,
      days: finalDays,
      duration,
      enabled: true,
    };

    if (isEditing) {
      updateAlarm.mutate(
        { id: alarmId!, alarm: alarmData },
        { onSuccess: () => navigate({ to: "/alarms" }) }
      );
    } else {
      createAlarm.mutate(alarmData, {
        onSuccess: () => navigate({ to: "/alarms" }),
      });
    }
  };

  if (isEditing && isLoading) {
    return <div className="loading">Loading alarm...</div>;
  }

  return (
    <div className="alarm-edit-page">
      <h2>{isEditing ? "Edit Alarm" : "New Alarm"}</h2>

      <form onSubmit={handleSubmit} className="alarm-form">
        {/* Time Picker */}
        <div
          className={`form-group time-picker ${
            errors.hour12 || errors.minute || errors.second ? "has-error" : ""
          }`}
        >
          <label>Time</label>
          {isMobile ? (
            <div className="time-inputs-mobile">
              <input
                type="time"
                step="1"
                value={getNativeTimeValue()}
                onChange={(e) => handleNativeTimeChange(e.target.value)}
                className={`time-input-native ${
                  errors.hour12 || errors.minute || errors.second
                    ? "input-error"
                    : ""
                }`}
              />
            </div>
          ) : (
            <div className="time-inputs">
              <input
                type="number"
                min={1}
                max={12}
                value={hour12}
                onChange={(e) => {
                  let val = parseInt(e.target.value) || 1;
                  if (val < 1) val = 1;
                  if (val > 12) val = 12;
                  setHour12(val);
                  setErrors((prev) => ({ ...prev, hour12: undefined }));
                }}
                className={`time-input ${errors.hour12 ? "input-error" : ""}`}
              />
              <span className="time-separator">:</span>
              <input
                type="number"
                min={0}
                max={59}
                value={minute.toString().padStart(2, "0")}
                onChange={(e) => {
                  setMinute(parseInt(e.target.value) || 0);
                  setErrors((prev) => ({ ...prev, minute: undefined }));
                }}
                className={`time-input ${errors.minute ? "input-error" : ""}`}
              />
              <span className="time-separator">:</span>
              <input
                type="number"
                min={0}
                max={59}
                value={second.toString().padStart(2, "0")}
                onChange={(e) => {
                  setSecond(parseInt(e.target.value) || 0);
                  setErrors((prev) => ({ ...prev, second: undefined }));
                }}
                className={`time-input time-input-sm ${
                  errors.second ? "input-error" : ""
                }`}
              />
              <select
                value={ampm}
                onChange={(e) => setAmpm(e.target.value as "AM" | "PM")}
                className="ampm-select"
              >
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          )}
          {(errors.hour12 || errors.minute || errors.second) && (
            <span className="form-error">
              {errors.hour12 || errors.minute || errors.second}
            </span>
          )}
        </div>

        {/* Name */}
        <div className={`form-group ${errors.name ? "has-error" : ""}`}>
          <label htmlFor="name">Name (optional)</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setErrors((prev) => ({ ...prev, name: undefined }));
            }}
            placeholder="Wake up, Meeting, etc."
            className={`form-input ${errors.name ? "input-error" : ""}`}
            maxLength={100}
          />
          {errors.name && <span className="form-error">{errors.name}</span>}
        </div>

        {/* Clock Selection */}
        <div className="form-group">
          <label>Clock</label>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                name="clockId"
                value={1}
                checked={clockId === 1}
                onChange={() => setClockId(1)}
              />
              Clock 1
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="clockId"
                value={2}
                checked={clockId === 2}
                onChange={() => setClockId(2)}
              />
              Clock 2
            </label>
          </div>
        </div>

        {/* Days */}
        <div className={`form-group ${errors.days ? "has-error" : ""}`}>
          <label htmlFor="days">Repeat</label>
          <select
            id="days"
            value={days}
            onChange={(e) => {
              handleDaysChange(e.target.value);
              setErrors((prev) => ({ ...prev, days: undefined }));
            }}
            className={`form-select ${errors.days ? "input-error" : ""}`}
          >
            {DAYS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {errors.days && <span className="form-error">{errors.days}</span>}
        </div>

        {/* Custom Days */}
        {showCustomDays && (
          <div className="form-group">
            <label>Select days</label>
            <div className="days-picker">
              {DAY_NAMES.map((day, i) => (
                <button
                  key={day}
                  type="button"
                  className={`day-btn ${
                    customDays.includes(day) ? "active" : ""
                  }`}
                  onClick={() => {
                    toggleCustomDay(day);
                    setErrors((prev) => ({ ...prev, days: undefined }));
                  }}
                >
                  {DAY_LABELS[i]}
                </button>
              ))}
            </div>
            {customDays.length === 0 && (
              <span className="form-hint">Select at least one day</span>
            )}
          </div>
        )}

        {/* Duration */}
        <div className={`form-group ${errors.duration ? "has-error" : ""}`}>
          <label htmlFor="duration">Duration (seconds)</label>
          <input
            type="number"
            id="duration"
            min={0}
            max={3600}
            value={duration}
            onChange={(e) => {
              setDuration(parseInt(e.target.value) || 0);
              setErrors((prev) => ({ ...prev, duration: undefined }));
            }}
            className={`form-input ${errors.duration ? "input-error" : ""}`}
          />
          {errors.duration ? (
            <span className="form-error">{errors.duration}</span>
          ) : (
            <small className="form-hint">0 = ring until manually stopped</small>
          )}
        </div>

        {/* Actions */}
        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate({ to: "/alarms" })}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={createAlarm.isPending || updateAlarm.isPending}
          >
            {isEditing ? "Save" : "Create"}
          </button>
        </div>
      </form>
    </div>
  );
}
