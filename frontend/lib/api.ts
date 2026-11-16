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

export async function identifyPhoto(file: File): Promise<Identification> {
  const body = new FormData();
  body.append("file", file);
  const res = await fetch(`${API_URL}/api/identify`, { method: "POST", body });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "L'identification a échoué. Tapez le nom de l'objet.");
  return data as Identification;
}

export type SearchEvent =
  | { type: "start"; product: string; category: string; sites: { key: string; name: string; active: boolean }[] }
  | { type: "site_step"; site: string; label?: string; elapsed_s?: number; steps?: number }
  | { type: "site_result"; site: string; state: "ok" | "aucun_resultat" | "indisponible"; duration_s?: number; offers: Offer[] }
  | { type: "shop_block"; block: ShopBlock | null }
  | { type: "done" };

export function searchPrices(product: string, category: string, onEvent: (e: SearchEvent) => void, onError: () => void) {
  const url = `${API_URL}/api/search?product=${encodeURIComponent(product)}&category=${encodeURIComponent(category)}`;
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
