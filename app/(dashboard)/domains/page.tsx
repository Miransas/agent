"use client";

import { Globe } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";

export default function DomainsPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Domains
        </h1>
        <p className="text-sm text-zinc-400">
          Verify your sending domains with SPF, DKIM, and DMARC records.
        </p>
      </header>

      <EmptyState
        icon={Globe}
        title="No domains yet"
        description="Add a domain to start sending emails from your own address."
        action={
          <Button onClick={() => console.log("TODO: add domain")}>
            Add domain
          </Button>
        }
      />
    </div>
  );
}
