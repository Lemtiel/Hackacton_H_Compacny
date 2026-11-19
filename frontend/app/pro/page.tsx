"use client";

// Espace revendeurs : version de départ, à faire évoluer par Tristan (voir docs/produit/revendeurs.md).
// Même recherche que l'app : aucun agent ni appel serveur en plus, le classement se calcule ici.

import Link from "next/link";
import { useEffect, useRef, useState, type CSSProperties } from "react";
import { CATEGORY_LABELS, type Category, type Offer, type SearchEvent, euros, isDemo, searchPrices, shotUrl } from "@/lib/api";
import { CONDITIONS, type Condition } from "@/lib/listing";
import { guessCategory } from "@/lib/variants";
import { type Row, SearchProgress } from "@/components/SearchScreen";

const DEFAULT_RESALE_FEES = 10;
const DEAL_GAP = 0.15; // « Bonne affaire » à partir de 15 % sous la médiane
const CATEGORIES = Object.keys(CATEGORY_LABELS) as Category[];

type Deal = Offer & { site: string; margin: number; gap: number; outlier: boolean };
type CartItem = {
  id: string;
  product: string;
  title: string;
  site: string;
  price: number;
  margin: number;
  url: string;
};

const CART_KEY = "snapncash.pro.cart.v1";

// Même règle que backend/pricing.py : on garde les prix entre la moitié et le double de la médiane.
function median(xs: number[]) {
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

export default function ProPage() {
  const [product, setProduct] = useState("");
  const [category, setCategory] = useState<Category>("console");
  const [condition, setCondition] = useState<Condition>("Bon état");
  const [query, setQuery] = useState<{ product: string; category: Category; condition: Condition } | null>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [done, setDone] = useState(false);
  const [failed, setFailed] = useState(false);
  const [refused, setRefused] = useState<string | null>(null);
  const [demo, setDemo] = useState(false);
  const [resaleFees, setResaleFees] = useState(DEFAULT_RESALE_FEES);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [cartLoaded, setCartLoaded] = useState(false);
  const stopRef = useRef<(() => void) | null>(null);

  useEffect(() => setDemo(isDemo()), []);
  useEffect(() => () => stopRef.current?.(), []);
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(CART_KEY) || "[]");
      if (Array.isArray(saved)) setCart(saved.filter((item): item is CartItem => typeof item?.url === "string" && item.url.length > 0));
    } catch { /* panier illisible : on repart vide */ }
    setCartLoaded(true);
  }, []);
  useEffect(() => {
    if (!cartLoaded) return;
    try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch { /* stockage privé ou plein */ }
  }, [cart, cartLoaded]);

  function launch() {
    const p = product.trim();
    if (p.length < 2) return;
    stopRef.current?.();
    setQuery({ product: p, category, condition });
    setRows([]);
    setDone(false);
    setFailed(false);
    setRefused(null);
    stopRef.current = searchPrices(
      p,
      category,
      (ev: SearchEvent) => {
        if (ev.type === "start") {
          setRows(ev.sites.map((s) => ({
            key: s.key, name: s.name, state: s.active ? "attente" : "hors_categorie",
            label: s.active ? "En attente" : "Hors catégorie", steps: [], elapsed: 0, offers: [],
          })));
        } else if (ev.type === "site_step") {
          const label = ev.label ? ev.label.charAt(0).toUpperCase() + ev.label.slice(1) : "Navigation en cours";
          setRows((r) => r.map((s) => {
            if (s.key !== ev.site) return s;
            const steps = s.steps[s.steps.length - 1] === label ? s.steps : [...s.steps, label].slice(-4);
            return { ...s, state: "en_cours", label, steps, elapsed: ev.elapsed_s ?? s.elapsed };
          }));
        } else if (ev.type === "site_shot") {
          setRows((r) => r.map((s) => (s.key === ev.site ? { ...s, shot: shotUrl(ev.shot) } : s)));
        } else if (ev.type === "site_result") {
          const label = ev.state === "ok"
            ? `${ev.offers.length} prix relevé${ev.offers.length > 1 ? "s" : ""}`
            : ev.state === "aucun_resultat" ? "Aucune offre comparable" : "Site indisponible";
          setRows((r) => r.map((s) => (s.key === ev.site
            ? { ...s, state: ev.state, label, elapsed: ev.duration_s ?? s.elapsed, offers: ev.offers }
            : s)));
        } else if (ev.type === "error") {
          setRefused(ev.message);
          setFailed(true);
        } else if (ev.type === "done") {
          setDone(true);
        }
      },
      () => { setFailed(true); setDone(true); },
      demo,
      "",
      { condition },
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

  function cartId(deal: Deal) {
    return `${deal.site}|${deal.url ?? deal.title}|${deal.price_eur}`;
  }

  function toggleCart(deal: Deal) {
    if (!deal.url) return;
    const url = deal.url;
    const id = cartId(deal);
    setCart((current) => current.some((item) => item.id === id)
      ? current.filter((item) => item.id !== id)
      : [...current, {
          id,
          product: query?.product ?? product.trim(),
          title: deal.title,
          site: deal.site,
          price: deal.price_eur,
          margin: deal.margin,
          url,
        }]);
  }

  return (
    <main className="page">
      <section className="screen">
        <header className="pro-header">
          <p className="muted">Espace revendeurs</p>
          <h1 className="display search-title">Trouvez les objets à racheter.</h1>
          <p className="lede">Nos agents relèvent les prix dans les boutiques d&apos;occasion. On classe les annonces selon la marge possible à la revente.</p>
        </header>

        <aside id="pro-cart" className="pro-cart" aria-label="Panier du revendeur">
          <details open={cart.length > 0}>
            <summary>
              <span className="pro-cart-title"><CartIcon /> Objets retenus</span>
              <span className="pro-cart-count num">{cart.length}</span>
            </summary>
            {cart.length === 0 ? (
              <p className="small">Retenez une bonne affaire pour la retrouver ici.</p>
            ) : (
              <div className="pro-cart-items">
                {cart.map((item) => (
                  <article key={item.id} className="pro-cart-item">
                    <a className="pro-cart-link" href={item.url} target="_blank" rel="noopener noreferrer" aria-label={`Ouvrir l'annonce ${item.title} sur ${item.site}`}>
                      <strong>{item.title}</strong>
                      <span className="small">{item.product} · {item.site} · achat {euros(item.price)} · marge {item.margin >= 0 ? "+" : ""}{euros(item.margin)}</span>
                      <span className="pro-cart-open">Voir l’article ↗</span>
                    </a>
                    <button type="button" className="pro-cart-remove" onClick={() => setCart((current) => current.filter((entry) => entry.id !== item.id))} aria-label={`Retirer ${item.title} du panier`}>×</button>
                  </article>
                ))}
              </div>
            )}
          </details>
        </aside>

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
          <div>
            <span className="label">État recherché</span>
            <div className="chips" role="group" aria-label="État recherché">
              {CONDITIONS.map((c) => (
                <button key={c} type="button" className="chip" aria-pressed={condition === c} onClick={() => setCondition(c)}>{c}</button>
              ))}
            </div>
          </div>
          <button className="btn btn-primary" type="submit" disabled={product.trim().length < 2 || (!!query && !done)}>
            Chercher les bonnes affaires
          </button>
        </form>

        {failed && <p className="notice error" style={{ marginTop: "1rem" }}>{refused ?? "Le serveur ne répond pas. Relancez la recherche."}</p>}
        {query && (
          <>
            <SearchProgress rows={rows} done={done} demo={demo} />
            <ProAgentLive rows={rows} done={done} />
          </>
        )}

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
                <article key={`${d.site}-${d.url ?? d.title}-${i}`} className="offer pro-offer" data-margin={d.margin >= 0 ? "profit" : "loss"}>
                  <span className="pro-offer-copy">
                    {d.gap >= DEAL_GAP && !d.outlier && <span className="status-pill" data-status="vendu" style={{ marginRight: "0.4rem" }}>Bonne affaire</span>}
                    {d.outlier && <span className="status-pill" style={{ marginRight: "0.4rem" }}>À vérifier</span>}
                    {d.url ? <a href={d.url} target="_blank" rel="noopener noreferrer">{d.title}</a> : d.title}
                    <span className="small">, {d.site}</span>
                  </span>
                  <span className="pro-offer-actions">
                    <span className="num pro-offer-price">
                      {euros(d.price_eur)}
                      <small>{d.margin >= 0 ? `+${euros(d.margin)} de marge` : `${euros(d.margin)} de perte`}</small>
                    </span>
                    <button type="button" className="pro-cart-toggle" disabled={!d.url} title={d.url ? undefined : "Lien de l’annonce indisponible"} aria-pressed={cart.some((item) => item.id === cartId(d))} onClick={() => toggleCart(d)}>
                      {!d.url ? "Lien indisponible" : cart.some((item) => item.id === cartId(d)) ? "Retenu ✓" : "Retenir"}
                    </button>
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

function CartIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden><path d="M3 4h2l2.1 10.2a2 2 0 0 0 2 1.6h7.8a2 2 0 0 0 2-1.6L20 8H6.1M9 20h.01M17 20h.01" /></svg>;
}

function ProAgentLive({ rows, done }: { rows: Row[]; done: boolean }) {
  const active = rows.filter((row) => row.state !== "hors_categorie");
  if (active.length === 0) return null;
  return (
    <section className="pro-agent-live" aria-labelledby="pro-agents-title" aria-live="polite">
      <div className="pro-agent-live-head">
        <span>
          <strong id="pro-agents-title">Agents en direct</strong>
          <span className="small">Chaque carte évolue pendant la visite du site.</span>
        </span>
        <span className="pro-live-dot" data-done={done} aria-hidden />
      </div>
      <div className="pro-agent-grid">
        {active.map((row) => (
          <article key={row.key} className="pro-agent-card" data-state={row.state}>
            <div className="pro-agent-card-head">
              <strong>{row.name}</strong>
              <span className="small num">{Math.round(row.elapsed)} s</span>
            </div>
            <div className="pro-agent-status"><span className="dot" data-state={row.state} />{row.label}</div>
            {row.steps.length > 0 && (
              <ol className="pro-agent-steps">
                {row.steps.map((step, index) => <li key={`${step}-${index}`}>{step}</li>)}
              </ol>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
