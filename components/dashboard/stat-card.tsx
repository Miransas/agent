import type { LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string;
  delta?: string;
  icon: LucideIcon;
}

export function StatCard({ label, value, delta, icon: Icon }: StatCardProps) {
  const isPositive = delta?.startsWith("+");
  const isNegative = delta?.startsWith("-");

  return (
    <Card className="flex flex-col gap-4 p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-zinc-500">
          {label}
        </span>
        <span className="flex size-7 items-center justify-center rounded-md border border-white/[0.06] bg-white/[0.02] text-zinc-400">
          <Icon className="size-3.5" strokeWidth={2} />
        </span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-2xl font-semibold tracking-tight text-foreground">
          {value}
        </span>
        {delta ? (
          <span
            className={cn(
              "font-mono text-xs font-medium",
              isPositive && "text-[#8CFF2E]",
              isNegative && "text-red-400",
              !isPositive && !isNegative && "text-zinc-500"
            )}
          >
            {delta}
          </span>
        ) : null}
      </div>
    </Card>
  );
}
