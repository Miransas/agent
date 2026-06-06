import { Key } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";

export default function ApiKeysPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          API Keys
        </h1>
        <p className="text-sm text-zinc-400">
          Generate and rotate credentials for the CourierX API.
        </p>
      </header>

      <EmptyState
        icon={Key}
        title="No API keys"
        description="Create a key to start authenticating requests to the CourierX API."
      />
    </div>
  );
}
