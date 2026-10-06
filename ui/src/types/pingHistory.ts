export type PingHistoryEntry = {
  id: number;
  monitor_id: string;
  pinged_at: string;
  status_code: number;
  latency_ms: number;
};
