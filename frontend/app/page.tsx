"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  CATEGORY_LABELS,
  type Category,
  type SearchEvent,
  type ShopBlock,
  type SiteRow,
  euros,
  identifyPhoto,
  marketplaceLinks,
  searchPrices,
} from "@/lib/api";
import {
  CONDITION_LABELS,
  type Condition,
  type HistoryItem,
  PLATFORM_LABELS,
  type Platform,
  draftListing,
  pushHistory,
  readHistory,
} from "@/lib/listing";

type Step = "home" | "identifying" | "confirm" | "search";

const CATEGORIES = Object.keys(CATEGORY_LABELS) as Category[];

export default function Home() {
  const [step, setStep] = useState<Step>("home");
  const [error, setError] = useState<string | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [product, setProduct] = useState("");
  const [category, setCategory] = useState<Category>("console");
  const [lowConfidence, setLowConfidence] = useState(false);
  const [condition, setCondition] = useState<Condition>("bon_etat");
  const [withBox, setWithBox] = useState(true);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => setHistory(readHistory()), []);
  useEffect(() => () => { if (photoUrl) URL.revokeObjectURL(photoUrl); }, [photoUrl]);

  async function onPhoto(file?: File) {
    if (!file) return;
    setError(null);
    setPhotoUrl(URL.createObjectURL(file));
    setStep("identifying");
    try {
      const ident = await identifyPhoto(file);
      setProduct([ident.product, ident.variant].filter(Boolean).join(" "));
      if (CATEGORIES.includes(ident.category as Category)) setCategory(ident.category as Category);
      setLowConfidence(ident.confidence < 0.7 || !ident.model);
      setStep("confirm");
    } catch (e) {
      setError((e as Error).message);
      setStep("confirm");
      setLowConfidence(true);
    }
  }

  function startOver() {
    setStep("home");
    setError(null);
    setPhotoUrl(null);
    setProduct("");
    setHistory(readHistory());
  }

  return (
    <main className="page">
      {step === "home" && (
        <HomeScreen
          onPhoto={onPhoto}
          onText={(p, c) => { setProduct(p); setCategory(c); setPhotoUrl(null); setStep("confirm"); }}
          history={history}
        />
      )}

      {step === "identifying" && (
        <section className="screen" aria-live="polite">
          {photoUrl && <img src={photoUrl} alt="Votre photo" className="photo" />}
          <h2 style={{ marginTop: "1.5rem" }}>On reconnaît votre objet…</h2>
          <p className="muted">Quelques secondes. La photo n&apos;est pas conservée.</p>
        </section>
      )}

      {step === "confirm" && (
        <section className="screen">
          {photoUrl && <img src={photoUrl} alt="Votre photo" className="photo" />}
          {error && <p className="notice error" style={{ marginTop: "1rem" }}>{error}</p>}
          <label className="label" htmlFor="product">Votre objet</label>
          <input
            id="product"
            className="field"
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            placeholder="Ex. Nintendo Switch OLED"
            autoComplete="off"
          />
          {lowConfidence && !error && (
            <p className="small" style={{ marginTop: "0.5rem" }}>
              Vérifiez le modèle exact (capacité, édition) : le prix en dépend.
            </p>
          )}

          <span className="label">Catégorie</span>
          <div className="chips">
            {CATEGORIES.map((c) => (
              <button key={c} type="button" className="chip" aria-pressed={category === c} onClick={() => setCategory(c)}>
                {CATEGORY_LABELS[c]}
              </button>
            ))}
          </div>

          <span className="label">État</span>
          <div className="seg" role="group" aria-label="État">
            {(Object.keys(CONDITION_LABELS) as Condition[]).map((c) => (
              <button key={c} type="button" aria-pressed={condition === c} onClick={() => setCondition(c)}>
                {CONDITION_LABELS[c]}
              </button>
            ))}
          </div>

          <span className="label">Boîte d&apos;origine</span>
          <div className="seg" role="group" aria-label="Boîte d'origine">
            <button type="button" aria-pressed={withBox} onClick={() => setWithBox(true)}>Avec</button>
            <button type="button" aria-pressed={!withBox} onClick={() => setWithBox(false)}>Sans</button>
          </div>

          <div className="stack" style={{ marginTop: "2rem" }}>
            <button
              className="btn btn-primary"
              disabled={product.trim().length < 2}
              onClick={() => { setError(null); setStep("search"); }}
            >
              Estimer le prix
            </button>
            <button className="link-btn" onClick={startOver}>Recommencer</button>
          </div>
        </section>
      )}

      {step === "search" && (
        <SearchScreen
          product={product.trim()}
          category={category}
          condition={condition}
          withBox={withBox}
          onDone={(item) => pushHistory(item)}
          onRestart={startOver}
        />
      )}
    </main>
  );
}

