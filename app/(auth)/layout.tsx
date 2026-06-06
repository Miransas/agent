import Link from "next/link";

import { Logomark } from "@/components/brand/logomark";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="px-8 py-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2.5 text-foreground"
        >
          <Logomark size={24} />
          <span className="text-[15px] font-semibold tracking-tight">
            CourierX
          </span>
        </Link>
      </header>
      <main className="flex flex-1 items-center justify-center px-6 pb-16">
        <div className="w-full max-w-sm">{children}</div>
      </main>
    </div>
  );
}
