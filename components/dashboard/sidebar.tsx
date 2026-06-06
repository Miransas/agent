/* eslint-disable @next/next/no-img-element */
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronsUpDown,
  Globe,
  Key,
  LayoutDashboard,
  LogOut,
  Mail,
  ScrollText,
  Settings,
  type LucideIcon,
} from "lucide-react";

import { useSidebarState } from "@/hooks/use-sidebar-state";
import { cn } from "@/lib/utils";

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

const navItems: NavItem[] = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Emails", href: "/emails", icon: Mail },
  { label: "Domains", href: "/domains", icon: Globe },
  { label: "API Keys", href: "/api-keys", icon: Key },
  { label: "Logs", href: "/logs", icon: ScrollText },
  { label: "Settings", href: "/settings", icon: Settings },
];

function isActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

const labelBase =
  "overflow-hidden whitespace-nowrap transition-[max-width,opacity] duration-150";
const labelExpanded = "max-w-[200px] opacity-100";
const labelCollapsed = "max-w-0 opacity-0";

export function Sidebar() {
  const pathname = usePathname();
  const { collapsed } = useSidebarState();

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 hidden flex-col overflow-hidden border-r border-white/[0.06] bg-[#0a0a0a] transition-[width] duration-200 ease-out md:flex",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div
        className={cn(
          "flex h-16 items-center",
          collapsed ? "justify-center" : "gap-2.5 px-5"
        )}
      >
        <img src="./favicon/favicon.svg" alt="" className="size-6 shrink-0" />
        <span
          className={cn(
            "text-[15px] font-semibold tracking-tight text-foreground",
            labelBase,
            collapsed ? labelCollapsed : labelExpanded
          )}
        >
          CourierX
        </span>
      </div>

      <div className={cn(collapsed ? "px-2" : "px-3")}>
        <button
          type="button"
          title={collapsed ? "Default Workspace" : undefined}
          className={cn(
            "flex w-full items-center rounded-md border border-white/[0.06] bg-white/[0.02] text-sm text-zinc-300 transition-colors hover:bg-white/[0.04]",
            collapsed ? "justify-center px-0 py-2" : "justify-between px-3 py-2 text-left"
          )}
        >
          <span className="flex items-center gap-2 truncate">
            <span className="flex size-5 shrink-0 items-center justify-center rounded bg-white/[0.06] text-[10px] font-semibold text-zinc-300">
              D
            </span>
            <span
              className={cn(
                "truncate",
                labelBase,
                collapsed ? labelCollapsed : labelExpanded
              )}
            >
              Default Workspace
            </span>
          </span>
          {!collapsed && (
            <ChevronsUpDown
              className="size-3.5 shrink-0 text-zinc-500"
              strokeWidth={2}
            />
          )}
        </button>
      </div>

      <nav
        className={cn(
          "mt-4 flex-1 overflow-y-auto",
          collapsed ? "px-2" : "px-3"
        )}
      >
        <ul className="space-y-0.5">
          {navItems.map(({ label, href, icon: Icon }) => {
            const active = isActive(pathname, href);
            return (
              <li key={href}>
                <Link
                  href={href}
                  title={label}
                  aria-label={label}
                  className={cn(
                    "relative flex items-center rounded-md text-sm transition-colors",
                    collapsed
                      ? "justify-center px-0 py-2"
                      : "gap-2.5 px-3 py-2",
                    active
                      ? "bg-[#8CFF2E]/10 text-foreground"
                      : "text-zinc-400 hover:bg-white/[0.03] hover:text-foreground"
                  )}
                >
                  {active ? (
                    <span
                      aria-hidden
                      className="absolute inset-y-1.5 left-0 w-[2px] rounded-r bg-[#8CFF2E]"
                    />
                  ) : null}
                  <Icon
                    className={cn(
                      "size-4 shrink-0",
                      active ? "text-[#8CFF2E]" : "text-zinc-500"
                    )}
                    strokeWidth={2}
                  />
                  <span
                    className={cn(
                      "font-medium",
                      labelBase,
                      collapsed ? labelCollapsed : labelExpanded
                    )}
                  >
                    {label}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div
        className={cn(
          "border-t border-white/[0.06]",
          collapsed ? "p-2" : "p-3"
        )}
      >
        {collapsed ? (
          <button
            type="button"
            title="Sign out"
            aria-label="Sign out"
            className="flex w-full items-center justify-center rounded-md py-1.5 transition-colors hover:bg-white/[0.04]"
          >
            <div className="flex size-8 items-center justify-center rounded-full bg-white/[0.06] text-xs font-semibold text-zinc-300">
              Y
            </div>
          </button>
        ) : (
          <div className="flex items-center gap-2.5 rounded-md px-2 py-2">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-white/[0.06] text-xs font-semibold text-zinc-300">
              Y
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-xs font-medium text-foreground">
                you@example.com
              </div>
              <div className="truncate text-[11px] text-zinc-500">
                Personal account
              </div>
            </div>
            <button
              type="button"
              aria-label="Sign out"
              className="flex size-7 shrink-0 items-center justify-center rounded-md text-zinc-500 transition-colors hover:bg-white/[0.04] hover:text-foreground"
            >
              <LogOut className="size-3.5" strokeWidth={2} />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
