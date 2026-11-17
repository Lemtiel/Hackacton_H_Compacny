"use client";

// Espace revendeurs : version de départ, à faire évoluer par Tristan (voir docs/revendeurs.md).
// Même recherche que l'app : aucun agent ni appel serveur en plus, le classement se calcule ici.

import Link from "next/link";
import { useEffect, useRef, useState, type CSSProperties } from "react";
import { CATEGORY_LABELS, type Category, type Offer, type SearchEvent, euros, isDemo, searchPrices, shotUrl } from "@/lib/api";
import { guessCategory } from "@/lib/variants";
import { type Row, SearchProgress } from "@/components/SearchScreen";

const DEFAULT_RESALE_FEES = 10;
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
  const [resaleFees, setResaleFees] = useState(DEFAULT_RESALE_FEES);
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
          margin: Math.round(ref * (1 - resaleFees / 100) - o.price_eur),
          gap: (ref - o.price_eur) / ref,
          outlier: o.price_eur < ref / 2 || o.price_eur > ref * 2,
        }))
        .sort((a, b) => b.margin - a.margin)
    : [];

  return (
    <main className="page">
      <section className="screen">
        <header className="pro-header">
          <p className="muted">Espace revendeurs</p>
          <h1 className="display search-title">Trouvez les objets à racheter.</h1>
          <p className="lede">Nos agents relèvent les prix dans les boutiques d&apos;occasion. On classe les annonces selon la marge possible à la revente.</p>
        </header>

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
          <section className="panel pro-results" aria-labelledby="market-title">
            <div className="pro-market-summary">
              <div>
                <p className="small">Référence de revente</p>
                <h2 id="market-title">Prix du marché : {euros(ref)}</h2>
              </div>
              <span className="status-pill">{kept.length} prix comparables</span>
            </div>
            <p className="small">
              Médiane des prix relevés dans les boutiques, après retrait des valeurs aberrantes. Prix indicatifs, sources visibles ci-dessous.
            </p>

            <div className="pro-fees">
              <div className="pro-fees-head">
                <label htmlFor="resale-fees">Frais de revente estimés</label>
                <output htmlFor="resale-fees" className="num">{resaleFees} %</output>
              </div>
              <input
                id="resale-fees"
                className="slider"
                type="range"
                min="0"
                max="25"
                step="1"
                value={resaleFees}
                onChange={(event) => setResaleFees(Number(event.target.value))}
                style={{ "--fill": `${(resaleFees / 25) * 100}%` } as CSSProperties}
              />
              <p className="small">Commission et envoi estimés. Les marges se recalculent immédiatement.</p>
            </div>

            <div className="pro-offers">
              {deals.map((d, i) => (
                <article key={`${d.site}-${d.url ?? d.title}-${i}`} className="offer pro-offer">
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
                </article>
              ))}
            </div>
          </section>
        )}

        {done && all.length === 0 && !failed && (
          <div className="notice warn pro-empty">
            <strong>Aucune boutique ne propose ce modèle.</strong>
            <span>Essayez un autre objet ou revenez à l&apos;estimation classique.</span>
            <Link href="/">Revenir à la recherche classique</Link>
          </div>
        )}

        {done && all.length > 0 && !ref && !failed && (
          <div className="notice warn pro-empty">
            <strong>Trop peu de prix pour juger ce modèle.</strong>
            <span>{raw.length} prix trouvé{raw.length === 1 ? "" : "s"} : il en faut au moins 3 comparables. Essayez un nom plus précis.</span>
          </div>
        )}
      </section>
    </main>
  );
}
