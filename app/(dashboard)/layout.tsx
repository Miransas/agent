import { TopBar } from "../../components/shared/navbar";
import { Sidebar } from "../../components/shared/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-[var(--bg)] text-[var(--text)] antialiased selection:bg-brand/20 selection:text-brand">
      {/* Sol Sidebar - Genişliği içerideki state'e göre pürüzsüzce değişir */}
      <Sidebar />

      {/* Sağ Ana İçerik Alanı */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Üst Bar - Sabit yükseklik ve hafif saydamlık/blur modernlik katar */}
        <TopBar />

        {/* İçerik Alanı */}
        <main className="flex-1 overflow-y-auto px-6 py-6 md:px-8 md:py-8">
          <div className="mx-auto w-full max-w-7xl animate-in fade-in duration-200">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}