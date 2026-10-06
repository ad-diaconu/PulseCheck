import { useCallback, useEffect, useState, type ReactNode } from "react";
import { api } from "../services/api";
import type { Workspace } from "../types/workspace";
import { WorkspaceContext } from "./workspace-context-definition";

export const WORKSPACE_STORAGE_KEY = "pulsecheck:currentWorkspaceId";
const STORAGE_KEY = WORKSPACE_STORAGE_KEY;

export const WorkspaceProvider = ({ children }: { children: ReactNode }) => {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [currentWorkspaceId, setCurrentWorkspaceIdState] = useState<
    string | null
  >(() => {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch {
      return null;
    }
  });

  const refetchWorkspaces = useCallback(async () => {
    try {
      const response = await api.get<Workspace[]>("/workspaces");
      setWorkspaces(response.data);
    } catch {
      setWorkspaces([]);
    }
  }, []);

  useEffect(() => {
    const loadInitialWorkspaces = async () => {
      try {
        const response = await api.get<Workspace[]>("/workspaces");
        setWorkspaces(response.data);
      } catch {
        setWorkspaces([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialWorkspaces();
  }, []);

  const setCurrentWorkspaceId = useCallback((id: string) => {
    setCurrentWorkspaceIdState(id);
    try {
      localStorage.setItem(STORAGE_KEY, id);
    } catch {
      // localStorage unavailable (private mode, etc.) — selection won't persist, not fatal
    }
  }, []);

  const currentWorkspace =
    workspaces.find((w) => w.id === currentWorkspaceId) ??
    workspaces[0] ??
    null;

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        currentWorkspace,
        setCurrentWorkspaceId,
        isLoading,
        refetchWorkspaces,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
};
