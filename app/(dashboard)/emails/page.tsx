import { Mail } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";

export default function EmailsPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Emails
        </h1>
        <p className="text-sm text-zinc-400">
          Send, queue, and review your transactional messages.
        </p>
      </header>

      <EmptyState
        icon={Mail}
        title="No emails yet"
        description="Sent messages will show up here once your first request comes in."
      />
    </div>
  );
}
