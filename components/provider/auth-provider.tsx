"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";

import { api, type MeResponse } from "@/lib/api";
import { clearToken, getToken, setToken } from "@/lib/auth";

interface AuthContextType {
  user: MeResponse | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<MeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: move to HTTP-only cookie before production
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    api.auth
      .me()
      .then((u) => setUser(u))
      .catch(() => {
        clearToken();
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await api.auth.login({ email, password });
      // TODO: move to HTTP-only cookie before production
      setToken(res.token);
      const me = await api.auth.me();
      setUser(me);
      router.push("/dashboard");
    },
    [router]
  );

  const register = useCallback(
    async (email: string, password: string, name?: string) => {
      const res = await api.auth.register({ email, password, name });
      // TODO: move to HTTP-only cookie before production
      setToken(res.token);
      const me = await api.auth.me();
      setUser(me);
      router.push("/dashboard");
    },
    [router]
  );

  const logout = useCallback(() => {
    // TODO: move to HTTP-only cookie before production
    clearToken();
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}
