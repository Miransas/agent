import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "radix-ui";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex shrink-0 select-none items-center justify-center gap-2 whitespace-nowrap rounded-full font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-accent text-accent-foreground hover:bg-accent/90 active:bg-accent/85",
        secondary:
          "bg-white/[0.05] text-zinc-200 hover:bg-white/[0.08] active:bg-white/[0.06]",
        ghost:
          "bg-transparent text-zinc-300 hover:bg-white/[0.05] hover:text-foreground",
        outline:
          "border border-white/10 bg-transparent text-zinc-200 hover:bg-white/[0.04] hover:text-foreground",
        danger:
          "bg-danger/15 text-danger hover:bg-danger/25",
      },
      size: {
        sm: "h-7 px-3 text-xs [&_svg]:size-3.5",
        default: "h-9 px-4 text-sm [&_svg]:size-4",
        lg: "h-11 px-6 text-sm [&_svg]:size-4",
        icon: "size-9 [&_svg]:size-4",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot.Root : "button";

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
