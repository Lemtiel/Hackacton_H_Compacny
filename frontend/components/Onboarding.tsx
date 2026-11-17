"use client";

import { useEffect, useRef, useState } from "react";

const KEY = "snapncash.onboarded";

const SLIDES = [
  {
    title: "Une photo suffit.",
    text: "Photographiez un objet qui dort chez vous : console, smartphone, tablette, jeu vidéo. On le reconnaît en quelques secondes.",
    art: "📸",
  },
  {
    title: "Nos agents font le tour des boutiques.",
    text: "Ils consultent les boutiques d'occasion comme vous le feriez, et relèvent les vrais prix. Vous les voyez travailler en direct.",
    art: "🔎",
  },
  {
    title: "Vous choisissez : vendre seul ou en magasin.",
    text: "On vous dit ce que vous gagnez dans chaque cas, et l'annonce est prête à copier. Vos objets restent dans Mon grenier.",
    art: "💶",
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
