import { createContext } from "react";

export type AuthContextType = {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: { name: string | null; email: string } | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined,
);
