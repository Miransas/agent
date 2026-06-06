import * as React from "react";

import { cn } from "@/lib/utils";

interface LogomarkProps extends React.SVGProps<SVGSVGElement> {
  size?: number;
}

function Logomark({ size = 24, className, ...props }: LogomarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className={cn("shrink-0", className)}
      {...props}
    >
      <rect width="24" height="24" rx="6" fill="#8CFF2E" />
      <path
        d="M6 8.5L12 5L18 8.5V15.5L12 19L6 15.5V8.5Z"
        stroke="#050505"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
      <path
        d="M6 8.5L12 12L18 8.5"
        stroke="#050505"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
      <path d="M12 12V19" stroke="#050505" strokeWidth="1.75" />
    </svg>
  );
}

export { Logomark };
