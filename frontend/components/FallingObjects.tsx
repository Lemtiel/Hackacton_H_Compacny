import type { ReactNode } from "react";

// Fond « Pop et cash » : des objets qui dorment dans les tiroirs tombent lentement derrière le contenu.
// Très transparents, jamais cliquables, immobiles si l'utilisateur demande moins d'animations (voir globals.css).

const ICONS: Record<string, ReactNode> = {
  console: (
    <>
      <rect x="3" y="8" width="26" height="16" rx="6" />
      <path d="M9 13v6M6 16h6" />
      <circle cx="21" cy="14" r="1.6" />
      <circle cx="24" cy="18" r="1.6" />
    </>
  ),
  phone: (
    <>
      <rect x="9" y="3" width="14" height="26" rx="3.5" />
      <path d="M14 25.5h4" />
    </>
  ),
  pad: (
    <>
      <path d="M8 11h16a5 5 0 0 1 5 5v3a4 4 0 0 1-7 2.6L20 19h-8l-2 2.6A4 4 0 0 1 3 19v-3a5 5 0 0 1 5-5Z" />
      <path d="M9 14v4M7 16h4" />
      <circle cx="22" cy="15" r="1.3" />
    </>
  ),
  headset: (
    <>
      <path d="M5 19v-3a11 11 0 0 1 22 0v3" />
      <rect x="4" y="18" width="6" height="9" rx="2.5" />
      <rect x="22" y="18" width="6" height="9" rx="2.5" />
    </>
  ),
  game: (
    <>
      <rect x="7" y="3" width="18" height="26" rx="2.5" />
      <path d="M7 8h18M12 17l4-3 4 3-4 3z" />
    </>
  ),
  coin: (
    <>
      <circle cx="16" cy="16" r="12" />
      <path d="M20.5 11.5a6 6 0 1 0 0 9M9 14.5h9M9 17.5h9" />
    </>
  ),
  tablet: (
    <>
      <rect x="4" y="6" width="24" height="20" rx="3" />
      <circle cx="16" cy="23" r="0.8" />
    </>
  ),
};

// Positions fixées à l'avance : même rendu côté serveur et navigateur, pas de saut à l'affichage.
const DROPS = [
  { icon: "console", left: 4, size: 64, dur: 26, delay: -3, rot: -12, tone: "ink" },
  { icon: "coin", left: 14, size: 36, dur: 19, delay: -11, rot: 20, tone: "ok" },
  { icon: "phone", left: 23, size: 46, dur: 23, delay: -17, rot: 10, tone: "action" },
  { icon: "pad", left: 34, size: 58, dur: 29, delay: -6, rot: -8, tone: "ink" },
  { icon: "coin", left: 45, size: 30, dur: 17, delay: -2, rot: -25, tone: "ok" },
  { icon: "headset", left: 55, size: 54, dur: 27, delay: -14, rot: 14, tone: "action" },
  { icon: "game", left: 66, size: 42, dur: 21, delay: -9, rot: -18, tone: "ink" },
  { icon: "coin", left: 75, size: 40, dur: 24, delay: -20, rot: 8, tone: "ok" },
  { icon: "tablet", left: 84, size: 56, dur: 31, delay: -12, rot: -6, tone: "action" },
  { icon: "phone", left: 93, size: 38, dur: 20, delay: -5, rot: 22, tone: "ink" },
  { icon: "coin", left: 9, size: 26, dur: 18, delay: -15, rot: 0, tone: "ok" },
  { icon: "game", left: 50, size: 34, dur: 25, delay: -22, rot: 12, tone: "action" },
  { icon: "console", left: 80, size: 48, dur: 28, delay: -1, rot: 16, tone: "ink" },
  { icon: "coin", left: 61, size: 28, dur: 16, delay: -8, rot: -14, tone: "ok" },
];

export default function FallingObjects() {
  return (
    <div className="falling" aria-hidden>
      {DROPS.map((d, i) => (
        <span
          key={i}
          className="falling-item"
          data-tone={d.tone}
          style={{
            left: `${d.left}%`,
            width: d.size,
            height: d.size,
            animationDuration: `${d.dur}s`,
            animationDelay: `${d.delay}s`,
            ["--rot" as string]: `${d.rot}deg`,
          }}
        >
          <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {ICONS[d.icon]}
          </svg>
        </span>
      ))}
    </div>
  );
}
