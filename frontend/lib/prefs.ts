// Réglages de l'app, gardés dans ce navigateur (localStorage). Aucun ne part sur un serveur.
export type Theme = "system" | "light" | "dark";
export type Prefs = { theme: Theme; motion: boolean; demo: boolean };

const KEY = "snapncash.prefs";
const EVENT = "snapncash:prefs";
export const DEFAULT_PREFS: Prefs = { theme: "system", motion: true, demo: false };

export function readPrefs(): Prefs {
  try {
    return { ...DEFAULT_PREFS, ...JSON.parse(localStorage.getItem(KEY) || "{}") };
  } catch {
    return DEFAULT_PREFS;
  }
}

export function writePrefs(patch: Partial<Prefs>) {
  const next = { ...readPrefs(), ...patch };
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    /* stockage indisponible : le réglage vaut pour cette visite seulement */
  }
  applyPrefs(next);
  window.dispatchEvent(new Event(EVENT));
  return next;
}

export function onPrefsChange(cb: () => void) {
  window.addEventListener(EVENT, cb);
  return () => window.removeEventListener(EVENT, cb);
}

// Thème et animations posés sur <html> : le CSS s'en sert (data-theme, data-motion).
export function applyPrefs(p: Prefs) {
  const root = document.documentElement;
  if (p.theme === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", p.theme);
  root.setAttribute("data-motion", p.motion ? "on" : "off");
}

// Script lancé avant l'affichage (dans layout.tsx) : pas de flash clair en mode sombre.
export const PREFS_BOOT_SCRIPT = `try{var p=JSON.parse(localStorage.getItem("${KEY}")||"{}");var r=document.documentElement;if(p.theme==="light"||p.theme==="dark")r.setAttribute("data-theme",p.theme);r.setAttribute("data-motion",p.motion===false?"off":"on");}catch(e){}`;
