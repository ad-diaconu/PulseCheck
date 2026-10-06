import { useState, type FormEvent } from "react";
import { X } from "lucide-react";
import type { Monitor } from "../types/monitor";

type EditMonitorModalProps = {
  monitor: Monitor;
  onSave: (
    name: string,
    url: string,
    intervalMinutes: number,
  ) => Promise<void>;
  onClose: () => void;
};

const EditMonitorModal = ({ monitor, onSave, onClose }: EditMonitorModalProps) => {
  // Pre-populated from the monitor being edited, not blank like AddMonitorModal.
  const [name, setName] = useState<string>(monitor.name);
  const [url, setUrl] = useState<string>(monitor.url);
  const [intervalMinutes, setIntervalMinutes] = useState<string>(
    String(monitor.interval_minutes),
  );
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !url.trim()) return;

    setIsSubmitting(true);
    try {
      await onSave(name.trim(), url.trim(), Number(intervalMinutes));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-slate-900">
            Edit Monitor
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X className="size-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="edit-name" className="text-sm font-medium text-slate-700">
              Name
            </label>
            <input
              id="edit-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="edit-url" className="text-sm font-medium text-slate-700">
              URL
            </label>
            <input
              id="edit-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="edit-interval" className="text-sm font-medium text-slate-700">
              Check interval
            </label>
            <select
              id="edit-interval"
              value={intervalMinutes}
              onChange={(e) => setIntervalMinutes(e.target.value)}
              className="px-3 py-2 text-sm border border-slate-300 rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-slate-900"
            >
              <option value="1">Every 1 minute</option>
              <option value="5">Every 5 minutes</option>
              <option value="15">Every 15 minutes</option>
              <option value="30">Every 30 minutes</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-2 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 text-sm font-medium rounded-lg text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !name.trim() || !url.trim()}
              className="px-3.5 py-2 text-sm font-medium rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditMonitorModal;
