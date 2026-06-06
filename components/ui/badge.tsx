import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-1.5 py-0.5 font-mono text-[11px] font-medium uppercase tracking-wide",
  {
    variants: {
      variant: {
        default:
          "border-white/10 bg-white/[0.04] text-zinc-300",
        success:
          "border-[#8CFF2E]/25 bg-[#8CFF2E]/10 text-[#8CFF2E]",
        warning:
          "border-amber-500/25 bg-amber-500/10 text-amber-400",
        danger:
          "border-red-500/25 bg-red-500/10 text-red-400",
        muted:
          "border-white/[0.06] bg-white/[0.02] text-zinc-500",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Badge({
  className,
  variant,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return (
    <span
      data-slot="badge"
      className={cn(badgeVariants({ variant, className }))}
      {...props}
    />
  );
}

export { Badge, badgeVariants };
