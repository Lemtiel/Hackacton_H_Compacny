// Brouillon d'annonce généré par gabarit, en attendant l'appel au modèle de texte Hugging Face.
export type Platform = "vinted" | "leboncoin" | "ebay" | "libre";

export const PLATFORM_LABELS: Record<Platform, string> = {
  vinted: "Vinted",
  leboncoin: "Leboncoin",
  ebay: "eBay",
  libre: "Texte libre",
};

export type Condition = "comme_neuf" | "bon_etat" | "use";

export const CONDITION_LABELS: Record<Condition, string> = {
  comme_neuf: "Comme neuf",
  bon_etat: "Bon état",
  use: "Usé",
};

export function draftListing(
  platform: Platform,
  product: string,
  condition: Condition,
  withBox: boolean,
  price?: number,
): string {
  const etat = CONDITION_LABELS[condition].toLowerCase();
  const boite = withBox ? "Vendu avec sa boîte d'origine." : "Vendu sans boîte d'origine.";
  const prix = price ? `${Math.round(price)} €` : "à fixer";
  switch (platform) {
    case "vinted":
      return `${product}, ${etat}\n\n${product} en ${etat}, testé et fonctionnel. ${boite}\nEnvoi soigné sous 48 h.\n\nPrix : ${prix}`;
    case "leboncoin":
      return `${product} – ${CONDITION_LABELS[condition]}\n\nJe vends mon ${product}, en ${etat}. Il fonctionne parfaitement. ${boite}\nRemise en main propre ou envoi possible.\n\nPrix : ${prix}`;
    case "ebay":
      return `${product} ${CONDITION_LABELS[condition]}${withBox ? " avec boîte" : ""}\n\nÉtat : ${CONDITION_LABELS[condition]}\nFonctionnement : testé, entièrement fonctionnel\nContenu : ${withBox ? "boîte d'origine incluse" : "sans boîte d'origine"}\n\nPrix : ${prix}`;
    default:
      return `${product}, ${etat}. ${boite} Prix : ${prix}.`;
  }
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
