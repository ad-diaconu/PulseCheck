import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { toast } from "sonner";
import { ArrowLeft, ShieldOff, Clock } from "lucide-react";
import { api } from "../services/api";
import { ApiError } from "../utils/errors";
import type { Member } from "../types/member";
import type { InvitationWithEmail } from "../types/invitation";
import InviteMemberForm from "../components/InviteMemberForm";

const fetchPendingInvitations = (workspaceId: string) =>
  api.get<InvitationWithEmail[]>(`/workspaces/${workspaceId}/invitations`);

const WorkspaceDetailPage = () => {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [members, setMembers] = useState<Member[]>([]);
  const [pendingInvitations, setPendingInvitations] = useState<
    InvitationWithEmail[]
  >([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [accessDenied, setAccessDenied] = useState<boolean>(false);

  useEffect(() => {
    if (!workspaceId) return;

    const loadMembers = async () => {
      try {
        const response = await api.get<Member[]>(
          `/workspaces/${workspaceId}/members`,
        );
        setMembers(response.data);
      } catch (error) {
        if (
          error instanceof ApiError &&
          [400, 403, 404, 422].includes(error.status)
        ) {
          setAccessDenied(true);
        } else {
          toast.error("Failed to load members");
        }
      } finally {
        setIsLoading(false);
      }
    };

    const loadPendingInvitations = async () => {
      try {
        const response = await fetchPendingInvitations(workspaceId);
        setPendingInvitations(response.data);
      } catch {
        setPendingInvitations([]);
      }
    };

    loadMembers();
    loadPendingInvitations();
  }, [workspaceId]);

  const handleInvite = async (email: string, role: string) => {
    if (!workspaceId) return;
    try {
      await api.post(`/workspaces/${workspaceId}/invitations`, {
        email,
        role,
      });
      toast.success("Invitation sent");
      try {
        const response = await fetchPendingInvitations(workspaceId);
        setPendingInvitations(response.data);
      } catch {
        // list refresh is best-effort — the invite itself already succeeded
      }
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error(error.message);
      } else {
        toast.error("Failed to send invitation");
      }
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl px-8 py-10">
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    );
  }

  if (accessDenied) {
    return (
      <div className="flex flex-col min-h-[calc(100vh-theme(spacing.11))] px-8 py-10">
        <Link
          to="/dashboard/workspaces"
          className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft className="size-4" />
          Back to Workspaces
        </Link>

        <div className="flex-1 flex items-center justify-center">
          <div className="w-full max-w-sm text-center">
            <ShieldOff className="size-8 text-slate-300 mx-auto mb-3" />
            <p className="text-sm font-medium text-slate-900">
              You don't have access to this workspace
            </p>
            <p className="text-sm text-slate-500 mt-1">
              Ask a workspace admin to invite you, or go back to your own
              workspaces.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl px-8 py-10">
      <Link
        to="/dashboard/workspaces"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900 mb-6"
      >
        <ArrowLeft className="size-4" />
        Back to Workspaces
      </Link>

      <h1 className="text-2xl font-semibold text-slate-900 mb-8">Members</h1>

      <div className="border border-slate-200 rounded-xl bg-white p-6 mb-8">
        <p className="text-sm font-medium text-slate-900 mb-3">
          Invite a member
        </p>
        <InviteMemberForm onInvite={handleInvite} />
      </div>

      {members.length === 0 ? (
        <div className="border border-slate-200 rounded-xl bg-white px-5 py-10 text-center">
          <p className="text-sm text-slate-500">No members yet.</p>
        </div>
      ) : (
        <div className="border border-slate-200 rounded-xl divide-y divide-slate-100 bg-white">
          {members.map((member) => (
            <div
              key={member.user_id}
              className="flex items-center justify-between px-5 py-4"
            >
              <p className="text-sm font-medium text-slate-900">
                {member.email}
              </p>
              <p className="text-xs text-slate-500">{member.role}</p>
            </div>
          ))}
        </div>
      )}

      {pendingInvitations.length > 0 && (
        <div className="mt-6">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">
            Pending invitations
          </p>
          <div className="border border-slate-200 rounded-xl divide-y divide-slate-100 bg-white">
            {pendingInvitations.map((invitation) => (
              <div
                key={invitation.id}
                className="flex items-center justify-between px-5 py-4"
              >
                <div className="flex items-center gap-2">
                  <Clock className="size-4 text-slate-400" />
                  <p className="text-sm font-medium text-slate-700">
                    {invitation.invited_email}
                  </p>
                </div>
                <span className="text-xs font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded-md">
                  {invitation.role} · Pending
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkspaceDetailPage;
