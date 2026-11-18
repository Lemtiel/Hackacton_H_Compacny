// Photo prise avec le bouton central « Estimer » de la barre du bas : elle attend que l'accueil la récupère.
let pending: File | null = null;
const EVENT = "snapncash:photo";

export function setPendingPhoto(file: File) {
  pending = file;
  window.dispatchEvent(new Event(EVENT));
}

export function takePendingPhoto(): File | null {
  const f = pending;
  pending = null;
  return f;
}

export function onPendingPhoto(cb: () => void) {
  window.addEventListener(EVENT, cb);
  return () => window.removeEventListener(EVENT, cb);
}
