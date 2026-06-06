"use client";

import type { ReactNode } from "react";

import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/topbar";
import {
  SidebarStateProvider,
  useSidebarState,
} from "@/hooks/use-sidebar-state";
import { cn } from "@/lib/utils";

function ShellLayout({ children }: { children: ReactNode }) {
  const { collapsed } = useSidebarState();
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div
        className={cn(
          "transition-[margin-left] duration-200 ease-out",
          collapsed ? "md:ml-16" : "md:ml-60"
        )}
      >
        <TopBar />
        <main className="px-6 py-8 md:px-8">
          <div className="mx-auto w-full max-w-6xl">{children}</div>
        </main>
      </div>
    </div>
  );
}

export function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <SidebarStateProvider>
      <ShellLayout>{children}</ShellLayout>
    </SidebarStateProvider>
  );
}