function HomeScreen({
  onPhoto,
  onText,
  history,
}: {
  onPhoto: (f?: File) => void;
  onText: (product: string, category: Category) => void;
  history: HistoryItem[];
}) {
  const cameraRef = useRef<HTMLInputElement>(null);
  const galleryRef = useRef<HTMLInputElement>(null);
  const [text, setText] = useState("");

  return (
    <section className="screen">
      <h1 className="display">Ce qui dort chez vous a un prix.</h1>
      <p className="lede">Photographiez votre objet. On compare les prix d&apos;occasion à votre place et on prépare l&apos;annonce.</p>

      <div className="stack">
        <button className="btn btn-primary" onClick={() => cameraRef.current?.click()}>
          <CameraIcon /> Prendre une photo
        </button>
        <button className="btn btn-quiet" onClick={() => galleryRef.current?.click()}>
          Choisir une photo
        </button>
      </div>
      <input ref={cameraRef} type="file" accept="image/*" capture="environment" className="sr-only" onChange={(e) => onPhoto(e.target.files?.[0])} />
      <input ref={galleryRef} type="file" accept="image/*" className="sr-only" onChange={(e) => onPhoto(e.target.files?.[0])} />
      <p className="small" style={{ marginTop: "0.75rem" }}>
        Photographiez l&apos;objet seul : une photo avec un visage est refusée.
      </p>

      <div className="or">ou</div>
      <form
        className="stack"
        onSubmit={(e) => { e.preventDefault(); if (text.trim().length >= 2) onText(text.trim(), "console"); }}
      >
        <label htmlFor="text" className="sr-only">Nom de l&apos;objet</label>
        <input id="text" className="field" value={text} onChange={(e) => setText(e.target.value)} placeholder="Tapez le nom de l'objet" autoComplete="off" />
        <button className="btn btn-quiet" type="submit" disabled={text.trim().length < 2}>Continuer</button>
      </form>

      {history.length > 0 && (
        <div style={{ marginTop: "2.5rem" }}>
          <h2>Vos dernières estimations</h2>
          <p className="small">Gardées seulement sur cet appareil.</p>
          <ul className="sites">
            {history.slice(0, 5).map((h) => (
              <li key={h.product + h.date} className="site" style={{ gridTemplateColumns: "1fr auto" }}>
                <span>
                  <span className="site-name">{h.product}</span>
                  <br />
                  <span className="site-step">{new Date(h.date).toLocaleDateString("fr-FR")}</span>
                </span>
                <span className="num muted">{h.low && h.high ? `${euros(h.low)} – ${euros(h.high)}` : ""}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function SearchScreen({
  product,
  category,
  condition,
  withBox,
  onDone,
  onRestart,
}: {
  product: string;
  category: Category;
  condition: Condition;
  withBox: boolean;
  onDone: (item: HistoryItem) => void;
  onRestart: () => void;
}) {
  const [rows, setRows] = useState<SiteRow[]>([]);
  const [shop, setShop] = useState<ShopBlock | null>(null);
  const [done, setDone] = useState(false);
  const [failed, setFailed] = useState(false);
  const [platform, setPlatform] = useState<Platform>("vinted");
  const [copied, setCopied] = useState(false);
  const shopRef = useRef<ShopBlock | null>(null);

  useEffect(() => {
    const stop = searchPrices(
      product,
      category,
      (ev: SearchEvent) => {
        if (ev.type === "start") {
          setRows(ev.sites.map((s) => ({
            key: s.key,
            name: s.name,
            state: s.active ? "attente" : "hors_categorie",
            label: s.active ? "En attente" : "Ne vend pas ce type d'objet",
            offers: [],
          })));
        } else if (ev.type === "site_step") {
          setRows((r) => r.map((s) => s.key === ev.site ? { ...s, state: "en_cours", label: ev.label ? ev.label.charAt(0).toUpperCase() + ev.label.slice(1) : s.label, elapsed_s: ev.elapsed_s ?? s.elapsed_s } : s));
        } else if (ev.type === "site_result") {
          const label = ev.state === "ok" ? `${ev.offers.length} prix relevés` : ev.state === "aucun_resultat" ? "Aucune offre trouvée" : "Site indisponible";
          setRows((r) => r.map((s) => s.key === ev.site ? { ...s, state: ev.state, label, elapsed_s: ev.duration_s, offers: ev.offers } : s));
        } else if (ev.type === "shop_block") {
          setShop(ev.block);
          shopRef.current = ev.block;
        } else if (ev.type === "done") {
          setDone(true);
          const b = shopRef.current;
          onDone({ product, date: new Date().toISOString(), low: b?.buyback_low, high: b?.buyback_high });
        }
      },
      () => { setFailed(true); setDone(true); },
    );
    return stop;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [product, category]);

  const draft = useMemo(
    () => draftListing(platform, product, condition, withBox, shop?.shop_median),
    [platform, product, condition, withBox, shop],
  );
  const [listing, setListing] = useState(draft);
  useEffect(() => setListing(draft), [draft]);

  async function copy() {
    try {
      await navigator.clipboard.writeText(listing);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* presse-papiers refusé : le texte reste sélectionnable */
    }
  }

  const running = !done;
  const okSites = rows.filter((r) => r.state === "ok");

  return (
    <section className="screen">
      <p className="muted" style={{ margin: "0.5rem 0 0" }}>{CATEGORY_LABELS[category]}, {CONDITION_LABELS[condition].toLowerCase()}</p>
      <h1 className="display" style={{ marginTop: "0.25rem" }}>{product}</h1>

      {failed && (
        <p className="notice error">Le serveur ne répond pas. Vérifiez votre connexion, puis relancez l&apos;estimation.</p>
      )}

      {shop ? (
        <PriceVerdict shop={shop} running={running} />
      ) : (
        running && !failed && <p className="lede" aria-live="polite">Nos agents visitent les boutiques d&apos;occasion. Comptez une à deux minutes.</p>
      )}

      {done && !shop && !failed && (
        <p className="notice warn">
          Aucune boutique n&apos;a cet objet en vente aujourd&apos;hui. Vérifiez le modèle exact, ou consultez les prix des particuliers ci-dessous.
        </p>
      )}

      <ul className="sites" aria-live="polite">
        {rows.map((s) => (
          <li key={s.key} className="site" data-state={s.state}>
            <span className="dot" data-state={s.state} aria-hidden />
            <span>
              <span className="site-name">{s.name}</span>
              <br />
              <span className="site-step">{s.label}</span>
            </span>
            <span className="small num">{s.elapsed_s ? `${Math.round(s.elapsed_s)} s` : ""}</span>
          </li>
        ))}
      </ul>

      {okSites.length > 0 && (
        <div className="panel">
          <h3>Les offres relevées</h3>
          <p className="small" style={{ margin: "0 0 0.5rem" }}>Prix de revente affichés par les boutiques. Ouvrez une offre pour la voir sur le site.</p>
          {okSites.map((s) => (
            <details key={s.key} className="site-detail">
              <summary>
                <span>{s.name}</span>
                <span className="num muted">{priceRange(s.offers.map((o) => o.price_eur))}</span>
              </summary>
              {s.offers.map((o, i) => (
                <div key={i} className="offer">
                  <span>{o.url ? <a href={o.url} target="_blank" rel="noopener noreferrer">{o.title}</a> : o.title}{o.condition ? <span className="small">, {o.condition}</span> : null}</span>
                  <span className="num">{euros(o.price_eur)}</span>
                </div>
              ))}
            </details>
          ))}
        </div>
      )}

      <div className="panel">
        <h3>Vendre seul</h3>
        <p className="small" style={{ margin: 0 }}>
          Le prix eBay arrive bientôt dans l&apos;estimation. En attendant, comparez vous-même les prix des particuliers :
        </p>
        <div className="links">
          {marketplaceLinks(product).map((l) => (
            <a key={l.name} className="btn btn-quiet" href={l.url} target="_blank" rel="noopener noreferrer" style={{ background: "#fff" }}>
              Voir sur {l.name}
            </a>
          ))}
        </div>
      </div>

      <div className="panel">
        <h3>Votre annonce</h3>
        <div className="seg" role="group" aria-label="Plateforme" style={{ marginTop: "0.5rem" }}>
          {(Object.keys(PLATFORM_LABELS) as Platform[]).map((p) => (
            <button key={p} type="button" aria-pressed={platform === p} onClick={() => setPlatform(p)}>
              {PLATFORM_LABELS[p]}
            </button>
          ))}
        </div>
        <label htmlFor="listing" className="sr-only">Texte de l&apos;annonce</label>
        <textarea id="listing" className="listing" value={listing} onChange={(e) => setListing(e.target.value)} />
        <button className="btn btn-primary" onClick={copy}>{copied ? "Annonce copiée" : "Copier l'annonce"}</button>
        <p className="small" style={{ marginTop: "0.6rem" }}>Ajustez le texte et le prix, puis collez l&apos;annonce sur le site de votre choix et publiez-la vous-même.</p>
      </div>

      <div className="stack" style={{ marginTop: "2rem" }}>
        <button className="btn btn-quiet" onClick={onRestart}>Estimer un autre objet</button>
      </div>

      <p className="footer-note">
        Prix indicatifs relevés sur Easy Cash, Gamecash, Troc.com et Cash Converters. Comparaison non exhaustive. Objet reconnu par
        intelligence artificielle. <a href="/comment-ca-marche">Comment ça marche</a>
      </p>
    </section>
  );
}

function PriceVerdict({ shop, running }: { shop: ShopBlock; running: boolean }) {
  // Une seule échelle en euros pour comparer d'un coup d'œil.
  const min = Math.floor(Math.min(shop.buyback_low, shop.shop_low) / 10) * 10;
  const max = Math.ceil(shop.shop_high / 10) * 10;
  const pos = (v: number) => `${((v - min) / Math.max(max - min, 1)) * 100}%`;
  const width = (a: number, b: number) => `${Math.max(((b - a) / Math.max(max - min, 1)) * 100, 2)}%`;

  return (
    <div aria-live="polite">
      <div className="verdict">
        <p className="muted" style={{ margin: 0 }}>En magasin, on vous en proposerait environ</p>
        <div className="verdict-price num">{euros(shop.buyback_estimate)}</div>
        <p className="small" style={{ margin: "0.4rem 0 0" }}>
          Estimation basse : {Math.round(shop.coef * 100)} % du prix de revente en boutique, d&apos;après {shop.n_kept} prix
          {running ? ", d'autres boutiques répondent encore" : ""}.
        </p>
      </div>

      <div className="scale" role="img" aria-label={`Rachat estimé entre ${euros(shop.buyback_low)} et ${euros(shop.buyback_high)}, revente en boutique entre ${euros(shop.shop_low)} et ${euros(shop.shop_high)}`}>
        <div className="scale-row">
          <div className="scale-head"><span>Rachat en magasin</span><span className="num">{euros(shop.buyback_low)} – {euros(shop.buyback_high)}</span></div>
          <div className="scale-track">
            <div className="scale-bar magasin" style={{ left: pos(shop.buyback_low), width: width(shop.buyback_low, shop.buyback_high) }} />
            <div className="scale-mark" style={{ left: pos(shop.buyback_estimate) }} />
          </div>
        </div>
        <div className="scale-row">
          <div className="scale-head"><span>Revendu par les boutiques</span><span className="num">{euros(shop.shop_low)} – {euros(shop.shop_high)}</span></div>
          <div className="scale-track">
            <div className="scale-bar boutique" style={{ left: pos(shop.shop_low), width: width(shop.shop_low, shop.shop_high) }} />
          </div>
        </div>
        <div className="scale-axis num"><span>{euros(min)}</span><span>{euros(max)}</span></div>
      </div>
      <p className="small">L&apos;écart entre les deux barres, c&apos;est ce que vous gagnez à vendre vous-même.</p>
    </div>
  );
}

function priceRange(prices: number[]) {
  const low = Math.min(...prices);
  const high = Math.max(...prices);
  return low === high ? euros(low) : `${euros(low)} – ${euros(high)}`;
}

function CameraIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.3l1.2-1.6A1 1 0 0 1 9.8 4h4.4a1 1 0 0 1 .8.4L16.2 6h1.3A2.5 2.5 0 0 1 20 8.5v8a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 16.5v-8Z" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="12" cy="12.5" r="3.5" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}
