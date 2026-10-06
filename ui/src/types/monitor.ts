export type MonitorStatus = "pending" | "up" | "down" | "paused" | "degraded";

export type Monitor = {
  id: string;
  workspace_id: string;
  name: string;
  url: string;
  status: MonitorStatus;
  interval_minutes: number;
  created_at: string;
  updated_at: string;
};
