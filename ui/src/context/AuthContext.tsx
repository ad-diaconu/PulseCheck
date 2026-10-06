import { useEffect, useState, type ReactNode } from "react";
import { api } from "../services/api";
import { AuthContext } from "./auth-context-definition";
import { WORKSPACE_STORAGE_KEY } from "./WorkspaceContext";

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<{
    name: string | null;
    email: string;
  } | null>(null);
  const fetchAuth = async () => {
    try {
      const response = await api.get("/me");
      setIsAuthenticated(true);
      setUser({
        name: response.data.full_name ?? null,
        email: response.data.email,
      });
    } catch {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  useEffect(() => {
    const loadInitialAuth = async () => {
      await fetchAuth();
      setIsLoading(false);
    };

    loadInitialAuth();
  }, []);

  const login = async () => {
    await fetchAuth();
  };

  const logout = async () => {
    try {
      await api.post("/logout");
      setIsAuthenticated(false);
      setUser(null);
      try {
        localStorage.removeItem(WORKSPACE_STORAGE_KEY);
      } catch {
        // localStorage unavailable — nothing to clean up
      }
    } catch (error) {
      throw new Error("Logout process could not be done.", { cause: error });
    }
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, isLoading, user, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};
