import { ScrollText } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";

export default function LogsPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Logs
        </h1>
        <p className="text-sm text-zinc-400">
          Inspect every request and delivery event in real time.
        </p>
      </header>

      <EmptyState
        icon={ScrollText}
        title="No log entries yet"
        description="Request and delivery events will stream in here as they happen."
      />
    </div>
  );
}
