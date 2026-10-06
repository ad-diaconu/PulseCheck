import { createContext } from "react";
import type { Workspace } from "../types/workspace";

export type WorkspaceContextType = {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  setCurrentWorkspaceId: (id: string) => void;
  isLoading: boolean;
  refetchWorkspaces: () => Promise<void>;
};

export const WorkspaceContext = createContext<WorkspaceContextType | undefined>(
  undefined,
);
