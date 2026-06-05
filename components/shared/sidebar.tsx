/* eslint-disable @next/next/no-img-element */
/* eslint-disable react-hooks/set-state-in-effect */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Key,
  LayoutDashboard,
  ScrollText,
  Send,
  Settings,
  ChevronLeft,
  ChevronRight,
  type LucideIcon,
} from "lucide-react";

import { cn } from "@/lib/utils";

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

const navItems: NavItem[] = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Emails", href: "/emails", icon: Send },
  { label: "API Keys", href: "/api-keys", icon: Key },
  { label: "Logs", href: "/logs", icon: ScrollText },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Sayfa yüklendiğinde kullanıcının son sidebar tercihini hatırla
  useEffect(() => {
    const saved = localStorage.getItem("sidebar-collapsed");
    if (saved === "true") {
      setIsCollapsed(true);
    }
    setMounted(true);
  }, []);

  const toggleSidebar = () => {
    setIsCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("sidebar-collapsed", String(next));
      return next;
    });
  };

  // SSR uyumsuzluğunu engellemek için mount kontrolü
  if (!mounted) {
    return <aside className="w-60 shrink-0 border-r border-white/10 bg-[var(--bg)]" />;
  }

  return (
    <aside
      className={cn(
        "flex shrink-0 flex-col border-r border-white/10 bg-[var(--bg)] transition-all duration-300 ease-in-out relative select-none",
        isCollapsed ? "w-[68px]" : "w-60"
      )}
    >
      {/* Üst Logo Alanı */}
      <div className="flex h-14 items-center px-4 border-b border-white/10 justify-between overflow-hidden">
        <Link 
          href="/dashboard" 
          className={cn(
            "inline-flex items-center transition-all duration-300",
            isCollapsed ? "transform translate-x-1" : ""
          )}
        >
        <img src="./favicon/favicon.svg" alt="Logo" className="h-6 w-auto transition-opacity duration-300" />
         <span className={cn("transition-all duration-200 whitespace-nowrap text-bold font-lg ml-2 text-xl", isCollapsed ? "opacity-0 pointer-events-none translate-x-2" : "opacity-100")}>
           Courier
         </span>
        </Link>
      </div>

      {/* Navigasyon Listesi */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto overflow-x-hidden space-y-1">
        <ul className="space-y-1">
          {navItems.map(({ label, href, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(`${href}/`);
            return (
              <li key={href} className="group relative">
                <Link
                  href={href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 relative",
                    active
                      ? "bg-white/[0.06] text-[var(--text)] shadow-sm shadow-black/20"
                      : "text-gray-400 hover:bg-white/[0.03] hover:text-[var(--text)]"
                  )}
                >
                  {/* Aktif Çizgisi - Modern Sol Çizgi */}
                  {active && (
                    <span
                      aria-hidden="true"
                      className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r-md bg-brand shadow-[0_0_10px_rgba(var(--brand-rgb),0.5)]"
                    />
                  )}
                  
                  {/* İkon */}
                  <Icon
                    className={cn(
                      "h-[18px] w-[18px] shrink-0 transition-colors duration-200",
                      active ? "text-brand" : "text-gray-400 group-hover:text-gray-200"
                    )}
                    strokeWidth={2}
                  />

                  {/* Metin Alanı (Kapanınca yumuşakça kaybolur) */}
                  <span
                    className={cn(
                      "transition-all duration-200 whitespace-nowrap",
                      isCollapsed ? "opacity-0 pointer-events-none translate-x-2" : "opacity-100"
                    )}
                  >
                    {label}
                  </span>
                </Link>

                {/* Sidebar kapalıyken çıkan modern Tooltip */}
                {isCollapsed && (
                  <div className="absolute left-16 top-1/2 -translate-y-1/2 z-50 pointer-events-none invisible opacity-0 translate-x-[-10px] group-hover:visible group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200 bg-gray-900 text-gray-100 text-xs font-medium px-2.5 py-1.5 rounded-md border border-gray-800 shadow-xl whitespace-nowrap">
                    {label}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Alt Profil ve Daraltma Butonu Alanı */}
      <div className="border-t border-gray-800/50 p-3 flex flex-col gap-2 bg-black/[0.02]">
        {/* Profil Kartı */}
        <div className="flex items-center gap-3 px-1 py-1 overflow-hidden min-h-[40px]">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-gray-800 bg-white/[0.04] text-xs font-bold text-gray-200 shadow-inner">
            P
          </div>
          <div
            className={cn(
              "min-w-0 flex-1 transition-all duration-200",
              isCollapsed ? "opacity-0 pointer-events-none translate-x-2" : "opacity-100"
            )}
          >
            <div className="truncate text-xs font-semibold text-[var(--text)] tracking-wide">
              Personal Workspace
            </div>
            <div className="inline-flex items-center rounded-full bg-brand/10 px-1.5 py-0.5 text-[10px] font-medium text-brand mt-0.5">
              Free plan
            </div>
          </div>
        </div>

        {/* Collapse Tetikleyici Buton */}
        <button
          onClick={toggleSidebar}
          className="mt-1 flex h-8 w-full items-center justify-center rounded-lg border border-gray-800/80 bg-white/[0.02] text-gray-400 hover:bg-white/[0.05] hover:text-[var(--text)] transition-colors duration-150 active:scale-[0.98]"
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <div className="flex items-center gap-2 text-xs font-medium px-2">
              <ChevronLeft className="h-4 w-4" />
              <span>Collapse</span>
            </div>
          )}
        </button>
      </div>
    </aside>
  );
}