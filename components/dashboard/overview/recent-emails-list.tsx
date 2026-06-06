import { ArrowRight } from "lucide-react";

import { cn } from "@/lib/utils";

type EmailStatus = "delivered" | "queued" | "failed";

interface RecentEmail {
  status: EmailStatus;
  from: string;
  to: string;
  subject: string;
  time: string;
}

const recentEmails: RecentEmail[] = [
  {
    status: "delivered",
    from: "welcome@app.io",
    to: "alex@example.com",
    subject: "Welcome to your new account",
    time: "2m ago",
  },
  {
    status: "delivered",
    from: "noreply@app.io",
    to: "maria@startup.dev",
    subject: "Your order has shipped",
    time: "5m ago",
  },
  {
    status: "queued",
    from: "billing@app.io",
    to: "sam@company.com",
    subject: "Invoice #423 — December 2026",
    time: "7m ago",
  },
  {
    status: "failed",
    from: "alerts@app.io",
    to: "broken@invalid",
    subject: "Alert: Build failed",
    time: "12m ago",
  },
  {
    status: "delivered",
    from: "hello@app.io",
    to: "emma@design.co",
    subject: "Quick question about your subscription",
    time: "15m ago",
  },
  {
    status: "delivered",
    from: "team@app.io",
    to: "john@example.org",
    subject: "Welcome back — your trial is active",
    time: "22m ago",
  },
];

const STATUS_STYLES: Record<
  EmailStatus,
  { dot: string; text: string; glow: string }
> = {
  delivered: {
    dot: "bg-[#8CFF2E]",
    text: "text-[#8CFF2E]",
    glow: "shadow-[0_0_6px_#8CFF2E]",
  },
  queued: {
    dot: "bg-amber-400",
    text: "text-amber-400",
    glow: "shadow-[0_0_6px_#fbbf24]",
  },
  failed: {
    dot: "bg-red-500",
    text: "text-red-400",
    glow: "shadow-[0_0_6px_#ef4444]",
  },
};

export function RecentEmailsList() {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-[#0a0a0a]">
      <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4">
        <h2 className="text-sm font-medium text-foreground">Recent emails</h2>
        <a
          href="/emails"
          className="inline-flex items-center gap-1 text-xs text-zinc-500 transition-colors hover:text-foreground"
        >
          View all
          <ArrowRight className="size-3" strokeWidth={2} />
        </a>
      </div>

      <ul>
        {recentEmails.map((email, i) => {
          const styles = STATUS_STYLES[email.status];
          const isLast = i === recentEmails.length - 1;
          return (
            <li
              key={`${email.to}-${email.time}`}
              className={cn(
                "flex items-center gap-4 px-5 py-3 transition-colors hover:bg-white/[0.02]",
                !isLast && "border-b border-white/[0.04]"
              )}
            >
              <div className="flex w-28 shrink-0 items-center gap-2.5">
                <span
                  className={cn(
                    "size-2 shrink-0 rounded-full",
                    styles.dot,
                    styles.glow
                  )}
                />
                <span
                  className={cn(
                    "text-xs font-medium capitalize",
                    styles.text
                  )}
                >
                  {email.status}
                </span>
              </div>

              <div className="flex min-w-0 items-center gap-2 font-mono text-sm text-zinc-300">
                <span className="truncate">{email.from}</span>
                <span className="text-zinc-600">→</span>
                <span className="truncate">{email.to}</span>
              </div>

              <span className="hidden flex-1 truncate text-sm text-zinc-400 md:block">
                {email.subject}
              </span>

              <span className="ml-auto shrink-0 font-mono text-xs text-zinc-500">
                {email.time}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
