import * as React from "react";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

interface EmptyStateProps extends React.ComponentProps<"div"> {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
  ...props
}: EmptyStateProps) {
  return (
    <div
      data-slot="empty-state"
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-white/[0.06] bg-[#0a0a0a] px-6 py-16 text-center",
        className
      )}
      {...props}
    >
      <div className="flex size-12 items-center justify-center rounded-full border border-white/[0.06] bg-white/[0.02] text-zinc-500">
        <Icon className="size-5" strokeWidth={1.75} />
      </div>
      <h3 className="mt-5 text-base font-semibold text-foreground">{title}</h3>
      {description ? (
        <p className="mt-1.5 max-w-sm text-sm text-zinc-400">{description}</p>
      ) : null}
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}

export { EmptyState };
