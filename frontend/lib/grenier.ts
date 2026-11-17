// « Mon grenier » : les objets estimés, gardés uniquement dans ce navigateur (rien sur notre serveur).
export type ItemStatus = "a_vendre" | "en_vente" | "vendu";

export const STATUS_LABELS: Record<ItemStatus, string> = {
  a_vendre: "À vendre",
  en_vente: "En vente",
  vendu: "Vendu",
};

export type GrenierItem = {
  id: string;
  product: string;
  category: string;
  condition: string;
  date: string;
  buyback: number | null; // rachat estimé en magasin
  sellAloneLow: number | null;
  sellAloneHigh: number | null;
  myPrice: number | null; // prix choisi avec le curseur
  status: ItemStatus;
  platform?: string; // où l'annonce a été publiée
  soldPrice?: number | null;
};

const KEY = "snapncash.grenier";
const EVENT = "snapncash:grenier";

export function readGrenier(): GrenierItem[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]");
  } catch {
    return [];
  }
}

function write(list: GrenierItem[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
    window.dispatchEvent(new Event(EVENT));
  } catch {
    /* stockage indisponible : le grenier reste vide */
  }
}

export function upsertItem(item: GrenierItem) {
  const list = readGrenier();
  const i = list.findIndex((x) => x.id === item.id);
  if (i >= 0) list[i] = item;
  else list.unshift(item);
  write(list.slice(0, 100));
}

export function updateItem(id: string, patch: Partial<GrenierItem>) {
  write(readGrenier().map((x) => (x.id === id ? { ...x, ...patch } : x)));
}

export function removeItem(id: string) {
  write(readGrenier().filter((x) => x.id !== id));
}

export function onGrenierChange(cb: () => void) {
  window.addEventListener(EVENT, cb);
  window.addEventListener("storage", cb);
  return () => {
    window.removeEventListener(EVENT, cb);
    window.removeEventListener("storage", cb);
  };
}

// Valeur d'un objet : prix réellement vendu, sinon prix choisi, sinon estimation basse.
export function itemValue(x: GrenierItem): number {
  if (x.status === "vendu" && x.soldPrice) return x.soldPrice;
  return x.myPrice ?? x.sellAloneLow ?? x.buyback ?? 0;
}

export function totals(list: GrenierItem[]) {
  const unsold = list.filter((x) => x.status !== "vendu");
  const sold = list.filter((x) => x.status === "vendu");
  return {
    count: list.length,
    sleepingValue: unsold.reduce((s, x) => s + itemValue(x), 0),
    earned: sold.reduce((s, x) => s + (x.soldPrice ?? itemValue(x)), 0),
    soldCount: sold.length,
  };
}

export function newId() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
}
