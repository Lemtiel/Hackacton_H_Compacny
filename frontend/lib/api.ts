// Appels au serveur FastAPI (backend/main.py).
export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

export type Category = "smartphone" | "console" | "jeu_video" | "tablette" | "informatique";

export const CATEGORY_LABELS: Record<Category, string> = {
  smartphone: "Smartphone",
  console: "Console",
  jeu_video: "Jeu vidéo",
  tablette: "Tablette",
  informatique: "Informatique",
};

export type Identification = {
  is_object: boolean;
  brand?: string | null;
  model?: string | null;
  variant?: string | null;
  category: string;
  condition?: string | null;
  confidence: number;
  product: string;
  kind?: string | null; // description générique pour élargir la recherche : « manette PS5 »
};

export type Offer = { title: string; price_eur: number; condition?: string | null; url?: string | null };

export type SiteState = "attente" | "en_cours" | "ok" | "aucun_resultat" | "indisponible" | "hors_categorie";

export type SiteRow = {
  key: string;
  name: string;
  state: SiteState;
  label: string;
  elapsed_s?: number;
  offers: Offer[];
};

export type ShopBlock = {
  n_prices: number;
  n_kept: number;
  shop_low: number;
  shop_high: number;
  shop_median: number;
  coef: number;
  buyback_estimate: number;
  buyback_low: number;
  buyback_high: number;
};

// Jusqu'à 3 photos du même objet (face, dos ou étiquette, détail), envoyées ensemble.
export async function identifyPhotos(files: File[]): Promise<Identification> {
  const body = new FormData();
  files.slice(0, 3).forEach((f) => body.append("files", f));
  const res = await fetch(`${API_URL}/api/identify`, { method: "POST", body });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "L'identification a échoué. Tapez le nom de l'objet.");
  return data as Identification;
}

export type SearchEvent =
  | { type: "start"; product: string; category: string; sites: { key: string; name: string; active: boolean }[] }
  | { type: "site_step"; site: string; label?: string; elapsed_s?: number; steps?: number }
  | { type: "site_result"; site: string; state: "ok" | "aucun_resultat" | "indisponible"; duration_s?: number; offers: Offer[]; n_rejected?: number }
  | { type: "site_shot"; site: string; shot: string }
  | { type: "error"; message: string }
  | { type: "shop_block"; block: ShopBlock | null }
  | { type: "done" };

export type PriceSearchContext = {
  condition?: string;
  box?: boolean | null;
  accessories?: string;
  details?: string;
};

// Mode démo (pitch, vidéo) : ?demo=1 dans l'adresse de la page affiche les captures des agents.
export function isDemo(): boolean {
  try {
    if (new URLSearchParams(window.location.search).get("demo") === "1") return true;
    return JSON.parse(localStorage.getItem("snapncash.prefs") || "{}").demo === true; // interrupteur dans Réglages
  } catch {
    return false;
  }
}

export const shotUrl = (token: string) => `${API_URL}/api/shot/${encodeURIComponent(token)}`;

// Clé de démo : ouverte une fois avec ?cle=… dans l'adresse, gardée dans ce navigateur. Elle lève la limite par
// adresse IP côté serveur (DEMO_KEY), pour que la démo ne soit pas bloquée par les autres personnes du même Wi-Fi.
export function demoKey(): string {
  try {
    const fromUrl = new URLSearchParams(window.location.search).get("cle");
    if (fromUrl) localStorage.setItem("snapncash.cle", fromUrl);
    return localStorage.getItem("snapncash.cle") || "";
  } catch {
    return "";
  }
}

export function searchPrices(
  product: string,
  category: string,
  onEvent: (e: SearchEvent) => void,
  onError: () => void,
  demo = false,
  hint = "",
  context: PriceSearchContext = {},
) {
  const params = new URLSearchParams({ product, category });
  if (demo) params.set("demo", "1");
  if (hint) params.set("hint", hint);
  if (context.condition) params.set("condition", context.condition);
  if (context.box !== undefined && context.box !== null) params.set("box", String(context.box));
  if (context.accessories) params.set("accessories", context.accessories);
  if (context.details) params.set("details", context.details);
  const key = demoKey();
  if (key) params.set("key", key);
  const url = `${API_URL}/api/search?${params.toString()}`;
  const source = new EventSource(url);
  source.onmessage = (msg) => {
    const ev = JSON.parse(msg.data) as SearchEvent;
    onEvent(ev);
    if (ev.type === "done") source.close();
  };
  source.onerror = () => {
    source.close();
    onError();
  };
  return () => source.close();
}

