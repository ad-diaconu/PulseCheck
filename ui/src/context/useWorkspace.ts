import { useContext } from "react";
import { WorkspaceContext } from "./workspace-context-definition";

export const useWorkspace = () => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error("useWorkspace must be used within WorkspaceProvider");
  }
  return context;
};
