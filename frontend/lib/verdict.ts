import type { ShopBlock } from "./api";

// En attendant le bloc eBay, le prix « vendre seul » est estimé à partir des boutiques.
// HYPOTHÈSE à remplacer par la médiane eBay (Specs.md) : un particulier vend environ 15 % sous le prix boutique,
// faute de garantie. Valeur à recalibrer avec le jeu de 30 objets.
export const SELL_ALONE_DISCOUNT = 0.15;

export type Verdict = {
  sellAloneLow: number;
  sellAloneHigh: number;
  sellAloneMid: number;
  buyback: number;
  gain: number;
  recommend: "seul" | "magasin";
  source: "boutiques" | "ebay";
};

export function computeVerdict(shop: ShopBlock, ebay?: { low: number; high: number; median: number } | null): Verdict {
  const k = 1 - SELL_ALONE_DISCOUNT;
  const low = ebay ? ebay.low : Math.round(shop.shop_low * k);
  const high = ebay ? ebay.high : Math.round(shop.shop_median * k);
  const mid = ebay ? ebay.median : Math.round((low + high) / 2);
  const gain = Math.round(mid - shop.buyback_estimate);
  // Vendre seul demande de publier, répondre et expédier : on ne le conseille que si ça rapporte nettement plus.
  const recommend = gain >= 30 && gain >= shop.buyback_estimate * 0.25 ? "seul" : "magasin";
  return { sellAloneLow: low, sellAloneHigh: high, sellAloneMid: mid, buyback: shop.buyback_estimate, gain, recommend, source: ebay ? "ebay" : "boutiques" };
}

export type PriceZone = { key: "rapide" | "juste" | "ambitieux"; label: string; hint: string };

export function priceZone(price: number, v: Verdict, shop: ShopBlock): PriceZone {
  if (price < v.sellAloneLow) return { key: "rapide", label: "Vente rapide", hint: "En dessous du marché : l'objet devrait partir vite." };
  if (price <= Math.max(v.sellAloneHigh, shop.shop_median * 0.95)) return { key: "juste", label: "Prix juste", hint: "Dans les prix du marché entre particuliers." };
  return { key: "ambitieux", label: "Ambitieux", hint: "Au niveau des boutiques, qui offrent une garantie : la vente peut prendre du temps." };
}

// Pages de dépôt d'annonce, ouvertes chez l'utilisateur : c'est lui qui publie.
export const PUBLISH_URLS: Record<string, { name: string; url: string }> = {
  vinted: { name: "Vinted", url: "https://www.vinted.fr/items/new" },
  leboncoin: { name: "Leboncoin", url: "https://www.leboncoin.fr/deposer-une-annonce" },
  ebay: { name: "eBay", url: "https://www.ebay.fr/sl/prelist/suggest" },
};
