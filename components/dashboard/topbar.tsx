"use client";

import { ArrowUpRight, Moon, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { usePathname } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useSidebarState } from "@/hooks/use-sidebar-state";

const SECTION_LABELS: Record<string, string> = {
  dashboard: "Overview",
  emails: "Emails",
  domains: "Domains",
  "api-keys": "API Keys",
  logs: "Logs",
  settings: "Settings",
  login: "Login",
};

function sectionLabel(pathname: string) {
  const first = pathname.split("/").filter(Boolean)[0];
  if (!first) return "Overview";
  return (
    SECTION_LABELS[first] ??
    first
      .split("-")
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join(" ")
  );
}

export function TopBar() {
  const pathname = usePathname();
  const label = sectionLabel(pathname);
  const { collapsed, toggle } = useSidebarState();
  const ToggleIcon = collapsed ? PanelLeftOpen : PanelLeftClose;

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/[0.06] bg-[#050505]/80 px-6 backdrop-blur md:px-8">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={toggle}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-pressed={collapsed}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="-ml-1.5 flex size-8 items-center justify-center rounded-md text-zinc-400 transition-colors hover:bg-white/[0.04] hover:text-foreground"
        >
          <ToggleIcon className="size-4" strokeWidth={2} />
        </button>
        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm">
          <span className="text-zinc-500">Console</span>
          <span className="text-zinc-700">/</span>
          <span className="font-medium text-foreground">{label}</span>
        </nav>
      </div>

      <div className="flex items-center gap-2">
        <a
          href="https://docs.courierx.dev"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 text-sm text-zinc-400 transition-colors hover:bg-white/[0.04] hover:text-foreground"
        >
          Docs
          <ArrowUpRight className="size-3.5" strokeWidth={2} />
        </a>
        <Button variant="ghost" size="sm">
          Feedback
        </Button>
        <Button variant="ghost" size="icon" aria-label="Toggle theme">
          <Moon className="size-4" strokeWidth={2} />
        </Button>
      </div>
    </header>
  );
}
