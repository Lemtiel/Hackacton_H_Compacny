"use client";

import { useEffect, useRef, useState } from "react";

const KEY = "snapncash.onboarded";

// Illustrations aux couleurs du logo (bleu nuit, vert), au lieu d'émojis qui changent selon le téléphone.
const ART_SEARCH = (
  <svg width="68" height="68" viewBox="0 0 48 48" fill="none" aria-hidden>
    <rect x="5" y="9" width="26" height="20" rx="4" stroke="var(--ink)" strokeWidth="3" />
    <path d="M10 16h16M10 22h10" stroke="var(--ink)" strokeWidth="3" strokeLinecap="round" />
    <circle cx="31" cy="30" r="8" fill="var(--bg)" stroke="var(--ok)" strokeWidth="3.5" />
    <path d="M37 36l6 6" stroke="var(--ok)" strokeWidth="3.5" strokeLinecap="round" />
  </svg>
);
const ART_CHOICE = (
  <svg width="68" height="68" viewBox="0 0 48 48" fill="none" aria-hidden>
    <path d="M24 7v34M13 41h22" stroke="var(--ink)" strokeWidth="3" strokeLinecap="round" />
    <path d="M8 15h32" stroke="var(--ink)" strokeWidth="3" strokeLinecap="round" />
    <path d="M8 15l-5 11h10L8 15zM40 15l-5 11h10l-5-11z" stroke="var(--ink)" strokeWidth="2.5" strokeLinejoin="round" />
    <circle cx="24" cy="15" r="5.5" fill="var(--ok)" />
  </svg>
);

const SLIDES = [
  {
    title: "Une photo suffit.",
    text: "Photographiez un objet qui dort chez vous : console, smartphone, tablette, jeu vidéo. On le reconnaît en quelques secondes.",
    // eslint-disable-next-line @next/next/no-img-element
    art: <img src="/logo-icon.png" alt="" width={72} height={51} />,
  },
  {
    title: "On fait le tour des boutiques pour vous.",
    text: "Les prix d'occasion de votre objet, comparés en une à deux minutes. Vous n'avez rien à chercher.",
    art: ART_SEARCH,
  },
  {
    title: "Vous choisissez : vendre seul ou en magasin.",
    text: "On vous dit ce que vous gagnez dans chaque cas, et l'annonce est prête à copier. Vos objets restent dans Mon grenier.",
    art: ART_CHOICE,
  },
];

// Découverte au premier lancement : trois écrans qui se balaient au doigt (défilement natif aimanté).
export default function Onboarding() {
  const [open, setOpen] = useState(false);
  const [index, setIndex] = useState(0);
  const track = useRef<HTMLDivElement>(null);
  const settle = useRef<number | undefined>(undefined);

  useEffect(() => {
    try {
      if (!localStorage.getItem(KEY)) setOpen(true);
    } catch {
      /* stockage indisponible : pas de découverte */
    }
  }, []);

  function close() {
    try {
      localStorage.setItem(KEY, "1");
    } catch {
      /* ignoré */
    }
    setOpen(false);
  }

  function goTo(i: number) {
    const el = track.current;
    if (!el) return;
    const target = Math.min(Math.max(i, 0), SLIDES.length - 1);
    setIndex(target); // mis à jour tout de suite : un second clic pendant l'animation avance encore
    el.scrollTo({ left: target * el.clientWidth, behavior: "smooth" });
  }

  // Balayage au doigt : l'écran courant suit la position une fois le défilement posé.
  function onScroll() {
    const el = track.current;
    if (!el) return;
    window.clearTimeout(settle.current);
    settle.current = window.setTimeout(() => setIndex(Math.round(el.scrollLeft / el.clientWidth)), 120);
  }

  if (!open) return null;
  const last = index === SLIDES.length - 1;

  return (
    <div className="onboarding" role="dialog" aria-modal="true" aria-label="Découvrir Snap N Cash">
      <button className="link-btn onboarding-skip" onClick={close}>Passer</button>
      <div className="onboarding-track" ref={track} onScroll={onScroll}>
        {SLIDES.map((s) => (
          <section key={s.title} className="onboarding-slide">
            <div className="onboarding-inner">
              <div className="onboarding-art" aria-hidden>{s.art}</div>
              <h2 className="display" style={{ fontSize: "clamp(2rem, 8vw, 2.6rem)" }}>{s.title}</h2>
              <p className="lede">{s.text}</p>
            </div>
          </section>
        ))}
      </div>
      <div className="onboarding-foot">
        <div className="dots" aria-hidden>
          {SLIDES.map((_, i) => <span key={i} className="dots-dot" data-active={i === index} />)}
        </div>
        <button className="btn btn-primary" onClick={() => (last ? close() : goTo(index + 1))}>
          {last ? "Commencer" : "Suivant"}
        </button>
      </div>
    </div>
  );
}
