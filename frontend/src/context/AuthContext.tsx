import { createContext, ReactNode, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";

export type User = { username: string; email: string };
type Auth = { user: User | null; token: string | null; login: (token: string, user: User) => void; logout: () => void; isAuthenticated: boolean };
const AuthContext = createContext<Auth | undefined>(undefined);
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem("auth_token"));
  const [user, setUser] = useState<User | null>(() => { try { return JSON.parse(localStorage.getItem("auth_user") || "null"); } catch { return null; } });
  const navigate = useNavigate();
  const login = (next: string, account: User) => { localStorage.setItem("auth_token", next); localStorage.setItem("auth_user", JSON.stringify(account)); setToken(next); setUser(account); };
  const logout = () => { localStorage.removeItem("auth_token"); localStorage.removeItem("auth_user"); setToken(null); setUser(null); navigate("/auth"); };
  return <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: Boolean(token) }}>{children}</AuthContext.Provider>;
}
export const useAuth = () => { const value = useContext(AuthContext); if (!value) throw new Error("useAuth requires AuthProvider"); return value; };
