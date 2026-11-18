"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { type ReactNode, useEffect, useRef, useState } from "react";
import { onGrenierChange, readGrenier } from "@/lib/grenier";
import { setPendingPhoto } from "@/lib/pending";

// Barre du bas : 4 onglets et, au centre, le bouton « Estimer » qui ouvre directement l'appareil photo.
export default function TabBar() {
  const path = usePathname();
  const router = useRouter();
  const [count, setCount] = useState(0);
  const camera = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const refresh = () => setCount(readGrenier().filter((x) => x.status !== "vendu").length);
    refresh();
    return onGrenierChange(refresh);
  }, []);

  const left = [
    { href: "/", label: "Accueil", icon: <HomeGlyph /> },
    { href: "/grenier", label: "Grenier", icon: <BoxGlyph />, badge: count },
  ];
  const right = [
    { href: "/compte", label: "Compte", icon: <UserGlyph /> },
    { href: "/reglages", label: "Réglages", icon: <GearGlyph /> },
  ];

  const tab = (t: { href: string; label: string; icon: ReactNode; badge?: number }) => {
    const active = t.href === "/" ? path === "/" : path.startsWith(t.href) || (t.href === "/reglages" && path.startsWith("/legal"));
    return (
      <Link key={t.href} href={t.href} className="tab" aria-current={active ? "page" : undefined}>
        <span className="tab-icon">
          {t.icon}
          {t.badge ? <span className="tab-badge num">{t.badge}</span> : null}
        </span>
        <span>{t.label}</span>
      </Link>
    );
  };

  return (
    <nav className="tabbar" aria-label="Navigation principale">
      {left.map(tab)}
      <button type="button" className="tab-fab" onClick={() => camera.current?.click()} aria-label="Estimer un objet : prendre une photo">
        <span className="tab-fab-circle"><CameraGlyph /></span>
        <span className="tab-fab-label">Estimer</span>
      </button>
      <input
        ref={camera}
        type="file"
        accept="image/*"
        capture="environment"
        className="sr-only"
        onChange={(e) => {
          const f = e.target.files?.[0];
          e.target.value = "";
          if (!f) return;
          setPendingPhoto(f);
          if (path !== "/") router.push("/");
        }}
      />
      {right.map(tab)}
    </nav>
  );
}

const glyph = { width: 24, height: 24, viewBox: "0 0 24 24", fill: "none", "aria-hidden": true } as const;

function HomeGlyph() {
  return <svg {...glyph}><path d="M4 11 12 4l8 7v8.5a1 1 0 0 1-1 1h-4.5V15h-5v5.5H5a1 1 0 0 1-1-1V11Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></svg>;
}
function BoxGlyph() {
  return (
    <svg {...glyph}>
      <path d="M3.5 8 12 4l8.5 4v8L12 20l-8.5-4V8Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M3.5 8 12 12l8.5-4M12 12v8" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    </svg>
  );
}
function UserGlyph() {
  return <svg {...glyph}><circle cx="12" cy="8.5" r="3.8" stroke="currentColor" strokeWidth="1.8" /><path d="M4.5 20c1.4-3.4 4.2-5 7.5-5s6.1 1.6 7.5 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>;
}
function GearGlyph() {
  return (
    <svg {...glyph}>
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M5.6 18.4l1.8-1.8M16.6 7.4l1.8-1.8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function CameraGlyph() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.3l1.2-1.6A1 1 0 0 1 9.8 4h4.4a1 1 0 0 1 .8.4L16.2 6h1.3A2.5 2.5 0 0 1 20 8.5v8a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 16.5v-8Z" stroke="currentColor" strokeWidth="1.9" />
      <circle cx="12" cy="12.5" r="3.5" stroke="currentColor" strokeWidth="1.9" />
    </svg>
  );
}
