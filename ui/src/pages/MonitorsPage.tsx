import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { api } from "../services/api";
import { useWorkspace } from "../context/useWorkspace";
import type { Monitor } from "../types/monitor";
import type { PingHistoryEntry } from "../types/pingHistory";
import MonitorRow from "../components/MonitorRow";
import AddMonitorModal from "../components/AddMonitorModal";
import EditMonitorModal from "../components/EditMonitorModal";

const MonitorsPage = () => {
  const { currentWorkspace, isLoading: isWorkspaceLoading } = useWorkspace();
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingMonitor, setEditingMonitor] = useState<Monitor | null>(null);
  // Keyed by monitor id -> latest latency in ms, or null if never pinged yet.
  // Separate from `monitors` state on purpose: latency comes from a
  // different endpoint (/monitors/{id}/pings) than the monitor list itself.
  const [latencyByMonitorId, setLatencyByMonitorId] = useState<
    Record<string, number | null>
  >({});

  const [trackedWorkspaceId, setTrackedWorkspaceId] = useState<
    string | undefined
  >(currentWorkspace?.id);
  if (currentWorkspace?.id !== trackedWorkspaceId) {
    setTrackedWorkspaceId(currentWorkspace?.id);
    setIsLoading(true);
  }

  useEffect(() => {
    if (!currentWorkspace) {
      return;
    }
    let isFirstFetch = true;

    // Fetches the single most recent ping for one monitor and returns its
    // latency, or null if the monitor has no pings yet (e.g. just created,
    // celery hasn't run its first check). limit=1 + default sort (date desc)
    // means pings[0], if present, is always the latest one.
    const fetchLatestLatency = async (
      monitorId: string,
    ): Promise<number | null> => {
      try {
        const response = await api.get<{ pings: PingHistoryEntry[] }>(
          `/monitors/${monitorId}/pings`,
          { params: { limit: 1 } },
        );
        return response.data.pings[0]?.latency_ms ?? null;
      } catch {
        // A single monitor's latency failing to load shouldn't break the
        // whole page — just show "—" for that one, silently.
        return null;
      }
    };

    const fetchMonitors = async () => {
      try {
        const response = await api.get<{ monitors: Monitor[] }>(
          `/workspaces/${currentWorkspace.id}/monitors`,
        );
        setMonitors(response.data.monitors);

        // One /pings request per monitor, fired in parallel (Promise.all)
        // rather than awaited one by one — otherwise 10 monitors would
        // mean 10x the wait, sequentially, for no reason.
        const fetchedMonitors = response.data.monitors;
        const latencies = await Promise.all(
          fetchedMonitors.map((monitor) => fetchLatestLatency(monitor.id)),
        );
        const latencyMap: Record<string, number | null> = {};
        fetchedMonitors.forEach((monitor, index) => {
          latencyMap[monitor.id] = latencies[index];
        });
        setLatencyByMonitorId(latencyMap);
      } catch {
        if (isFirstFetch) {
          toast.error("Failed to load monitors");
        }
      } finally {
        if (isFirstFetch) {
          setIsLoading(false);
          isFirstFetch = false;
        }
      }
    };

    fetchMonitors();

    const intervalId = setInterval(fetchMonitors, 10000);
    return () => clearInterval(intervalId);
  }, [currentWorkspace]);

  const handleCreateMonitor = async (
    name: string,
    url: string,
    intervalMinutes: number,
  ) => {
    if (!currentWorkspace) return;

    try {
      const response = await api.post<Monitor>(
        `/workspaces/${currentWorkspace.id}/monitors`,
        { name, url, interval_minutes: intervalMinutes },
      );
      setMonitors((prev) => [...prev, response.data]);
      setIsModalOpen(false);
      toast.success("Monitor created");
    } catch {
      toast.error("Failed to create monitor");
    }
  };

  const handleSaveMonitor = async (
    name: string,
    url: string,
    intervalMinutes: number,
  ) => {
    if (!editingMonitor) return;

    try {
      const response = await api.patch<Monitor>(
        `/monitors/${editingMonitor.id}`,
        { name, url, interval_minutes: intervalMinutes },
      );
      // Replace just the one monitor that changed, keep the rest as-is —
      // same immutable-update pattern as handleCreateMonitor's append.
      setMonitors((prev) =>
        prev.map((m) => (m.id === response.data.id ? response.data : m)),
      );
      setEditingMonitor(null);
      toast.success("Monitor updated");
    } catch {
      toast.error("Failed to update monitor");
    }
  };

  const handleDeleteMonitor = async (monitor: Monitor) => {
    // Native confirm() — a destructive action still needs explicit
    // confirmation per the UX guidelines, and a custom modal would be
    // overkill for this single use case right now.
    const confirmed = window.confirm(
      `Delete "${monitor.name}"? This cannot be undone.`,
    );
    if (!confirmed) return;

    try {
      await api.delete(`/monitors/${monitor.id}`);
      setMonitors((prev) => prev.filter((m) => m.id !== monitor.id));
      toast.success("Monitor deleted");
    } catch {
      toast.error("Failed to delete monitor");
    }
  };

  const downCount = monitors.filter((m) => m.status === "down").length;

  if (isWorkspaceLoading) {
    return (
      <div className="max-w-5xl px-8 py-10">
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    );
  }

  if (!currentWorkspace) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-theme(spacing.11))] px-8 py-10">
        <div className="w-full max-w-sm text-center">
          <h1 className="text-2xl font-semibold text-slate-900">
            No workspace yet
          </h1>
          <p className="text-sm text-slate-500 mt-1 mb-4">
            You'll need a workspace before you can add monitors.
          </p>
          <Link
            to="/dashboard/workspaces"
            className="inline-flex items-center px-3.5 py-2 text-sm font-medium rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors"
          >
            Go to Workspaces
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-5xl px-8 py-10">
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Monitors</h1>
          <p className="text-sm text-slate-500 mt-1">
            {monitors.length} monitors
            {downCount > 0 && (
              <span className="text-red-600"> · {downCount} down</span>
            )}
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsModalOpen(true)}
          className="cursor-pointer flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Monitor
        </button>
      </div>

      {monitors.length === 0 ? (
        <div className="border border-slate-200 rounded-xl bg-white px-5 py-10 text-center">
          <p className="text-sm text-slate-500">
            No monitors yet. Add your first one to start tracking uptime.
          </p>
        </div>
      ) : (
        <div className="border border-slate-200 rounded-xl divide-y divide-slate-100 bg-white">
          {monitors.map((monitor) => (
            <MonitorRow
              key={monitor.id}
              monitor={monitor}
              latencyMs={latencyByMonitorId[monitor.id] ?? null}
              onEdit={setEditingMonitor}
              onDelete={handleDeleteMonitor}
            />
          ))}
        </div>
      )}

      {isModalOpen && (
        <AddMonitorModal
          onCreate={handleCreateMonitor}
          onClose={() => setIsModalOpen(false)}
        />
      )}

      {editingMonitor && (
        <EditMonitorModal
          monitor={editingMonitor}
          onSave={handleSaveMonitor}
          onClose={() => setEditingMonitor(null)}
        />
      )}
    </div>
  );
};

export default MonitorsPage;
