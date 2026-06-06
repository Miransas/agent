"use client";

import {
  createContext,
  useCallback,
  useContext,
  useSyncExternalStore,
  type ReactNode,
} from "react";

const STORAGE_KEY = "cx-sidebar-collapsed";

interface SidebarState {
  collapsed: boolean;
  toggle: () => void;
}

const SidebarStateContext = createContext<SidebarState | null>(null);

function subscribe(onChange: () => void) {
  window.addEventListener("storage", onChange);
  window.addEventListener("cx-sidebar-collapsed-change", onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener("cx-sidebar-collapsed-change", onChange);
  };
}

function getClientSnapshot(): boolean {
  return window.localStorage.getItem(STORAGE_KEY) === "true";
}

function getServerSnapshot(): boolean {
  return false;
}

interface ProviderProps {
  children: ReactNode;
}

export function SidebarStateProvider({ children }: ProviderProps) {
  const collapsed = useSyncExternalStore(
    subscribe,
    getClientSnapshot,
    getServerSnapshot
  );

  const toggle = useCallback(() => {
    const next = !(window.localStorage.getItem(STORAGE_KEY) === "true");
    window.localStorage.setItem(STORAGE_KEY, String(next));
    window.dispatchEvent(new Event("cx-sidebar-collapsed-change"));
  }, []);

  return (
    <SidebarStateContext.Provider value={{ collapsed, toggle }}>
      {children}
    </SidebarStateContext.Provider>
  );
}

export function useSidebarState(): SidebarState {
  const ctx = useContext(SidebarStateContext);
  if (!ctx) {
    throw new Error(
      "useSidebarState must be used within a SidebarStateProvider"
    );
  }
  return ctx;
}
