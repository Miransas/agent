import type { ReactNode } from "react";
import { Code, Database, Mail, Zap } from "lucide-react";
import Image from "next/image";
import { Logomark } from "@/components/brand/logomark";

interface AuthBrandPanelProps {
  variant?: "login" | "register";
}

export function AuthBrandPanel({ variant = "login" }: AuthBrandPanelProps) {
  const eyebrow = variant === "register" ? "GET STARTED" : "WELCOME BACK";
  const description =
    variant === "register"
      ? "Drop-in Resend-compatible API, full source code, and a worker you can self-host."
      : "Pick up where you left off. Manage your domains, API keys, and email logs from one place.";

  return (
    <div className="relative hidden h-full overflow-hidden border-r border-white/[0.06] bg-[#0a0a0a] p-12 md:flex md:flex-col md:justify-between">
      <div className="pointer-events-none absolute inset-0">
        <div
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage:
              "radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px)",
            backgroundSize: "32px 32px",
            maskImage:
              "radial-gradient(ellipse at center, black 30%, transparent 80%)",
            WebkitMaskImage:
              "radial-gradient(ellipse at center, black 30%, transparent 80%)",
          }}
        />
        <div
          className="absolute -bottom-32 -left-32 h-[500px] w-[500px] rounded-full"
          style={{
            background: "#8CFF2E",
            opacity: 0.05,
            filter: "blur(140px)",
          }}
        />
      </div>

      <div className="relative z-10 flex items-center gap-3">
        <Image src="/favicon/favicon.svg" alt="CourierX" width={32} height={32} />
        <span className="text-xl font-bold tracking-tight text-foreground">
          CourierX
        </span>
      </div>

      <div className="relative z-10 max-w-md space-y-8">
        <div>
          <div className="mb-4 font-mono text-xs font-medium uppercase tracking-[0.2em] text-[#8CFF2E]">
            {eyebrow}
          </div>
          <h1 className="text-4xl font-bold leading-[1.1] tracking-tight text-foreground lg:text-5xl">
            {variant === "register" ? (
              <>
                The open-source
                <br />
                email API for{" "}
                <span className="text-[#8CFF2E]">developers</span>
              </>
            ) : (
              <>
                Send your first
                <br />
                email in <span className="text-[#8CFF2E]">5 minutes</span>
              </>
            )}
          </h1>
          <p className="mt-6 text-base leading-relaxed text-zinc-400">
            {description}
          </p>
        </div>

        <div className="space-y-3">
          <FeatureItem
            icon={<Code className="size-4" />}
            text="Resend-compatible API surface"
          />
          <FeatureItem
            icon={<Database className="size-4" />}
            text="Postgres-backed queue, no Redis"
          />
          <FeatureItem
            icon={<Zap className="size-4" />}
            text="Open source, self-host forever"
          />
          <FeatureItem
            icon={<Mail className="size-4" />}
            text="Built on Rust + Tokio"
          />
        </div>
      </div>

      <div className="relative z-10 flex items-center justify-between text-xs text-zinc-600">
        <span>© 2026 Miransas</span>
        <a
          href="https://miransas.com"
          target="_blank"
          rel="noopener noreferrer"
          className="transition-colors hover:text-zinc-400"
        >
          miransas.com ↗
        </a>
      </div>
    </div>
  );
}

function FeatureItem({ icon, text }: { icon: ReactNode; text: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-zinc-300">
      <div className="flex size-7 items-center justify-center rounded-md border border-white/[0.06] bg-white/[0.03] text-[#8CFF2E]">
        {icon}
      </div>
      <span>{text}</span>
    </div>
  );
}
