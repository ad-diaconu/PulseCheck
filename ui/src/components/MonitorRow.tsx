import { useEffect, useRef, useState } from "react";
import { MoreVertical, Pencil, Trash2 } from "lucide-react";
import type { Monitor, MonitorStatus } from "../types/monitor";

type MonitorRowProps = {
  monitor: Monitor;
  latencyMs: number | null;
  onEdit: (monitor: Monitor) => void;
  onDelete: (monitor: Monitor) => void;
};

const STATUS_STYLES: Record<MonitorStatus, { dot: string; label: string }> = {
  up: { dot: "bg-emerald-500", label: "Operational" },
  down: { dot: "bg-red-500", label: "Down" },
  degraded: { dot: "bg-amber-500", label: "Degraded" },
  paused: { dot: "bg-slate-300", label: "Paused" },
  pending: { dot: "bg-slate-300", label: "Pending" },
};

const MonitorRow = ({ monitor, latencyMs, onEdit, onDelete }: MonitorRowProps) => {
  const statusStyle = STATUS_STYLES[monitor.status];
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Same click-outside-to-close pattern as UserMenu.tsx: a ref on the
  // wrapping div, a mousedown listener on the document, close if the
  // click landed outside the ref'd element.
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="flex items-center gap-4 px-5 py-4 hover:bg-slate-50 transition-colors">
      <span
        className={`h-2.5 w-2.5 rounded-full shrink-0 ${statusStyle.dot}`}
        title={statusStyle.label}
      />

      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-slate-900 truncate">
          {monitor.name}
        </p>
        <p className="text-sm text-slate-500 truncate">{monitor.url}</p>
      </div>

      <div className="text-right shrink-0">
        <p className="text-sm font-medium text-slate-700">
          {latencyMs !== null ? `${latencyMs}ms` : "—"}
        </p>
        <p className="text-xs text-slate-400">every {monitor.interval_minutes}m</p>
      </div>

      <div className="relative shrink-0" ref={menuRef}>
        <button
          type="button"
          onClick={() => setIsMenuOpen((prev) => !prev)}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
          aria-label="Monitor actions"
        >
          <MoreVertical className="w-4 h-4" />
        </button>

        {isMenuOpen && (
          <div className="absolute right-0 top-full mt-1 w-36 bg-white border border-slate-200 rounded-lg shadow-lg py-1 z-10">
            <button
              type="button"
              onClick={() => {
                setIsMenuOpen(false);
                onEdit(monitor);
              }}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer"
            >
              <Pencil className="w-3.5 h-3.5" />
              Edit
            </button>
            <button
              type="button"
              onClick={() => {
                setIsMenuOpen(false);
                onDelete(monitor);
              }}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MonitorRow;
