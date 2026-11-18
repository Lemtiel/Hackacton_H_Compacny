"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { DEFAULT_PREFS, type Prefs, type Theme, onPrefsChange, readPrefs, writePrefs } from "@/lib/prefs";
import { LEGAL_PAGES } from "@/lib/legal";

const THEMES: { key: Theme; label: string }[] = [
  { key: "system", label: "Auto" },
  { key: "light", label: "Clair" },
  { key: "dark", label: "Sombre" },
];

export default function SettingsPage() {
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS);
  const [confirm, setConfirm] = useState(false);
  const [cleared, setCleared] = useState(false);

  useEffect(() => {
    setPrefs(readPrefs());
    return onPrefsChange(() => setPrefs(readPrefs()));
  }, []);

  function clearData() {
    try {
      localStorage.removeItem("snapncash.grenier");
      window.dispatchEvent(new Event("snapncash:grenier"));
    } catch {
      /* rien à effacer */
    }
    setConfirm(false);
    setCleared(true);
  }

  return (
    <main className="page screen settings">
      <h1 className="display search-title">Réglages</h1>

      <section className="settings-group" aria-labelledby="g-apparence">
        <h2 id="g-apparence">Apparence</h2>
        <div className="settings-row">
          <span>Thème</span>
          <div className="seg" role="group" aria-label="Thème">
            {THEMES.map((t) => (
              <button key={t.key} type="button" aria-pressed={prefs.theme === t.key} onClick={() => writePrefs({ theme: t.key })}>{t.label}</button>
            ))}
          </div>
        </div>
        <label className="settings-row" htmlFor="motion">
          <span>Objets animés en fond<span className="small settings-hint">Coupés automatiquement si votre téléphone limite les animations.</span></span>
          <input id="motion" type="checkbox" className="switch" checked={prefs.motion} onChange={(e) => writePrefs({ motion: e.target.checked })} />
        </label>
      </section>

      <section className="settings-group" aria-labelledby="g-demo">
        <h2 id="g-demo">Démonstration</h2>
        <label className="settings-row" htmlFor="demo">
          <span>Mode démo<span className="small settings-hint">Montre l&apos;écran de chaque agent pendant la recherche.</span></span>
          <input id="demo" type="checkbox" className="switch" checked={prefs.demo} onChange={(e) => writePrefs({ demo: e.target.checked })} />
        </label>
      </section>

      <section className="settings-group" aria-labelledby="g-region">
        <h2 id="g-region">Langue et devise</h2>
        <div className="settings-row">
          <span>Langue</span>
          <span className="settings-value">Français</span>
        </div>
        <div className="settings-row">
          <span>Devise<span className="small settings-hint">Les prix viennent de boutiques françaises.</span></span>
          <span className="settings-value">Euro (€)</span>
        </div>
        <p className="small settings-note">D&apos;autres langues et devises arriveront avec l&apos;ouverture à d&apos;autres pays.</p>
      </section>

      <section className="settings-group" aria-labelledby="g-donnees">
        <h2 id="g-donnees">Vos données</h2>
        <p className="small settings-note">Mon grenier et vos réglages restent sur cet appareil. Rien n&apos;est gardé sur nos serveurs.</p>
        {!confirm ? (
          <button type="button" className="settings-row settings-danger" onClick={() => { setConfirm(true); setCleared(false); }}>
            <span>Effacer Mon grenier</span><span aria-hidden>›</span>
          </button>
        ) : (
          <div className="settings-confirm" role="alertdialog" aria-label="Confirmer l'effacement">
            <p>Effacer tous les objets de Mon grenier sur cet appareil ? Impossible d&apos;annuler.</p>
            <div className="settings-confirm-actions">
              <button type="button" className="btn btn-quiet" onClick={() => setConfirm(false)}>Annuler</button>
              <button type="button" className="btn btn-danger" onClick={clearData}>Effacer</button>
            </div>
          </div>
        )}
        {cleared && <p className="small" role="status" style={{ margin: "0.5rem 0 0" }}>Mon grenier est vide.</p>}
      </section>

      <section className="settings-group" aria-labelledby="g-aide">
        <h2 id="g-aide">Aide</h2>
        <Link href="/comment-ca-marche" className="settings-row"><span>Comment ça marche</span><span aria-hidden>›</span></Link>
        <Link href="/legal/contact" className="settings-row"><span>Nous contacter</span><span aria-hidden>›</span></Link>
      </section>

      <section className="settings-group" aria-labelledby="g-legal">
        <h2 id="g-legal">Informations légales</h2>
        {LEGAL_PAGES.filter((p) => p.slug !== "contact").map((p) => (
          <Link key={p.slug} href={`/legal/${p.slug}`} className="settings-row">
            <span>{p.title}<span className="small settings-hint">{p.summary}</span></span><span aria-hidden>›</span>
          </Link>
        ))}
      </section>

      <p className="small settings-note" style={{ textAlign: "center", marginTop: "1.5rem" }}>
        Snap N Cash · prototype du hackathon Eugenia School × H Company, novembre 2026
      </p>
    </main>
  );
}
