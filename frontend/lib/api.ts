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

// condition_match (boutiques seulement) : « exact » = même état que demandé ; « proche » = un cran au-dessus ou
// en dessous, ajouté s'il manquait des offres ; « inconnu » = la boutique n'affiche pas d'état.
export type Offer = {
  title: string;
  price_eur: number;
  condition?: string | null;
  url?: string | null;
  condition_match?: "exact" | "proche" | "inconnu";
};

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
// Réduit une photo avant l'envoi : un iPhone prend du 4032×3024 (3 Mo), trois photos font 9 Mo, trop pour un Wi-Fi ou un
// partage de connexion (requête coupée en route : « Failed to fetch », relevé le 18/11). 1600 px suffisent pour reconnaître
// l'objet. Si la réduction échoue, on envoie la photo d'origine.
export async function downscale(file: Blob, maxSide = 1600, quality = 0.85): Promise<Blob> {
  try {
    const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
    const scale = Math.min(1, maxSide / Math.max(bmp.width, bmp.height));
    if (scale === 1 && file.size < 1_000_000) {
      bmp.close();
      return file;
    }
    const w = Math.round(bmp.width * scale);
    const h = Math.round(bmp.height * scale);
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return file;
    ctx.drawImage(bmp, 0, 0, w, h);
    bmp.close();
    const out = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/jpeg", quality));
    return out && out.size < file.size ? out : file;
  } catch {
    return file;
  }
}

export async function identifyPhotos(files: File[]): Promise<Identification> {
  const body = new FormData();
  const small = await Promise.all(files.slice(0, 3).map((f) => downscale(f)));
  small.forEach((b, i) => body.append("files", b, `photo-${i + 1}.jpg`));
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

// Mode démo : captures des agents pendant la recherche. Actif par défaut (décision du 19/11) ; l'interrupteur de
// Réglages le coupe ou le rallume ; ?demo=1 dans l'adresse le force.
export function isDemo(): boolean {
  try {
    if (new URLSearchParams(window.location.search).get("demo") === "1") return true;
    return JSON.parse(localStorage.getItem("snapncash.prefs") || "{}").demo !== false; // interrupteur dans Réglages
  } catch {
    return true;
  }
}

export const shotUrl = (token: string) => `${API_URL}/api/shot/${encodeURIComponent(token)}`;

// Clé de démo : ouverte une fois avec ?cle=… dans l'adresse, gardée dans ce navigateur. Elle lève la limite par
// adresse IP côté serveur (DEMO_KEY), pour que la démo ne soit pas bloquée par les autres personnes du même Wi-Fi.
export function demoKey(): string {
  // Une clé copiée depuis une phrase traîne souvent une virgule ou un point à la fin (« …?cle=abc, ») : on les retire,
  // y compris sur la clé déjà gardée dans le navigateur.
  const clean = (k: string | null) => (k ?? "").trim().replace(/[,.;:)\]]+$/, "");
  try {
    const fromUrl = clean(new URLSearchParams(window.location.search).get("cle"));
    if (fromUrl) localStorage.setItem("snapncash.cle", fromUrl);
    const stored = clean(localStorage.getItem("snapncash.cle"));
    if (stored) localStorage.setItem("snapncash.cle", stored);
    return stored;
  } catch {
    return "";
  }
}

export function searchPrices(
  product: string,
  category: string,
  onEvent: (e: SearchEvent) => void,
  onError: (message?: string) => void,
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
  const controller = new AbortController();
  let source: EventSource | null = null;
  let stopped = false;

  // EventSource masque le corps des erreurs HTTP (clé absente, mauvaise configuration, etc.).
  // Cette vérification légère permet d'afficher une cause utile avant de lancer les agents.
  fetch(`${API_URL}/api/config`, { signal: controller.signal })
    .then(async (res) => {
      if (!res.ok) throw new Error(`Le serveur répond avec l'erreur ${res.status}.`);
      const config = await res.json() as { search_ready?: boolean };
      if (config.search_ready === false) {
        onError("Le serveur est démarré, mais la clé HAI_API_KEY manque dans le fichier .env à la racine. Redémarrez le serveur après l'avoir ajoutée.");
        return;
      }
      if (stopped) return;

      source = new EventSource(url);
      source.onmessage = (msg) => {
        const ev = JSON.parse(msg.data) as SearchEvent;
        onEvent(ev);
        if (ev.type === "done") source?.close();
      };
      source.onerror = () => {
        source?.close();
        if (!stopped) onError(`La connexion au flux de recherche a été coupée (${API_URL}). Vérifiez le terminal du serveur, puis relancez.`);
      };
    })
    .catch((error: unknown) => {
      if (stopped || (error instanceof DOMException && error.name === "AbortError")) return;
      onError(`Impossible de joindre le serveur sur ${API_URL}. Vérifiez qu'il écoute bien sur le port 8000 et que NEXT_PUBLIC_API_URL pointe vers cette adresse.`);
    });

  return () => {
    stopped = true;
    controller.abort();
    source?.close();
  };
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
  body.append("file", await downscale(photo), "photo.jpg");
  const key = demoKey();
  const res = await fetch(`${API_URL}/api/studio`, { method: "POST", body, headers: key ? { "X-Demo-Key": key } : undefined });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(typeof data.detail === "string" ? data.detail : "La photo studio a échoué. Réessayez dans un instant.");
  }
  return res.blob();
}


// --- Brouillon eBay préparé par un agent H dans le Chrome de l'ordinateur (démo seulement, voir agents/ebay_draft.py) ---
export type DraftEvent =
  | { type: "start"; photos: number }
  | { type: "step"; label: string; steps?: number }
  | {
      type: "result";
      status: "draft_saved" | "login_required" | "blocked" | "partial" | "cancelled";
      photos_uploaded?: number;
      description_filled?: boolean;
      price_set?: boolean;
      draft_url?: string | null;
      note?: string;
    }
  | { type: "done" };

// La fonction n'existe que sur le serveur de démo (EBAY_DRAFT_LOCAL=1) et avec la clé de démo dans le navigateur.
export async function draftAvailable(): Promise<boolean> {
  if (!demoKey()) return false;
  try {
    const res = await fetch(`${API_URL}/api/health`);
    return res.ok && Boolean((await res.json()).brouillon_ebay);
  } catch {
    return false;
  }
}

export async function startEbayDraft(
  p: { photos: string[]; title: string; description: string; price: number; categoryId?: string | null; condition: string; consent: true },
  onEvent: (e: DraftEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const body = new FormData();
  const blobs = await Promise.all(p.photos.slice(0, 10).map(async (u) => downscale(await fetch(u).then((r) => r.blob()))));
  blobs.forEach((b, i) => body.append("files", b, `photo-${i + 1}.jpg`));
  body.append("title", p.title);
  body.append("description", p.description);
  body.append("price", String(p.price));
  body.append("category_id", p.categoryId ?? "");
  body.append("condition", p.condition);
  body.append("key", demoKey());
  body.append("consent", p.consent ? "1" : ""); // donné par l'écran d'autorisation, à chaque brouillon
  const res = await fetch(`${API_URL}/api/ebay/draft`, { method: "POST", body, signal });
  if (!res.ok || !res.body) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Le brouillon n'a pas pu démarrer.");
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let i: number;
    while ((i = buf.indexOf("\n\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 2);
      if (line.startsWith("data:")) onEvent(JSON.parse(line.slice(5)) as DraftEvent);
    }
  }
}
