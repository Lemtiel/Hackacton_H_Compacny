import type { Metadata, Viewport } from "next";
import Link from "next/link";
import "./globals.css";
import TabBar from "@/components/TabBar";
import Onboarding from "@/components/Onboarding";
import FallingObjects from "@/components/FallingObjects";
import { PREFS_BOOT_SCRIPT } from "@/lib/prefs";

export const metadata: Metadata = {
  title: "Snap N Cash",
  description: "Une photo, le bon prix, l'annonce prête. Estimez la valeur de revente de vos objets high-tech et jeux vidéo.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: [{ media: "(prefers-color-scheme: light)", color: "#f7fafe" }, { media: "(prefers-color-scheme: dark)", color: "#0b1424" }] };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: PREFS_BOOT_SCRIPT }} />
      </head>
      <body>
        <FallingObjects />
        <header className="topbar">
          <Link href="/" className="wordmark">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo-icon.png" alt="" width={34} height={24} className="wordmark-icon logo-light" />
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo-icon-dark.png" alt="" width={34} height={24} className="wordmark-icon logo-dark" />
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
