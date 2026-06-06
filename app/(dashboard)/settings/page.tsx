import { Settings as SettingsIcon } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";

export default function SettingsPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Settings
        </h1>
        <p className="text-sm text-zinc-400">
          Manage your workspace, billing, and team.
        </p>
      </header>

      <EmptyState
        icon={SettingsIcon}
        title="Nothing to configure yet"
        description="Workspace, billing, and team settings will live here."
      />
    </div>
  );
}
