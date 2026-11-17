// Précisions intelligentes : variantes courantes proposées en un toucher.
// Le prix dépend du modèle exact (Switch, Switch OLED et Switch Lite n'ont pas le même prix).
type Rule = { match: RegExp; label: string; options: string[] };

const RULES: Rule[] = [
  { match: /switch/i, label: "Quel modèle de Switch ?", options: ["Switch", "Switch OLED", "Switch Lite", "Switch 2"] },
  { match: /playstation|ps[345]\b/i, label: "Quelle version ?", options: ["Standard", "Slim", "Pro", "Digital"] },
  { match: /xbox/i, label: "Quelle version ?", options: ["Series X", "Series S", "One S", "One X"] },
  { match: /iphone|galaxy|redmi|xiaomi|pixel|smartphone/i, label: "Quelle capacité ?", options: ["64 Go", "128 Go", "256 Go", "512 Go"] },
  { match: /ipad|tablette|tab\b/i, label: "Quelle capacité ?", options: ["32 Go", "64 Go", "128 Go", "256 Go"] },
];

const CAPACITY = /\b\d{2,4}\s?go\b/i;

export function variantSuggestion(product: string, category: string): Rule | null {
  const rule = RULES.find((r) => r.match.test(product)) ?? (category === "smartphone" ? RULES[3] : category === "tablette" ? RULES[4] : null);
  if (!rule) return null;
  // Capacité déjà indiquée : rien à proposer.
  if (rule.options[0].endsWith("Go") && CAPACITY.test(product)) return null;
  return rule;
}

// Applique une variante : remplace la précédente plutôt que d'empiler les mots.
export function applyVariant(product: string, rule: Rule, option: string): string {
  if (option.endsWith("Go")) return `${product.replace(CAPACITY, "").trim()} ${option}`;
  if (/switch/i.test(rule.label)) return `Nintendo ${option}`;
  const base = product.replace(new RegExp(`\\b(${rule.options.join("|")})\\b`, "gi"), "").replace(/\s+/g, " ").trim();
  return option === "Standard" ? base : `${base} ${option}`;
}

// Catégorie devinée à partir du nom tapé (la photo, elle, la donne directement).
export function guessCategory(product: string): "smartphone" | "console" | "jeu_video" | "tablette" | "informatique" | null {
  const p = product.toLowerCase();
  if (/\b(jeu|game)\b/.test(p)) return "jeu_video";
  if (/ipad|tablette|galaxy tab|\btab\b/.test(p)) return "tablette";
  if (/iphone|galaxy|redmi|xiaomi|pixel|oneplus|huawei|smartphone|t[ée]l[ée]phone/.test(p)) return "smartphone";
  if (/switch|playstation|ps[2-5]\b|xbox|wii|game ?boy|nintendo/.test(p)) return "console";
  if (/macbook|ordinateur|laptop|pc portable|imac/.test(p)) return "informatique";
  return null;
}
