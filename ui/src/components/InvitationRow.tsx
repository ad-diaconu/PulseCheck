import { Check, X } from "lucide-react";
import type { InvitationWithContext } from "../types/invitation";

type InvitationRowProps = {
  invitation: InvitationWithContext;
  isResponding: boolean;
  onAccept: () => void;
  onDecline: () => void;
};

const InvitationRow = ({
  invitation,
  isResponding,
  onAccept,
  onDecline,
}: InvitationRowProps) => {
  return (
    <div className="flex items-center gap-4 px-5 py-4">
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-slate-900 truncate">
          {invitation.workspace_name}
        </p>
        <p className="text-xs text-slate-500 truncate">
          Invited by {invitation.invited_by_email} · {invitation.role}
        </p>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          type="button"
          onClick={onDecline}
          disabled={isResponding}
          className="p-1.5 rounded-md text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Decline invitation"
        >
          <X className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={onAccept}
          disabled={isResponding}
          className="p-1.5 rounded-md text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Accept invitation"
        >
          <Check className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default InvitationRow;
