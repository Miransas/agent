"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Check, Copy, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { api, type CreateApiKeyResponse } from "@/lib/api";

interface CreateApiKeyModalProps {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function CreateApiKeyModal({
  open,
  onClose,
  onCreated,
}: CreateApiKeyModalProps) {
  const [name, setName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createdKey, setCreatedKey] =
    useState<CreateApiKeyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!open) {
      setName("");
      setCreatedKey(null);
      setError(null);
      setCopied(false);
      setIsSubmitting(false);
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Please enter a name");
      return;
    }
    setError(null);
    setIsSubmitting(true);

    try {
      const res = await api.apiKeys.create(trimmed);
      setCreatedKey(res);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to create key";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCopy = async () => {
    if (!createdKey) return;
    try {
      await navigator.clipboard.writeText(createdKey.key);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Copy failed — select the key and copy manually.");
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="w-full max-w-lg overflow-hidden rounded-xl border border-white/[0.08] bg-[#0a0a0a] shadow-[0_20px_60px_-20px_rgba(0,0,0,0.8)]">
        <div className="flex items-center justify-between border-b border-white/[0.06] px-6 py-4">
          <h3 className="text-base font-semibold text-foreground">
            {createdKey ? "API key created" : "Create API key"}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-zinc-500 transition-colors hover:bg-white/[0.04] hover:text-foreground"
            aria-label="Close"
          >
            <X className="size-4" />
          </button>
        </div>

        <div className="p-6">
          {!createdKey ? (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label
                  htmlFor="api-key-name"
                  className="mb-2 block text-sm font-medium text-zinc-300"
                >
                  Name
                </label>
                <input
                  id="api-key-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Production server"
                  autoFocus
                  className="w-full rounded-lg border border-white/[0.08] bg-white/[0.02] px-4 py-3 text-sm text-foreground placeholder:text-zinc-500 transition-colors focus:border-accent/40 focus:outline-none focus:ring-2 focus:ring-accent/10"
                />
                <p className="mt-1.5 text-xs text-zinc-500">
                  Give this key a recognizable name so you can identify it later.
                </p>
              </div>

              {error ? (
                <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              ) : null}

              <div className="flex items-center justify-end gap-2 pt-2">
                <Button
                  variant="ghost"
                  type="button"
                  onClick={onClose}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Creating..." : "Create key"}
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-5">
              <div className="flex items-start gap-3 rounded-lg border border-amber-500/20 bg-amber-500/5 px-4 py-3">
                <AlertTriangle className="mt-0.5 size-4 flex-shrink-0 text-amber-400" />
                <div className="text-sm text-amber-200">
                  <strong className="font-semibold">
                    This is the only time you&apos;ll see this key.
                  </strong>
                  <p className="mt-1 text-amber-200/80">
                    Copy it now and store it somewhere safe. If you lose it,
                    you&apos;ll need to create a new one.
                  </p>
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-zinc-300">
                  API key
                </label>
                <div className="relative">
                  <div className="break-all rounded-lg border border-white/[0.08] bg-white/[0.02] px-4 py-4 pr-12 font-mono text-sm text-accent">
                    {createdKey.key}
                  </div>
                  <button
                    type="button"
                    onClick={handleCopy}
                    className="absolute right-3 top-3 rounded-md bg-white/[0.04] p-2 text-zinc-400 transition-colors hover:bg-white/[0.08] hover:text-foreground"
                    title="Copy to clipboard"
                    aria-label="Copy API key"
                  >
                    {copied ? (
                      <Check className="size-4 text-accent" />
                    ) : (
                      <Copy className="size-4" />
                    )}
                  </button>
                </div>
              </div>

              <div className="rounded-md border border-white/[0.04] bg-white/[0.02] p-3 font-mono text-xs text-zinc-500">
                <span className="text-zinc-600">
                  Use this key in the Authorization header:
                </span>
                <div className="mt-1 break-all text-zinc-300">
                  Authorization: Bearer {createdKey.key_prefix}...
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <Button onClick={onCreated}>Done</Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
