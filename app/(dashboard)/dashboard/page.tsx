import {
  Activity,
  Calendar,
  CheckCircle2,
  ChevronDown,
  Mail,
  XCircle,
} from "lucide-react";

import { StatCard } from "@/components/dashboard/stat-card";
import { DeliverabilityCard } from "@/components/dashboard/overview/deliverability-card";
import { MetricsChart } from "@/components/dashboard/overview/metrics-chart";
import { RecentEmailsList } from "@/components/dashboard/overview/recent-emails-list";

export default function OverviewPage() {
  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1.5">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Overview
          </h1>
          <p className="text-sm text-zinc-400">
            A quick read on your sending activity.
          </p>
        </div>
        <button
          type="button"
          className="flex items-center gap-2 rounded-full border border-white/[0.08] px-4 py-2 text-sm text-zinc-300 transition-colors hover:border-white/[0.15]"
        >
          <Calendar className="size-3.5" strokeWidth={2} />
          Last 7 days
          <ChevronDown className="size-3.5 text-zinc-500" strokeWidth={2} />
        </button>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Emails sent"
          value="12,847"
          delta="+12.4% from last week"
          icon={Mail}
        />
        <StatCard
          label="Delivered"
          value="12,634"
          delta="+11.8% from last week"
          icon={CheckCircle2}
        />
        <StatCard
          label="Bounced"
          value="213"
          delta="-3.2% from last week"
          deltaDirection="down"
          deltaPositive
          icon={XCircle}
        />
        <StatCard
          label="API requests"
          value="15,402"
          delta="+18.1% from last week"
          icon={Activity}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <MetricsChart />
        <DeliverabilityCard />
      </div>

      <RecentEmailsList />
    </div>
  );
}
