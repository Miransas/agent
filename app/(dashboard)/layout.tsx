import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { DashboardGuard } from "@/components/provider/dashboard-guard";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DashboardGuard>
      <DashboardShell>{children}</DashboardShell>
    </DashboardGuard>
  );
}
