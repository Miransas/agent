import { Activity, CheckCircle2, Mail, XCircle } from "lucide-react";

import { StatCard } from "@/components/dashboard/stat-card";

export default function OverviewPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Overview
        </h1>
        <p className="text-sm text-zinc-400">
          A quick read on your sending activity.
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Emails sent" value="0" icon={Mail} />
        <StatCard label="Delivered" value="0" icon={CheckCircle2} />
        <StatCard label="Bounced" value="0" icon={XCircle} />
        <StatCard label="API requests" value="0" icon={Activity} />
      </div>
    </div>
  );
}
