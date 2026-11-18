"use client";

import { useEffect, useRef, useState } from "react";
import { euros } from "@/lib/api";

const reduceMotion = () => {
  try {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch {
    return false;
  }
};

// Montant qui défile comme un compteur jusqu'à sa valeur (puis suit ses changements).
export function CountUp({ value, duration = 900 }: { value: number; duration?: number }) {
  const [shown, setShown] = useState(value);
  const from = useRef(0);
  useEffect(() => {
    if (reduceMotion()) {
      setShown(value);
      from.current = value;
      return;
    }
    const start = performance.now();
    const a = from.current;
    let raf = 0;
    const tick = (t: number) => {
      const k = Math.min((t - start) / duration, 1);
      const eased = 1 - Math.pow(1 - k, 3);
      setShown(Math.round(a + (value - a) * eased));
      if (k < 1) raf = requestAnimationFrame(tick);
      else from.current = value;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value, duration]);
  return <span className="num">{euros(shown)}</span>;
}

// Petite pluie de pièces, une seule fois, quand le verdict apparaît.
export function CoinRain({ count = 16 }: { count?: number }) {
  const [on, setOn] = useState(false);
  useEffect(() => {
    if (reduceMotion()) return;
    setOn(true);
    const t = setTimeout(() => setOn(false), 2600);
    return () => clearTimeout(t);
  }, []);
  if (!on) return null;
  return (
    <div className="coin-rain" aria-hidden>
      {Array.from({ length: count }, (_, i) => (
        <span
          key={i}
          className="coin"
          style={{
            left: `${(i * 61) % 100}%`,
            animationDelay: `${(i % 6) * 0.12}s`,
            animationDuration: `${1.4 + (i % 4) * 0.25}s`,
            ["--drift" as string]: `${((i % 5) - 2) * 14}px`,
          }}
        >
          €
        </span>
      ))}
    </div>
  );
}
