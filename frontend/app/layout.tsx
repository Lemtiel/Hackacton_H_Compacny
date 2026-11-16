import type { Metadata, Viewport } from "next";
import Link from "next/link";
import "./globals.css";

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
            Snap N <span>Cash</span>
          </Link>
          <Link href="/comment-ca-marche" className="small">
            Comment ça marche
          </Link>
        </header>
        {children}
      </body>
    </html>
  );
}
