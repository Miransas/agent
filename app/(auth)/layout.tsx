
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex justify-center">
          {/* /* Logo veya başlık buraya gelecek */ }
        </div>
        <div className="rounded-xl border border-gray-800 bg-[var(--bg-elevated)] p-6">
          {children}
        </div>
        <footer className="mt-8 text-center text-xs text-gray-500">
          © 2026 CourierX · Part of Miransas
        </footer>
      </div>
    </div>
  );
}