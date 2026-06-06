import type { LucideIcon } from "lucide-react";
import { TrendingDown, TrendingUp } from "lucide-react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string;
  delta?: string;
  /** Direction of the delta arrow. Defaults to inferring from the sign of `delta`. */
  deltaDirection?: "up" | "down";
  /** Whether the delta should be styled as a positive change. Defaults to inferring from the sign of `delta`. */
  deltaPositive?: boolean;
  icon: LucideIcon;
}

export function StatCard({
  label,
  value,
  delta,
  deltaDirection,
  deltaPositive,
  icon: Icon,
}: StatCardProps) {
  const inferredDown = delta?.trim().startsWith("-");
  const direction = deltaDirection ?? (inferredDown ? "down" : "up");
  const isPositive = deltaPositive ?? !inferredDown;
  const TrendIcon = direction === "down" ? TrendingDown : TrendingUp;

  return (
    <Card className="flex flex-col gap-3 p-5">
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-zinc-500">
          {label}
        </span>
        <Icon className="size-4 text-zinc-600" strokeWidth={2} />
      </div>
      <span className="font-mono text-4xl font-bold tracking-tight text-foreground">
        {value}
      </span>
      {delta ? (
        <span
          className={cn(
            "flex items-center gap-1 text-xs font-medium",
            isPositive ? "text-[#8CFF2E]" : "text-red-400"
          )}
        >
          <TrendIcon className="size-3.5" strokeWidth={2.25} />
          {delta}
        </span>
      ) : null}
    </Card>
  );
}
