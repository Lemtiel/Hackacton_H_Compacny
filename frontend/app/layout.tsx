import type { Metadata, Viewport } from "next";
import Link from "next/link";
import "./globals.css";
import TabBar from "@/components/TabBar";
import Onboarding from "@/components/Onboarding";

export const metadata: Metadata = {
  title: "Snap N Cash",
  description: "Une photo, le bon prix, l'annonce prête. Estimez la valeur de revente de vos objets high-tech et jeux vidéo.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#ffffff" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>
        <header className="topbar">
          <Link href="/" className="wordmark">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo-icon.png" alt="" width={34} height={24} className="wordmark-icon" />
            Snap <span>N</span> Cash
          </Link>
          <Link href="/comment-ca-marche" className="small">
            Comment ça marche
          </Link>
        </header>
        {children}
        <TabBar />
        <Onboarding />
      </body>
    </html>
  );
}
