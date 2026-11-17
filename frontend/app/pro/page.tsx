"use client";

// Espace revendeurs : version de départ, à faire évoluer par Tristan (voir docs/revendeurs.md).
// Même recherche que l'app : aucun agent ni appel serveur en plus, le classement se calcule ici.

import { useEffect, useRef, useState } from "react";
import { CATEGORY_LABELS, type Category, type Offer, type SearchEvent, euros, isDemo, searchPrices, shotUrl } from "@/lib/api";
import { guessCategory } from "@/lib/variants";
import { type Row, SearchProgress } from "@/components/SearchScreen";

const RESALE_FEES = 0.1; // commission et envoi : à rendre réglable (docs/revendeurs.md, point 1)
const DEAL_GAP = 0.15; // « Bonne affaire » à partir de 15 % sous la médiane
const CATEGORIES = Object.keys(CATEGORY_LABELS) as Category[];

type Deal = Offer & { site: string; margin: number; gap: number; outlier: boolean };

// Même règle que backend/pricing.py : on garde les prix entre la moitié et le double de la médiane.
function median(xs: number[]) {
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

export default function ProPage() {
  const [product, setProduct] = useState("");
  const [category, setCategory] = useState<Category>("console");
  const [query, setQuery] = useState<{ product: string; category: Category } | null>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [done, setDone] = useState(false);
  const [failed, setFailed] = useState(false);
  const [demo, setDemo] = useState(false);
  const stopRef = useRef<(() => void) | null>(null);

  useEffect(() => setDemo(isDemo()), []);
  useEffect(() => () => stopRef.current?.(), []);

  function launch() {
    const p = product.trim();
    if (p.length < 2) return;
    stopRef.current?.();
    setQuery({ product: p, category });
    setRows([]);
    setDone(false);
    setFailed(false);
    stopRef.current = searchPrices(
      p,
      category,
      (ev: SearchEvent) => {
        if (ev.type === "start") {
          setRows(ev.sites.map((s) => ({
            key: s.key, name: s.name, state: s.active ? "attente" : "hors_categorie",
            label: "", steps: [], elapsed: 0, offers: [],
          })));
        } else if (ev.type === "site_step") {
          setRows((r) => r.map((s) => (s.key === ev.site ? { ...s, state: "en_cours", elapsed: ev.elapsed_s ?? s.elapsed } : s)));
        } else if (ev.type === "site_shot") {
          setRows((r) => r.map((s) => (s.key === ev.site ? { ...s, shot: shotUrl(ev.shot) } : s)));
        } else if (ev.type === "site_result") {
          setRows((r) => r.map((s) => (s.key === ev.site ? { ...s, state: ev.state, offers: ev.offers } : s)));
        } else if (ev.type === "done") {
          setDone(true);
        }
      },
      () => { setFailed(true); setDone(true); },
      demo,
    );
  }

  const all = rows.flatMap((r) => r.offers.map((o) => ({ ...o, site: r.name })));
  const raw = all.map((o) => o.price_eur).filter((p) => p > 0);
  const m0 = raw.length >= 3 ? median(raw) : null;
  const kept = m0 ? raw.filter((p) => p >= m0 / 2 && p <= m0 * 2) : raw;
  const ref = kept.length >= 3 ? median(kept) : null;
  const deals: Deal[] = ref
    ? all
        .map((o) => ({
          ...o,
          margin: Math.round(ref * (1 - RESALE_FEES) - o.price_eur),
          gap: (ref - o.price_eur) / ref,
          outlier: o.price_eur < ref / 2 || o.price_eur > ref * 2,
        }))
        .sort((a, b) => b.margin - a.margin)
    : [];

  return (
    <main className="page">
      <section className="screen">
        <p className="muted" style={{ margin: "0.5rem 0 0" }}>Espace revendeurs</p>
        <h1 className="display search-title">Trouvez les objets à racheter.</h1>
        <p className="lede">Nos agents relèvent les prix dans les boutiques d&apos;occasion. On classe les annonces selon la marge possible à la revente.</p>

        <form className="stack" onSubmit={(e) => { e.preventDefault(); launch(); }}>
          <label htmlFor="pro-product" className="sr-only">Objet recherché</label>
          <input
            id="pro-product"
            className="field"
            value={product}
            onChange={(e) => { setProduct(e.target.value); const g = guessCategory(e.target.value); if (g) setCategory(g); }}
            placeholder="Ex. Nintendo Switch"
            autoComplete="off"
          />
          <div className="chips">
            {CATEGORIES.map((c) => (
              <button key={c} type="button" className="chip" aria-pressed={category === c} onClick={() => setCategory(c)}>{CATEGORY_LABELS[c]}</button>
            ))}
          </div>
          <button className="btn btn-primary" type="submit" disabled={product.trim().length < 2 || (!!query && !done)}>
            Chercher les bonnes affaires
          </button>
        </form>

        {failed && <p className="notice error" style={{ marginTop: "1rem" }}>Le serveur ne répond pas. Relancez la recherche.</p>}
        {query && <SearchProgress rows={rows} done={done} demo={demo} />}

        {ref && (
          <div className="panel">
            <h3>Prix du marché : {euros(ref)}</h3>
            <p className="small" style={{ margin: "0 0 0.75rem" }}>
              Médiane de {kept.length} prix en boutique, même modèle. Marge estimée après {Math.round(RESALE_FEES * 100)} % de frais de revente.
              Prix indicatifs.
            </p>
            {deals.map((d, i) => (
              <div key={i} className="offer">
                <span>
                  {d.gap >= DEAL_GAP && !d.outlier && <span className="status-pill" data-status="vendu" style={{ marginRight: "0.4rem" }}>Bonne affaire</span>}
                  {d.outlier && <span className="status-pill" style={{ marginRight: "0.4rem" }}>À vérifier</span>}
                  {d.url ? <a href={d.url} target="_blank" rel="noopener noreferrer">{d.title}</a> : d.title}
                  <span className="small">, {d.site}</span>
                </span>
                <span className="num" style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                  {euros(d.price_eur)}
                  <br />
                  <span className="small">{d.margin >= 0 ? `+${euros(d.margin)}` : euros(d.margin)}</span>
                </span>
              </div>
            ))}
          </div>
        )}

        {done && !ref && !failed && (
          <p className="notice warn" style={{ marginTop: "1rem" }}>Trop peu de prix pour juger ce modèle. Essayez un nom plus précis.</p>
        )}
      </section>
    </main>
  );
}
