// Lien d'ouverture de l'éditeur d'annonce d'eBay.fr avec le titre, la catégorie et l'état déjà remplis.
// Les paramètres ne sont pas documentés par eBay : ils viennent de l'adresse que eBay construit lui-même
// quand on lance une annonce (relevé le 18/11 : /sl/list?mode=AddItem&title=…&categoryId=…&condition=…).
// À revérifier si eBay change son formulaire. Sans catégorie connue, on ouvre l'étape « Trouver un objet » avec le titre.

const BASE = "https://www.ebay.fr/sl";

// Identifiants d'état d'eBay : 1000 neuf, 1500 ouvert, 2500 reconditionné par le vendeur, 3000 occasion, 7000 pour pièces.
export function ebayConditionId(condition: string): number {
  return condition === "Pour pièces" ? 7000 : 3000;
}

export function ebayListingUrl(opts: { title: string; categoryId?: string | null; condition: string }): string {
  const title = opts.title.trim().slice(0, 80); // eBay limite le titre à 80 caractères
  if (!title) return `${BASE}/prelist/suggest`;
  const q = new URLSearchParams({ title });
  if (!opts.categoryId) return `${BASE}/prelist/identify?${q.toString()}`;
  q.set("mode", "AddItem");
  q.set("condition", String(ebayConditionId(opts.condition)));
  q.set("categoryId", opts.categoryId);
  return `${BASE}/list?${q.toString()}`;
}
