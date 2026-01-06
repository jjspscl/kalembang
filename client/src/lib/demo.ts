
import type {
  Status,
  ServerTime,
  ApiResponse,
  Alarm,
  AlarmCreate,
} from "./api";

interface DemoState {
  clock1: { enabled: boolean; duty: number };
  clock2: { enabled: boolean; duty: number };
  alarms: Alarm[];
  nextAlarmId: number;
}

const demoState: DemoState = {
  clock1: { enabled: false, duty: 50 },
  clock2: { enabled: false, duty: 50 },
  alarms: [
    {
      id: 1,
      name: "Morning Wake Up",
      hour: 7,
      minute: 0,
      second: 0,
      clock_id: 1,
      enabled: true,
      days: "weekdays",
      duration: 60,
      created_at: "2026-01-01T00:00:00Z",
      last_triggered: undefined,
    },
    {
      id: 2,
      name: "Weekend Alarm",
      hour: 9,
      minute: 30,
      second: 0,
      clock_id: 2,
      enabled: true,
      days: "weekends",
      duration: 120,
      created_at: "2026-01-01T00:00:00Z",
      last_triggered: undefined,
    },
    {
      id: 3,
      name: "Daily Reminder",
      hour: 12,
      minute: 0,
      second: 0,
      clock_id: 1,
      enabled: false,
      days: "everyday",
      duration: 30,
      created_at: "2026-01-02T00:00:00Z",
      last_triggered: "2026-01-03T12:00:00Z",
    },
  ],
  nextAlarmId: 4,
};

function delay(ms: number = 100): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function success(message: string): ApiResponse {
  return { message, success: true };
}

export const demoStatusApi = {
  get: async (): Promise<Status> => {
    await delay(50);
    return {
      clock1: demoState.clock1,
      clock2: demoState.clock2,
      stop_button_pressed: false,
      current_time: new Date().toISOString(),
    };
  },

  getTime: async (): Promise<ServerTime> => {
    await delay(20);
    const now = new Date();
    const days = [
      "Sunday",
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
    ];
    return {
      timestamp: now.toISOString(),
      hour: now.getHours(),
      minute: now.getMinutes(),
      second: now.getSeconds(),
      day_of_week: days[now.getDay()],
    };
  },
};

export const demoClockApi = {
  clock1: {
    on: async (): Promise<ApiResponse> => {
      await delay();
      demoState.clock1.enabled = true;
      return success("Clock 1 turned ON");
    },
    off: async (): Promise<ApiResponse> => {
      await delay();
      demoState.clock1.enabled = false;
      return success("Clock 1 turned OFF");
    },
    setDuty: async (duty: number): Promise<ApiResponse> => {
      await delay();
      demoState.clock1.duty = Math.max(0, Math.min(100, duty));
      return success(`Clock 1 duty set to ${demoState.clock1.duty}%`);
    },
  },
  clock2: {
    on: async (): Promise<ApiResponse> => {
      await delay();
      demoState.clock2.enabled = true;
      return success("Clock 2 turned ON");
    },
    off: async (): Promise<ApiResponse> => {
      await delay();
      demoState.clock2.enabled = false;
      return success("Clock 2 turned OFF");
    },
    setDuty: async (duty: number): Promise<ApiResponse> => {
      await delay();
      demoState.clock2.duty = Math.max(0, Math.min(100, duty));
      return success(`Clock 2 duty set to ${demoState.clock2.duty}%`);
    },
  },
  allOff: async (): Promise<ApiResponse> => {
    await delay();
    demoState.clock1.enabled = false;
    demoState.clock2.enabled = false;
    return success("All clocks turned OFF");
  },
};

export const demoStopApi = {
  trigger: async (): Promise<ApiResponse> => {
    await delay();
    demoState.clock1.enabled = false;
    demoState.clock2.enabled = false;
    return success("Stop triggered - all clocks stopped");
  },
};

export const demoAlarmApi = {
  list: async (): Promise<Alarm[]> => {
    await delay(100);
    return [...demoState.alarms].sort((a, b) => {

      const timeA = a.hour * 3600 + a.minute * 60 + a.second;
      const timeB = b.hour * 3600 + b.minute * 60 + b.second;
      return timeA - timeB;
    });
  },

  get: async (id: number): Promise<Alarm> => {
    await delay(50);
    const alarm = demoState.alarms.find((a) => a.id === id);
    if (!alarm) {
      throw new Error(`Alarm ${id} not found`);
    }
    return { ...alarm };
  },

  create: async (data: AlarmCreate): Promise<Alarm> => {
    await delay(150);
    const newAlarm: Alarm = {
      id: demoState.nextAlarmId++,
      name: data.name,
      hour: data.hour,
      minute: data.minute,
      second: data.second ?? 0,
      clock_id: data.clock_id ?? 1,
      enabled: data.enabled ?? true,
      days: data.days ?? "everyday",
      duration: data.duration ?? 60,
      created_at: new Date().toISOString(),
      last_triggered: undefined,
    };
    demoState.alarms.push(newAlarm);
    return { ...newAlarm };
  },

  update: async (id: number, data: AlarmCreate): Promise<Alarm> => {
    await delay(150);
    const index = demoState.alarms.findIndex((a) => a.id === id);
    if (index === -1) {
      throw new Error(`Alarm ${id} not found`);
    }
    const updated: Alarm = {
      ...demoState.alarms[index],
      name: data.name,
      hour: data.hour,
      minute: data.minute,
      second: data.second ?? demoState.alarms[index].second,
      clock_id: data.clock_id ?? demoState.alarms[index].clock_id,
      enabled: data.enabled ?? demoState.alarms[index].enabled,
      days: data.days ?? demoState.alarms[index].days,
      duration: data.duration ?? demoState.alarms[index].duration,
    };
    demoState.alarms[index] = updated;
    return { ...updated };
  },

  delete: async (id: number): Promise<ApiResponse> => {
    await delay(100);
    const index = demoState.alarms.findIndex((a) => a.id === id);
    if (index === -1) {
      throw new Error(`Alarm ${id} not found`);
    }
    demoState.alarms.splice(index, 1);
    return success(`Alarm ${id} deleted`);
  },

  toggle: async (id: number, enabled: boolean): Promise<Alarm> => {
    await delay(100);
    const index = demoState.alarms.findIndex((a) => a.id === id);
    if (index === -1) {
      throw new Error(`Alarm ${id} not found`);
    }
    demoState.alarms[index].enabled = enabled;
    return { ...demoState.alarms[index] };
  },
};

export const isDemo = import.meta.env.VITE_DEMO_MODE === "true";

export function getApi<T>(realApi: T, demoApi: T): T {
  return isDemo ? demoApi : realApi;
}
