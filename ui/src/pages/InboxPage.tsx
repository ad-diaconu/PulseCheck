import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../services/api";
import { useWorkspace } from "../context/useWorkspace";
import type { InvitationWithContext } from "../types/invitation";
import InvitationRow from "../components/InvitationRow";

const InboxPage = () => {
  const { refetchWorkspaces } = useWorkspace();
  const [invitations, setInvitations] = useState<InvitationWithContext[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [respondingId, setRespondingId] = useState<string | null>(null);

  useEffect(() => {
    const fetchInvitations = async () => {
      try {
        const response = await api.get<InvitationWithContext[]>("/invitations");
        setInvitations(response.data);
      } catch {
        toast.error("Failed to load invitations");
      } finally {
        setIsLoading(false);
      }
    };

    fetchInvitations();
  }, []);

  const handleAccept = async (invitationId: string) => {
    setRespondingId(invitationId);
    try {
      await api.post(`/invitations/${invitationId}/accept`);
      setInvitations((prev) => prev.filter((inv) => inv.id !== invitationId));
      // The backend just added this user to a new workspace. WorkspaceContext
      // only fetches /workspaces once on mount, so without this it has no
      // way to know — the new workspace wouldn't show up until a full page
      // reload remounted the provider. refetchWorkspaces() re-pulls the
      // list right now, into the same context every other page reads from.
      await refetchWorkspaces();
      toast.success("Invitation accepted");
    } catch {
      toast.error("Failed to accept invitation");
    } finally {
      setRespondingId(null);
    }
  };

  const handleDecline = async (invitationId: string) => {
    setRespondingId(invitationId);
    try {
      await api.post(`/invitations/${invitationId}/decline`);
      setInvitations((prev) => prev.filter((inv) => inv.id !== invitationId));
      toast.success("Invitation declined");
    } catch {
      toast.error("Failed to decline invitation");
    } finally {
      setRespondingId(null);
    }
  };

  return (
    <div className="max-w-3xl px-8 py-10">
      <h1 className="text-2xl font-semibold text-slate-900">Inbox</h1>
      <p className="text-sm text-slate-500 mt-1">
        Workspace invitations waiting for your response.
      </p>

      <div className="mt-8">
        {isLoading ? (
          <p className="text-sm text-slate-500">Loading...</p>
        ) : invitations.length === 0 ? (
          <p className="text-sm text-slate-500">
            You have no pending invitations.
          </p>
        ) : (
          <div className="border border-slate-200 rounded-xl divide-y divide-slate-100 bg-white">
            {invitations.map((invitation) => (
              <InvitationRow
                key={invitation.id}
                invitation={invitation}
                isResponding={respondingId === invitation.id}
                onAccept={() => handleAccept(invitation.id)}
                onDecline={() => handleDecline(invitation.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default InboxPage;
