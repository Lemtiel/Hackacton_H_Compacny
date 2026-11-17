"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { onGrenierChange, readGrenier } from "@/lib/grenier";

// Barre d'onglets translucide, en bas comme sur iPhone.
export default function TabBar() {
  const path = usePathname();
  const [count, setCount] = useState(0);

  useEffect(() => {
    const refresh = () => setCount(readGrenier().filter((x) => x.status !== "vendu").length);
    refresh();
    return onGrenierChange(refresh);
  }, []);

  const tabs = [
    { href: "/", label: "Estimer", icon: <CameraGlyph /> },
    { href: "/grenier", label: "Mon grenier", icon: <BoxGlyph />, badge: count },
  ];

  return (
    <nav className="tabbar" aria-label="Navigation principale">
      {tabs.map((t) => {
        const active = t.href === "/" ? path === "/" : path.startsWith(t.href);
        return (
          <Link key={t.href} href={t.href} className="tab" aria-current={active ? "page" : undefined}>
            <span className="tab-icon">
              {t.icon}
              {t.badge ? <span className="tab-badge num">{t.badge}</span> : null}
            </span>
            <span>{t.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

function CameraGlyph() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.3l1.2-1.6A1 1 0 0 1 9.8 4h4.4a1 1 0 0 1 .8.4L16.2 6h1.3A2.5 2.5 0 0 1 20 8.5v8a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 16.5v-8Z" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="12" cy="12.5" r="3.5" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function BoxGlyph() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M3.5 8 12 4l8.5 4v8L12 20l-8.5-4V8Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M3.5 8 12 12l8.5-4M12 12v8" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    </svg>
  );
}