// Recherche ouverte dans le navigateur de l'utilisateur : aucun agent ne lit ces sites.
export function marketplaceLinks(product: string) {
  const q = encodeURIComponent(product);
  return [
    { name: "Vinted", url: `https://www.vinted.fr/catalog?search_text=${q}` },
    { name: "Leboncoin", url: `https://www.leboncoin.fr/recherche?text=${q}` },
    { name: "eBay (ventes conclues)", url: `https://www.ebay.fr/sch/i.html?_nkw=${q}&LH_Sold=1&LH_Complete=1` },
  ];
}

export const euros = (n: number) =>
  new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);

export type ListingRequest = {
  product: string;
  category: string;
  condition: string;
  box: boolean | null;
  accessories: string;
  details: string;
};

// Rédaction de l'annonce en 4 formats par le serveur (environ 30 s).
export async function generateListing(req: ListingRequest): Promise<import("./listing").ListingFormat[]> {
  const res = await fetch(`${API_URL}/api/listing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "La rédaction a échoué. Réessayez dans un instant.");
  return data.formats;
}

// Bloc « Vendre seul (eBay) » : annonces eBay en cours via l'API officielle, jamais mélangées aux boutiques.
export type EbayBlock = {
  n_prices: number;
  n_kept: number;
  listed_low: number;
  listed_high: number;
  listed_median: number;
  discount: number;
  sell_low: number;
  sell_high: number;
  sell_price: number;
};

export type EbayResult = {
  state: "ok" | "aucun_resultat" | "indisponible" | "non_configure";
  block: EbayBlock | null;
  items: Offer[];
  n_found?: number;
  n_rejected?: number;
  duration_s?: number;
};

export async function fetchEbay(product: string, category: string, signal?: AbortSignal): Promise<EbayResult> {
  const url = `${API_URL}/api/ebay?product=${encodeURIComponent(product)}&category=${encodeURIComponent(category)}`;
  try {
    const res = await fetch(url, { signal });
    if (!res.ok) return { state: "indisponible", block: null, items: [] };
    return (await res.json()) as EbayResult;
  } catch {
    return { state: "indisponible", block: null, items: [] };
  }
}

// Aide à la publication sur eBay : catégorie suggérée par eBay (API Taxonomy), triée par le serveur avec notre
// catégorie (pièces détachées et accessoires écartés). L'utilisateur publie lui-même.
export type EbayCategory = { id: string; name: string; path: string };
export type EbayCategoryResult = {
  state: "ok" | "aucun_resultat" | "indisponible" | "non_configure";
  categories: EbayCategory[];
};

export async function fetchEbayCategory(product: string, category: string): Promise<EbayCategoryResult> {
  try {
    const res = await fetch(`${API_URL}/api/ebay/category?product=${encodeURIComponent(product)}&category=${encodeURIComponent(category)}`);
    if (!res.ok) return { state: "indisponible", categories: [] };
    return (await res.json()) as EbayCategoryResult;
  } catch {
    return { state: "indisponible", categories: [] };
  }
}

// Studio photo : l'objet détouré, posé sur un fond clair. L'objet n'est pas modifié.
export async function makeStudio(photo: Blob): Promise<Blob> {
  const body = new FormData();
  body.append("file", photo, "photo.jpg");
  const key = demoKey();
  const res = await fetch(`${API_URL}/api/studio`, { method: "POST", body, headers: key ? { "X-Demo-Key": key } : undefined });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(typeof data.detail === "string" ? data.detail : "La photo studio a échoué. Réessayez dans un instant.");
  }
  return res.blob();
}
