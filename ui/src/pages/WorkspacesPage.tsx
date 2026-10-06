import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { api } from "../services/api";
import { useWorkspace } from "../context/useWorkspace";
import type { Workspace } from "../types/workspace";
import type { Member } from "../types/member";
import CreateWorkspaceForm from "../components/CreateWorkspaceForm";
import MemberAvatars from "../components/MemberAvatars";

const WorkspacesPage = () => {
  const {
    workspaces,
    currentWorkspace,
    isLoading,
    refetchWorkspaces,
    setCurrentWorkspaceId,
  } = useWorkspace();
  const [membersByWorkspace, setMembersByWorkspace] = useState<
    Record<string, Member[]>
  >({});

  useEffect(() => {
    workspaces.forEach((workspace) => {
      if (membersByWorkspace[workspace.id]) return;

      api
        .get<Member[]>(`/workspaces/${workspace.id}/members`)
        .then((response) => {
          setMembersByWorkspace((prev) => ({
            ...prev,
            [workspace.id]: response.data,
          }));
        })
        .catch(() => {
          setMembersByWorkspace((prev) => ({ ...prev, [workspace.id]: [] }));
        });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaces]);

  const handleCreateWorkspace = async (name: string) => {
    try {
      await api.post("/workspaces", { name });
      await refetchWorkspaces();
      toast.success("Workspace created");
    } catch {
      toast.error("Failed to create workspace");
    }
  };

  return (
    <div className="max-w-5xl px-8 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Workspaces</h1>
        <p className="text-sm text-slate-500 mt-1">
          {workspaces.length} workspaces
        </p>
      </div>

      <div className="border border-slate-200 rounded-xl bg-white p-6 mb-8">
        <p className="text-sm font-medium text-slate-900 mb-3">
          Create a new workspace
        </p>
        <CreateWorkspaceForm onCreate={handleCreateWorkspace} />
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-500">Loading...</p>
      ) : workspaces.length === 0 ? (
        <div className="border border-slate-200 rounded-xl bg-white px-5 py-10 text-center">
          <p className="text-sm text-slate-500">
            You don't have any workspaces yet.
          </p>
        </div>
      ) : (
        <div className="border border-slate-200 rounded-xl divide-y divide-slate-100 bg-white">
          {workspaces.map((workspace) => (
            <WorkspaceRow
              key={workspace.id}
              workspace={workspace}
              members={membersByWorkspace[workspace.id] ?? []}
              isActive={currentWorkspace?.id === workspace.id}
              onSetActive={() => setCurrentWorkspaceId(workspace.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

type WorkspaceRowProps = {
  workspace: Workspace;
  members: Member[];
  isActive: boolean;
  onSetActive: () => void;
};

const WorkspaceRow = ({
  workspace,
  members,
  isActive,
  onSetActive,
}: WorkspaceRowProps) => {
  return (
    <div className="flex items-center gap-4 px-5 py-4">
      <div className="size-9 rounded-lg bg-slate-900 flex items-center justify-center shrink-0 text-white font-semibold text-sm">
        {workspace.name.slice(0, 1).toUpperCase()}
      </div>

      <div className="min-w-0 flex-1">
        <Link
          to={`/dashboard/workspaces/${workspace.id}`}
          className="text-sm font-medium text-slate-900 hover:underline truncate block"
        >
          {workspace.name}
        </Link>
        <p className="text-xs text-slate-500">{workspace.role}</p>
      </div>

      <MemberAvatars members={members} />

      {isActive ? (
        <span className="text-xs font-medium text-slate-500 px-2.5 py-1 rounded-md bg-slate-100 shrink-0">
          Current
        </span>
      ) : (
        <button
          type="button"
          onClick={onSetActive}
          className="text-xs font-medium text-slate-600 hover:text-slate-900 px-2.5 py-1 rounded-md border border-slate-200 hover:bg-slate-50 transition-colors shrink-0"
        >
          Set active
        </button>
      )}
    </div>
  );
};

export default WorkspacesPage;
