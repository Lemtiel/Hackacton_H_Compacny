"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { euros } from "@/lib/api";
import { onGrenierChange, readGrenier, totals } from "@/lib/grenier";

// Pas de compte dans le prototype (Specs : utilisation anonyme). La page le dit et montre ce qui est sur cet appareil.
export default function AccountPage() {
  const [t, setT] = useState<ReturnType<typeof totals> | null>(null);
  useEffect(() => {
    const refresh = () => setT(totals(readGrenier()));
    refresh();
    return onGrenierChange(refresh);
  }, []);

  return (
    <main className="page screen account">
      <h1 className="display search-title">Mon compte</h1>

      <div className="account-card">
        <div className="account-avatar" aria-hidden>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><circle cx="12" cy="9" r="4" /><path d="M4 20c1.5-3.5 4.5-5 8-5s6.5 1.5 8 5" strokeLinecap="round" /></svg>
        </div>
        <div>
          <strong>Utilisation sans compte</strong>
          <p className="small" style={{ margin: "0.2rem 0 0" }}>Aucune inscription : vos estimations restent sur cet appareil.</p>
        </div>
      </div>

      {t && (
        <div className="account-stats">
          <div><span className="num account-stat">{t.count}</span><span className="small">objet{t.count > 1 ? "s" : ""} estimé{t.count > 1 ? "s" : ""}</span></div>
          <div><span className="num account-stat">{euros(t.sleepingValue)}</span><span className="small">qui dorment encore</span></div>
          <div><span className="num account-stat cash">{euros(t.earned)}</span><span className="small">déjà gagnés</span></div>
        </div>
      )}

      <div className="panel">
        <h3>Bientôt</h3>
        <p className="small" style={{ margin: 0 }}>
          Un compte pour retrouver Mon grenier sur tous vos appareils, suivre l&apos;évolution des prix de vos objets et publier plus vite.
        </p>
      </div>

      <div className="stack" style={{ marginTop: "1.5rem" }}>
        <Link href="/grenier" className="btn btn-quiet">Voir Mon grenier</Link>
        <Link href="/reglages" className="btn btn-quiet">Réglages</Link>
      </div>
    </main>
  );
}
