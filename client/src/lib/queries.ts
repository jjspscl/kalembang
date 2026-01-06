import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";
import {
  statusApi,
  clockApi,
  stopApi,
  alarmApi,
  type Status,
  type Alarm,
  type AlarmCreate,
  type ServerTime,
} from "./api";

export const queryKeys = {
  status: ["status"] as const,
  time: ["time"] as const,
  alarms: ["alarms"] as const,
  alarm: (id: number) => ["alarms", id] as const,
};

export function useStatus(
  options?: Omit<UseQueryOptions<Status>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.status,
    queryFn: statusApi.get,
    refetchInterval: 2000,
    ...options,
  });
}

export function useServerTime(
  options?: Omit<UseQueryOptions<ServerTime>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.time,
    queryFn: statusApi.getTime,
    refetchInterval: 1000,
    ...options,
  });
}

export function useClockOn(clockId: 1 | 2) {
  const queryClient = useQueryClient();
  const clockFn = clockId === 1 ? clockApi.clock1.on : clockApi.clock2.on;

  return useMutation({
    mutationFn: clockFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.status });
    },
  });
}

export function useClockOff(clockId: 1 | 2) {
  const queryClient = useQueryClient();
  const clockFn = clockId === 1 ? clockApi.clock1.off : clockApi.clock2.off;

  return useMutation({
    mutationFn: clockFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.status });
    },
  });
}

export function useClockDuty(clockId: 1 | 2) {
  const queryClient = useQueryClient();
  const clockFn =
    clockId === 1 ? clockApi.clock1.setDuty : clockApi.clock2.setDuty;

  return useMutation({
    mutationFn: clockFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.status });
    },
  });
}

export function useAllOff() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: clockApi.allOff,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.status });
    },
  });
}

export function useStopTrigger() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: stopApi.trigger,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.status });
    },
  });
}

export function useAlarms(
  options?: Omit<UseQueryOptions<Alarm[]>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.alarms,
    queryFn: alarmApi.list,
    ...options,
  });
}

export function useAlarm(
  id: number,
  options?: Omit<UseQueryOptions<Alarm>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.alarm(id),
    queryFn: () => alarmApi.get(id),
    ...options,
  });
}

export function useCreateAlarm() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alarm: AlarmCreate) => alarmApi.create(alarm),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alarms });
    },
  });
}

export function useUpdateAlarm() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, alarm }: { id: number; alarm: AlarmCreate }) =>
      alarmApi.update(id, alarm),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alarms });
      queryClient.invalidateQueries({ queryKey: queryKeys.alarm(id) });
    },
  });
}

export function useDeleteAlarm() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => alarmApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alarms });
    },
  });
}

export function useToggleAlarm() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, enabled }: { id: number; enabled: boolean }) =>
      alarmApi.toggle(id, enabled),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alarms });
      queryClient.invalidateQueries({ queryKey: queryKeys.alarm(id) });
    },
  });
}
