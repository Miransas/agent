"use client";

import { useCallback, useEffect, useState } from "react";
import { Key, Plus, Trash2 } from "lucide-react";

import { CreateApiKeyModal } from "@/components/dashboard/create-api-key-modal";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { api, type ApiKey } from "@/lib/api";

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadKeys = useCallback(async () => {
    try {
      const res = await api.apiKeys.list();
      setKeys(res.keys);
      setLoadError(null);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load API keys";
      setLoadError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadKeys();
  }, [loadKeys]);

  const handleKeyCreated = () => {
    setIsModalOpen(false);
    loadKeys();
  };

  const handleRevoke = async (id: string, name: string) => {
    if (!confirm(`Revoke API key "${name}"? This cannot be undone.`)) return;
    try {
      await api.apiKeys.revoke(id);
      loadKeys();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to revoke key";
      alert(message);
    }
  };

  return (
    <div className="space-y-8">
      <header className="flex items-start justify-between gap-4">
        <div className="space-y-1.5">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            API Keys
          </h1>
          <p className="text-sm text-zinc-400">
            Authenticate requests to the CourierX API with bearer tokens.
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="size-4" />
          Create key
        </Button>
      </header>

      {isLoading ? (
        <Card className="p-8 text-center text-sm text-zinc-500">Loading…</Card>
      ) : loadError ? (
        <Card className="border-red-500/20 bg-red-500/5 p-6 text-sm text-red-300">
          {loadError}
        </Card>
      ) : keys.length === 0 ? (
        <EmptyState
          icon={Key}
          title="No API keys"
          description="Create an API key to start sending email from your application."
          action={
            <Button onClick={() => setIsModalOpen(true)}>
              <Plus className="size-4" />
              Create your first key
            </Button>
          }
        />
      ) : (
        <Card className="overflow-hidden p-0">
          <div className="divide-y divide-white/[0.04]">
            {keys.map((key) => (
              <ApiKeyRow
                key={key.id}
                apiKey={key}
                onRevoke={() => handleRevoke(key.id, key.name)}
              />
            ))}
          </div>
        </Card>
      )}

      <CreateApiKeyModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreated={handleKeyCreated}
      />
    </div>
  );
}

function ApiKeyRow({
  apiKey,
  onRevoke,
}: {
  apiKey: ApiKey;
  onRevoke: () => void;
}) {
  const isRevoked = apiKey.revoked_at !== null;
  const dateStr = new Date(apiKey.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="flex items-center gap-4 px-6 py-4 transition-colors hover:bg-white/[0.02]">
      <div
        className={
          isRevoked
            ? "size-2 rounded-full bg-zinc-600"
            : "size-2 rounded-full bg-accent shadow-[0_0_6px_rgba(140,255,46,0.6)]"
        }
      />

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span
            className={
              isRevoked
                ? "text-sm font-medium text-zinc-500"
                : "text-sm font-medium text-foreground"
            }
          >
            {apiKey.name}
          </span>
          {isRevoked ? (
            <span className="font-mono text-[10px] uppercase tracking-wider text-zinc-600">
              Revoked
            </span>
          ) : null}
        </div>
        <div className="mt-0.5 font-mono text-xs text-zinc-500">
          {apiKey.key_prefix}••••••••••••
        </div>
      </div>

      <div className="font-mono text-xs text-zinc-500">{dateStr}</div>

      {!isRevoked ? (
        <button
          type="button"
          onClick={onRevoke}
          className="rounded-md p-2 text-zinc-500 transition-colors hover:bg-white/[0.05] hover:text-red-400"
          title="Revoke key"
          aria-label={`Revoke ${apiKey.name}`}
        >
          <Trash2 className="size-4" />
        </button>
      ) : null}
    </div>
  );
}
