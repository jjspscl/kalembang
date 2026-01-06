import {
  isDemo,
  demoStatusApi,
  demoClockApi,
  demoStopApi,
  demoAlarmApi,
} from "./demo";

const API_BASE = import.meta.env.VITE_API_BASE || "";

export interface ClockStatus {
  enabled: boolean;
  duty: number;
}

export interface Status {
  clock1: ClockStatus;
  clock2: ClockStatus;
  stop_button_pressed: boolean | null;
  current_time: string;
}

export interface ApiResponse {
  message: string;
  success: boolean;
}

export interface Alarm {
  id: number | null;
  name: string;
  hour: number;
  minute: number;
  second: number;
  clock_id: number;
  enabled: boolean;
  days: string;
  duration: number;
  created_at?: string;
  last_triggered?: string;
}

export interface AlarmCreate {
  name: string;
  hour: number;
  minute: number;
  second?: number;
  clock_id?: number;
  enabled?: boolean;
  days?: string;
  duration?: number;
}

export interface ServerTime {
  timestamp: string;
  hour: number;
  minute: number;
  second: number;
  day_of_week: string;
}

export class ApiError extends Error {
  constructor(message: string, public status: number, public detail?: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const errorData = await response.json();
      detail = errorData.detail;
    } catch {}
    throw new ApiError(
      `API request failed: ${response.status}`,
      response.status,
      detail
    );
  }

  return response.json();
}

const realStatusApi = {
  get: () => request<Status>("/api/v1/status"),
  getTime: () => request<ServerTime>("/api/v1/time"),
};

export const statusApi = isDemo ? demoStatusApi : realStatusApi;

const realClockApi = {
  clock1: {
    on: () => request<ApiResponse>("/api/v1/clock/1/on", { method: "POST" }),
    off: () => request<ApiResponse>("/api/v1/clock/1/off", { method: "POST" }),
    setDuty: (duty: number) =>
      request<ApiResponse>("/api/v1/clock/1/duty", {
        method: "POST",
        body: JSON.stringify({ duty }),
      }),
  },
  clock2: {
    on: () => request<ApiResponse>("/api/v1/clock/2/on", { method: "POST" }),
    off: () => request<ApiResponse>("/api/v1/clock/2/off", { method: "POST" }),
    setDuty: (duty: number) =>
      request<ApiResponse>("/api/v1/clock/2/duty", {
        method: "POST",
        body: JSON.stringify({ duty }),
      }),
  },
  allOff: () =>
    request<ApiResponse>("/api/v1/clock/all/off", { method: "POST" }),
};

export const clockApi = isDemo ? demoClockApi : realClockApi;

const realStopApi = {
  trigger: () =>
    request<ApiResponse>("/api/v1/stop/trigger", { method: "POST" }),
};

export const stopApi = isDemo ? demoStopApi : realStopApi;

const realAlarmApi = {
  list: () => request<Alarm[]>("/api/v1/alarms"),
  get: (id: number) => request<Alarm>(`/api/v1/alarms/${id}`),
  create: (alarm: AlarmCreate) =>
    request<Alarm>("/api/v1/alarms", {
      method: "POST",
      body: JSON.stringify(alarm),
    }),
  update: (id: number, alarm: AlarmCreate) =>
    request<Alarm>(`/api/v1/alarms/${id}`, {
      method: "PUT",
      body: JSON.stringify(alarm),
    }),
  delete: (id: number) =>
    request<ApiResponse>(`/api/v1/alarms/${id}`, { method: "DELETE" }),
  toggle: (id: number, enabled: boolean) =>
    request<Alarm>(`/api/v1/alarms/${id}/toggle?enabled=${enabled}`, {
      method: "PATCH",
    }),
};

export const alarmApi = isDemo ? demoAlarmApi : realAlarmApi;
export { isDemo };
