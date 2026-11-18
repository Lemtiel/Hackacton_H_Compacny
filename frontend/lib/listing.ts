// Annonce : générée par le serveur (POST /api/listing, modèle de texte Hugging Face).
// Le gabarit ci-dessous ne sert que de secours quand la rédaction par IA est indisponible.

// Mêmes états que backend/listing.py (CONDITIONS).
export const CONDITIONS = ["Comme neuf", "Très bon état", "Bon état", "État correct", "Pour pièces"] as const;
export type Condition = (typeof CONDITIONS)[number];

export type Platform = "vinted" | "leboncoin" | "ebay" | "generique";

export type ListingFormat = { key: Platform; name: string; title_max: number; title: string; description: string };

const FORMATS: { key: Platform; name: string; title_max: number }[] = [
  { key: "vinted", name: "Vinted", title_max: 60 },
  { key: "leboncoin", name: "Leboncoin", title_max: 50 },
  { key: "ebay", name: "eBay", title_max: 80 },
  { key: "generique", name: "Texte générique", title_max: 80 },
];

// État à choisir dans le formulaire eBay. Un particulier y choisit « Occasion » (les états « reconditionné »
// sont réservés aux vendeurs professionnels) ; l'état précis est déjà écrit dans la description.
export function ebayCondition(condition: Condition): string {
  return condition === "Pour pièces" ? "« Pour pièces détachées ou ne fonctionne pas »" : "« Occasion »";
}

// Secours sans IA, sans prix : le prix se saisit à part sur chaque site.
export function fallbackListing(product: string, condition: Condition, box: boolean, accessories: string, details: string): ListingFormat[] {
  const boite = box ? "Vendu avec sa boîte d'origine." : "Vendu sans boîte d'origine.";
  const acc = accessories.trim() ? ` Fourni avec : ${accessories.trim()}.` : "";
  const det = details.trim() ? ` ${details.trim().replace(/\.?$/, ".")}` : "";
  const body = `${product}, ${condition.toLowerCase()}. ${boite}${acc}${det}`;
  return FORMATS.map((f) => ({
    ...f,
    title: `${product} ${condition.toLowerCase()}`.slice(0, f.title_max),
    description: body,
  }));
}

// Historique : gardé uniquement dans ce navigateur (rien sur notre serveur).
export type HistoryItem = { product: string; date: string; low?: number; high?: number };
const KEY = "snapncash.history";

export function readHistory(): HistoryItem[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]");
  } catch {
    return [];
  }
}

export function pushHistory(item: HistoryItem) {
  try {
    const list = [item, ...readHistory().filter((h) => h.product !== item.product)].slice(0, 20);
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    /* stockage indisponible : on ignore */
  }
}
