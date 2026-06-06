import * as React from "react";

import { cn } from "@/lib/utils";

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      data-slot="input"
      type={type}
      className={cn(
        "flex h-9 w-full rounded-md border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-sm text-foreground placeholder:text-zinc-500",
        "outline-none transition-colors",
        "focus:border-[#8CFF2E]/50 focus:ring-1 focus:ring-[#8CFF2E]/30",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground",
        className
      )}
      {...props}
    />
  );
}

export { Input };
