"use client";

import { ChevronDown, ChevronRight, Search } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const labelMap: Record<string, string> = {
  dashboard: "Overview",
  emails: "Emails",
  "api-keys": "API Keys",
  logs: "Logs",
  settings: "Settings",
};

function segmentLabel(segment: string) {
  return (
    labelMap[segment] ??
    segment
      .split("-")
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join(" ")
  );
}

export function TopBar() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);
  const crumbs = segments.length > 0 ? segments : ["dashboard"];

  return (
    <header className="sticky top-0 z-40 flex h-14 shrink-0 items-center justify-between border-b border-white/10  bg-[var(--bg)]/75 px-6 backdrop-blur-md">
      {/* Sol Taraf: Modern Breadcrumb */}
      <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-xs font-medium tracking-wide">
        <span className="text-gray-400 hover:text-gray-200 transition-colors cursor-pointer bg-white/[0.03] px-2 py-1 rounded-md border border-gray-800/60">
          Personal Workspace
        </span>
        <ChevronRight className="h-3 w-3 text-gray-600" strokeWidth={2.5} />
        
        <div className="flex items-center gap-1.5">
          {crumbs.map((seg, i) => {
            const isLast = i === crumbs.length - 1;
            return (
              <div key={`${seg}-${i}`} className="flex items-center gap-1.5">
                {i > 0 && <ChevronRight className="h-3 w-3 text-gray-600" strokeWidth={2.5} />}
                <span
                  className={cn(
                    "transition-colors",
                    isLast
                      ? "text-[var(--text)] font-semibold"
                      : "text-gray-500 hover:text-gray-300 cursor-pointer"
                  )}
                >
                  {segmentLabel(seg)}
                </span>
              </div>
            );
          })}
        </div>
      </nav>

      {/* Sağ Taraf: Arama ve Profil */}
      <div className="flex items-center gap-3">
        {/* Modern Arama Butonu */}
        <button
          type="button"
          className="inline-flex h-8 w-44 items-center justify-between rounded-lg border border-gray-800/80 bg-white/[0.01] pl-2.5 pr-1.5 text-xs text-gray-400 transition-all duration-150 hover:border-gray-700 hover:bg-white/[0.03] hover:text-gray-300 focus:outline-none focus:ring-1 focus:ring-brand/50"
        >
          <div className="flex items-center gap-2">
            <Search className="h-3.5 w-3.5 text-gray-500" strokeWidth={2} />
            <span>Search...</span>
          </div>
          <kbd className="inline-flex h-5 select-none items-center gap-0.5 rounded border border-gray-800 bg-white/[0.04] px-1.5 font-mono text-[9px] font-medium text-gray-500 shadow-sm">
            /
          </kbd>
        </button>

        {/* Profil Menü Butonu */}
        <button
          type="button"
          className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-transparent p-1 pl-1 pr-2 transition-all duration-150 hover:border-gray-800 hover:bg-white/[0.03] active:scale-[0.98]"
          aria-label="User menu"
        >
          <div className="relative flex h-6 w-6 shrink-0 select-none items-center justify-center rounded-full bg-gradient-to-br from-emerald-500/90 to-teal-600 text-[10px] font-bold text-white shadow-md shadow-emerald-950/50 ring-1 ring-white/10">
            SA
          </div>
          <ChevronDown
            className="h-3 w-3 text-gray-500 transition-colors group-hover:text-gray-300"
            strokeWidth={2.5}
          />
        </button>
      </div>
    </header>
  );
}