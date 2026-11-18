"use client";

import { useEffect, useRef, useState } from "react";
import {
  CATEGORY_LABELS,
  type Category,
  type EbayCategoryResult,
  type EbayResult,
  type Offer,
  type SearchEvent,
  type ShopBlock,
  euros,
  fetchEbay,
  fetchEbayCategory,
  generateListing,
  isDemo,
  makeStudio,
  marketplaceLinks,
  searchPrices,
  shotUrl,
} from "@/lib/api";
import { type GrenierItem, newId, updateItem, upsertItem } from "@/lib/grenier";
import { type Condition, type ListingFormat, type Platform, ebayCondition, fallbackListing } from "@/lib/listing";
import { PUBLISH_URLS, type Verdict, computeVerdict, priceZone } from "@/lib/verdict";
import { CoinRain, CountUp } from "@/components/CashFx";

type State = "attente" | "en_cours" | "ok" | "aucun_resultat" | "indisponible" | "hors_categorie";
export type Row = {
  key: string;
  name: string;
  state: State;
  label: string;
  steps: string[];
  elapsed: number;
  offers: Offer[];
  shot?: string;
};

const MAX_S = 90;

export type SearchInput = {
  product: string;
  category: Category;
  condition: Condition;
  withBox: boolean;
  accessories: string;
  details: string;
  photos: string[];
  hint?: string; // description générique tirée de la photo (« manette PS5 »)
};

export default function SearchScreen({ input, onRestart }: { input: SearchInput; onRestart: () => void }) {
  const { product, category, condition, withBox, accessories, details, photos } = input;
  const [rows, setRows] = useState<Row[]>([]);
  const [shop, setShop] = useState<ShopBlock | null>(null);
  const [done, setDone] = useState(false);
  const [failed, setFailed] = useState(false);
  const [refused, setRefused] = useState<string | null>(null); // recherche refusée par le serveur (limite d'usage)
  const [myPrice, setMyPrice] = useState<number | null>(null);
  const [sharePhotos, setSharePhotos] = useState<string[]>(photos); // photos à partager : studio ou originale, comme affichées
  const idRef = useRef(newId());
  const shopRef = useRef<ShopBlock | null>(null);
  const [ebay, setEbay] = useState<EbayResult | null>(null);
  const ebayRef = useRef<EbayResult | null>(null);
  const priceTouched = useRef(false);
  // Mode démo (?demo=1) : lu après le montage, pour que le rendu serveur et le rendu navigateur concordent.
  const [demo, setDemo] = useState(false);
  useEffect(() => setDemo(isDemo()), []);

  // eBay répond en 1 à 2 s, en parallèle des agents : bloc séparé, jamais mélangé aux boutiques.
  useEffect(() => {
    const ctrl = new AbortController();
    fetchEbay(product, category, ctrl.signal).then((r) => {
      if (ctrl.signal.aborted) return;
      ebayRef.current = r;
      setEbay(r);
    });
    return () => ctrl.abort();
  }, [product, category]);

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
            steps: [],
            elapsed: 0,
            offers: [],
          })));
        } else if (ev.type === "site_step") {
          const label = ev.label ? ev.label.charAt(0).toUpperCase() + ev.label.slice(1) : null;
          setRows((r) => r.map((s) => {
            if (s.key !== ev.site) return s;
            const steps = label && s.steps[s.steps.length - 1] !== label ? [...s.steps, label].slice(-4) : s.steps;
            return { ...s, state: "en_cours", label: label ?? s.label, steps, elapsed: ev.elapsed_s ?? s.elapsed };
          }));
        } else if (ev.type === "site_result") {
          const base = ev.state === "ok" ? `${ev.offers.length} prix relevé${ev.offers.length > 1 ? "s" : ""}` : ev.state === "aucun_resultat" ? "Aucune offre de ce modèle" : "Site indisponible";
          const rejected = ev.n_rejected ? `, ${ev.n_rejected} écartée${ev.n_rejected > 1 ? "s" : ""} (non comparable ou invérifiable)` : "";
          setRows((r) => r.map((s) => (s.key === ev.site ? { ...s, state: ev.state, label: base + rejected, elapsed: ev.duration_s ?? s.elapsed, offers: ev.offers } : s)));
        } else if (ev.type === "site_shot") {
          setRows((r) => r.map((s) => (s.key === ev.site ? { ...s, shot: shotUrl(ev.shot) } : s)));
        } else if (ev.type === "shop_block") {
          setShop(ev.block);
          shopRef.current = ev.block;
        } else if (ev.type === "error") {
          setRefused(ev.message);
          setFailed(true);
        } else if (ev.type === "done") {
          setDone(true);
        }
      },
      () => { setFailed(true); setDone(true); },
      isDemo(),
      input.hint ?? "",
      { condition, box: withBox, accessories, details },
    );
    return stop;
  }, [product, category, condition, withBox, accessories, details, input.hint]);

  const verdict = shop ? computeVerdict(shop, ebaySellRange(ebay)) : null;

  // Prix proposé par défaut : le prix « vendre seul ». Il suit le calcul (eBay peut arriver après les boutiques)
  // tant que l'utilisateur n'a pas bougé le curseur.
  const defaultPrice = verdict?.sellAloneMid ?? null;
  useEffect(() => {
    if (defaultPrice !== null && !priceTouched.current) setMyPrice(defaultPrice);
  }, [defaultPrice]);

  // L'objet entre dans Mon grenier dès que la recherche est finie, puis suit le prix choisi.
  useEffect(() => {
    if (!done || failed) return;
    const b = shopRef.current;
    const e = ebaySellRange(ebayRef.current);
    const v = b ? computeVerdict(b, e) : null;
    const item: GrenierItem = {
      id: idRef.current,
      product,
      category,
      condition,
      date: new Date().toISOString(),
      buyback: b?.buyback_estimate ?? null,
      sellAloneLow: v?.sellAloneLow ?? e?.low ?? null,
      sellAloneHigh: v?.sellAloneHigh ?? e?.high ?? null,
      myPrice: myPrice ?? e?.median ?? null,
      status: "a_vendre",
    };
    upsertItem(item);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [done]);

  useEffect(() => {
    if (done && myPrice !== null) updateItem(idRef.current, { myPrice });
  }, [done, myPrice]);

  // eBay arrivé après la fin des agents (rare) : on met à jour la fourchette dans Mon grenier.
  useEffect(() => {
    const e = ebaySellRange(ebay);
    if (done && !failed && e) updateItem(idRef.current, { sellAloneLow: e.low, sellAloneHigh: e.high });
  }, [done, failed, ebay]);

  const running = !done;
  const okSites = rows.filter((r) => r.state === "ok");

  return (
    <section className="screen">
      <p className="muted" style={{ margin: "0.5rem 0 0" }}>{CATEGORY_LABELS[category]}, {condition.toLowerCase()}</p>
      <h1 className="display search-title">{product}</h1>

      {failed && <p className="notice error">{refused ?? "L'estimation n'a pas pu aboutir. Vérifiez votre connexion, puis réessayez."}</p>}

      <SearchProgress rows={rows} done={done} demo={demo} />

      {done && !shop && !failed && (
        <p className="notice warn" style={{ marginTop: "1rem" }}>
          Aucune boutique n&apos;a ce modèle en vente aujourd&apos;hui. Vérifiez le modèle exact, ou consultez les prix eBay et ceux des particuliers ci-dessous.
        </p>
      )}

      {shop && verdict && (
        <>
          <VerdictCard verdict={verdict} running={running} />
          <PriceScale shop={shop} verdict={verdict} />
          {myPrice !== null && (
            <PriceSlider shop={shop} verdict={verdict} value={myPrice} onChange={(v) => { priceTouched.current = true; setMyPrice(v); }} />
          )}
        </>
      )}

      {/* L'annonce, deuxième promesse du produit, juste après le prix (elle se rédige pendant la recherche). */}
      <ListingPanel
        input={input}
        sharePhotos={sharePhotos}
        myPrice={myPrice}
        onPublish={(platform) => updateItem(idRef.current, { status: "en_vente", platform })}
        canTrack={done && !failed}
      />

      <EbayPanel result={ebay} />

      {okSites.length > 0 && (
        <div className="panel">
          <h3>Les offres relevées</h3>
          <p className="small" style={{ margin: "0 0 0.5rem" }}>Le même modèle, en vente dans les boutiques d&apos;occasion.</p>
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

      {/* Liens vers d'autres sites : seulement une fois notre résultat affiché, pour ne pas faire partir l'utilisateur
          pendant l'attente. Le lien eBay disparaît quand le bloc eBay a ses propres prix. */}
      {done && (
        <div className="panel">
          <h3>Prix entre particuliers</h3>
          <p className="small" style={{ margin: 0 }}>
            Comparez aussi vous-même sur les sites entre particuliers :
          </p>
          <div className="links">
            {marketplaceLinks(product)
              .filter((l) => !(ebay?.block && l.name.startsWith("eBay")))
              .map((l) => (
                <a key={l.name} className="btn btn-quiet" href={l.url} target="_blank" rel="noopener noreferrer" style={{ background: "#fff" }}>
                  Voir sur {l.name}
                </a>
              ))}
          </div>
        </div>
      )}

      {photos.length > 0 && <StudioPhotos photos={photos} onShareable={setSharePhotos} />}

      <div className="stack" style={{ marginTop: "2rem" }}>
        {done && !failed && <a href="/grenier" className="btn btn-quiet">Voir Mon grenier</a>}
        <button className="btn btn-quiet" onClick={onRestart}>Estimer un autre objet</button>
      </div>

      <p className="footer-note">
        Prix indicatifs, comparaison non exhaustive. Estimation et annonce générées par IA. <a href="/comment-ca-marche">Comment ça marche</a>
      </p>
    </section>
  );
}

// Une seule barre pour toute la recherche. En mode démo, les écrans des agents s'affichent côte à côte
// dessous (captures rafraîchies à chaque étape). Les noms des sites restent dans « Les offres relevées ».
export function SearchProgress({ rows, done, demo }: { rows: Row[]; done: boolean; demo: boolean }) {
  const active = rows.filter((r) => r.state !== "hors_categorie");
  if (active.length === 0) return null;
  const finished = active.filter((r) => r.state === "ok" || r.state === "aucun_resultat" || r.state === "indisponible").length;
  const progress = done
    ? 1
    : active.reduce((sum, r) => sum + (r.state === "attente" ? 0 : r.state === "en_cours" ? Math.min(r.elapsed / MAX_S, 0.95) : 1), 0) / active.length;
  // Ce que l'utilisateur lit : où en est son estimation, sans détail technique.
  const label = done
    ? "Votre estimation est prête."
    : finished === 0
      ? progress < 0.3 ? "On compare les prix d'occasion…" : "On vérifie les annonces une à une…"
      : finished < active.length ? "On affine votre estimation…" : "Encore quelques secondes…";
  const live = active.filter((r) => r.state === "en_cours" || r.shot);
  return (
    <div className="search-progress" aria-live="polite">
      <div className="search-progress-head">
        <span>{label}</span>
        <span className="small num">{Math.round(progress * 100)} %</span>
      </div>
      <div className="search-bar" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(progress * 100)} aria-label="Avancement de la recherche">
        <span style={{ transform: `scaleX(${progress})` }} data-done={done} />
      </div>
      <p className="small search-sources">Boutiques consultées : {active.map((r) => r.name).join(", ")}</p>
      {demo && !done && live.length > 0 && (
        <div className="agent-grid">
          {live.map((r) => (
            <figure key={r.key} className="agent-tile" data-state={r.state}>
              {r.shot
                // eslint-disable-next-line @next/next/no-img-element
                ? <img src={r.shot} alt={`Ce que voit l'agent sur ${r.name}`} />
                : <div className="agent-tile-wait">Démarrage du navigateur…</div>}
              <figcaption>
                {r.name}
                {r.state === "ok" ? ` · ${r.offers.length} prix` : r.state === "aucun_resultat" ? " · aucun résultat" : r.state === "indisponible" ? " · indisponible" : ""}
              </figcaption>
            </figure>
          ))}
        </div>
      )}
    </div>
  );
}

function VerdictCard({ verdict, running }: { verdict: Verdict; running: boolean }) {
  const seul = verdict.recommend === "seul";
  return (
    <div className="verdict-card" aria-live="polite">
      <CoinRain />
      <p className="muted" style={{ margin: 0 }}>Où vendre ?</p>
      <h2 className="verdict-title">{seul ? "Vendez-le vous-même." : "Passez en magasin."}</h2>
      <p style={{ margin: "0.25rem 0 0" }}>
        {seul
          ? <>Vous gagnez environ <strong><CountUp value={verdict.gain} /></strong> de plus qu&apos;en magasin, en échange d&apos;une annonce à publier et d&apos;un envoi.</>
          : <>Vendre seul ne rapporterait qu&apos;environ <strong className="num">{euros(Math.max(verdict.gain, 0))}</strong> de plus. En magasin, vous êtes payé tout de suite.</>}
      </p>
      <div className="verdict-options">
        <div className="verdict-option" data-chosen={seul}>
          <span className="small">Vendre seul</span>
          <span className="verdict-amount"><CountUp value={verdict.sellAloneLow} /> – <CountUp value={verdict.sellAloneHigh} /></span>
          <span className="small">Annonce, messages, envoi</span>
        </div>
        <div className="verdict-option" data-chosen={!seul}>
          <span className="small">Offre de rachat typique</span>
          <span className="verdict-amount">≈ <CountUp value={verdict.buyback} /></span>
          <span className="small">Un passage en boutique</span>
        </div>
      </div>
      <p className="small" style={{ margin: "0.75rem 0 0" }}>
        {running ? "L'estimation s'affine encore." : "Prix indicatifs."}
      </p>
    </div>
  );
}

function PriceScale({ shop, verdict }: { shop: ShopBlock; verdict: Verdict }) {
  const min = Math.floor(Math.min(shop.buyback_low, verdict.sellAloneLow) / 10) * 10;
  const max = Math.ceil(Math.max(shop.shop_high, verdict.sellAloneHigh) / 10) * 10;
  const span = Math.max(max - min, 1);
  const pos = (v: number) => `${((v - min) / span) * 100}%`;
  const width = (a: number, b: number) => `${Math.max(((b - a) / span) * 100, 2)}%`;
  const bars = [
    { label: "Vendre seul", cls: "seul", lo: verdict.sellAloneLow, hi: verdict.sellAloneHigh, mark: verdict.sellAloneMid },
    { label: "Prix de revente en boutique", cls: "boutique", lo: shop.shop_low, hi: shop.shop_high },
    { label: "Ce qu'une boutique vous propose", cls: "magasin", lo: shop.buyback_low, hi: shop.buyback_high, mark: shop.buyback_estimate },
  ];
  return (
    <div className="scale" role="img" aria-label={bars.map((b) => `${b.label} : ${euros(b.lo)} à ${euros(b.hi)}`).join(", ")}>
      {bars.map((b) => (
        <div key={b.cls} className="scale-row">
          <div className="scale-head"><span>{b.label}</span><span className="num">{b.lo === b.hi ? euros(b.lo) : `${euros(b.lo)} – ${euros(b.hi)}`}</span></div>
          <div className="scale-track">
            <div className={`scale-bar ${b.cls}`} style={{ left: pos(b.lo), width: width(b.lo, b.hi) }} />
            {b.mark !== undefined && <div className="scale-mark" style={{ left: pos(b.mark) }} />}
          </div>
        </div>
      ))}
      <div className="scale-axis num"><span>{euros(min)}</span><span>{euros(max)}</span></div>
    </div>
  );
}

function PriceSlider({ shop, verdict, value, onChange }: { shop: ShopBlock; verdict: Verdict; value: number; onChange: (v: number) => void }) {
  const min = Math.floor(Math.min(shop.buyback_low, verdict.sellAloneLow));
  const max = Math.ceil(Math.max(shop.shop_high, verdict.sellAloneHigh));
  const zone = priceZone(value, verdict, shop);
  return (
    <div className="panel">
      <h3>Fixer mon prix</h3>
      <div className="slider-value num">{euros(value)}</div>
      <span className="zone-pill" data-zone={zone.key}>{zone.label}</span>
      <label htmlFor="price" className="sr-only">Votre prix de vente</label>
      <input
        id="price"
        type="range"
        className="slider"
        min={min}
        max={max}
        step={1}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ ["--fill" as string]: `${((value - min) / Math.max(max - min, 1)) * 100}%` }}
      />
      <div className="scale-axis num"><span>{euros(min)}</span><span>{euros(max)}</span></div>
      <p className="small" style={{ margin: "0.5rem 0 0" }}>{zone.hint} Ce prix est enregistré dans Mon grenier : saisissez-le sur le site au moment de publier.</p>
    </div>
  );
}

function ListingPanel({
  input,
  sharePhotos,
  myPrice,
  onPublish,
  canTrack,
}: {
  input: SearchInput;
  sharePhotos: string[];
  myPrice: number | null;
  onPublish: (platform: string) => void;
  canTrack: boolean;
}) {
  const { product, category, condition, withBox, accessories, details } = input;
  const [platform, setPlatform] = useState<Platform>("vinted");
  const [ads, setAds] = useState<ListingFormat[] | null>(null);
  const [adState, setAdState] = useState<"loading" | "ok" | "fallback">("loading");
  const [adError, setAdError] = useState<string | null>(null);
  const [copied, setCopied] = useState<"annonce" | "title" | "description" | null>(null);
  const [ebayCat, setEbayCat] = useState<EbayCategoryResult | null>(null);
  const ebayCatAsked = useRef(false);
  const [canShare, setCanShare] = useState(false);
  const [shareMsg, setShareMsg] = useState<string | null>(null);

  // Le partage natif n'existe qu'en HTTPS (ou localhost) et sur les navigateurs qui le gèrent : sinon on ne montre pas le bouton.
  useEffect(() => setCanShare(typeof navigator !== "undefined" && typeof navigator.share === "function"), []);

  // Catégorie eBay suggérée : demandée une seule fois, quand l'utilisateur ouvre l'onglet eBay.
  useEffect(() => {
    if (platform !== "ebay" || ebayCatAsked.current) return;
    ebayCatAsked.current = true;
    fetchEbayCategory(product, category).then(setEbayCat);
  }, [platform, product]);

  // L'annonce se rédige en parallèle des agents : elle est prête quand les prix arrivent.
  function writeListing() {
    setAdState("loading");
    setAdError(null);
    generateListing({ product, category, condition, box: withBox, accessories, details })
      .then((formats) => { setAds(formats); setAdState("ok"); })
      .catch((e: Error) => {
        setAds(fallbackListing(product, condition, withBox, accessories, details));
        setAdError(e.message);
        setAdState("fallback");
      });
  }
  useEffect(writeListing, []); // eslint-disable-line react-hooks/exhaustive-deps

  const ad = ads?.find((a) => a.key === platform) ?? null;
  const publish = PUBLISH_URLS[platform];

  function editAd(field: "title" | "description", value: string) {
    setAds((list) => list?.map((a) => (a.key === platform ? { ...a, [field]: value } : a)) ?? null);
  }

  // eBay a deux champs séparés (titre puis description) : on peut copier l'un ou l'autre.
  async function copy(what: "annonce" | "title" | "description") {
    if (!ad) return;
    const text = what === "title" ? ad.title : what === "description" ? ad.description : `${ad.title}\n\n${ad.description}`;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(what);
      setTimeout(() => setCopied((c) => (c === what ? null : c)), 2500);
    } catch {
      /* presse-papiers refusé : le texte reste sélectionnable */
    }
  }

  // Une seule feuille de partage du téléphone : photos + titre + description + prix. L'app qui la reçoit (eBay, Vinted, Notes,
  // Photos, Messages...) prend ce qu'elle sait lire. Rien ne passe par notre serveur.
  async function shareAd() {
    if (!ad) return;
    setShareMsg(null);
    const text = `${ad.title}\n\n${ad.description}${myPrice !== null ? `\n\nPrix : ${euros(myPrice)}` : ""}`;
    try {
      const files = await Promise.all(
        sharePhotos.map(async (u, i) => {
          const blob = await fetch(u).then((r) => r.blob());
          const ext = blob.type === "image/png" ? "png" : "jpg";
          return new File([blob], `snapncash-photo-${i + 1}.${ext}`, { type: blob.type || "image/jpeg" });
        }),
      );
      const withFiles = { files, title: ad.title, text };
      if (files.length && navigator.canShare?.(withFiles)) await navigator.share(withFiles);
      else await navigator.share({ title: ad.title, text }); // photos non partageables ici : le texte au moins
    } catch (e) {
      if ((e as Error).name !== "AbortError") setShareMsg("Le partage n'a pas abouti. Copiez le titre et la description, puis ajoutez vos photos à la main.");
    }
  }

  const ebayCategory = ebayCat?.state === "ok" ? ebayCat.categories[0] : null;

  return (
    <div className="panel">
      <h3>Votre annonce</h3>
      <div className="seg" role="group" aria-label="Plateforme" style={{ marginTop: "0.5rem" }}>
        {(ads ?? fallbackListing(product, condition, withBox, accessories, details)).map((a) => (
          <button key={a.key} type="button" aria-pressed={platform === a.key} onClick={() => setPlatform(a.key)}>
            {a.key === "generique" ? "Autre" : a.name}
          </button>
        ))}
      </div>

      {adState === "loading" && <p className="muted" aria-live="polite" style={{ margin: "1rem 0 0.25rem" }}>On rédige votre annonce dans les 4 formats…</p>}

      {adState === "fallback" && (
        <p className="notice warn" style={{ marginTop: "0.75rem" }}>
          {adError} Voici un brouillon simple à compléter.{" "}
          <button className="link-btn" onClick={writeListing}>Réessayer la rédaction</button>
        </p>
      )}

      {ad && adState !== "loading" && (
        <>
          <label htmlFor="ad-title" className="label" style={{ display: "flex", justifyContent: "space-between" }}>
            <span>Titre</span>
            <span className="small num" style={{ color: ad.title.length > ad.title_max ? "#991b1b" : undefined }}>{ad.title.length}/{ad.title_max}</span>
          </label>
          <input id="ad-title" className="field field-white" value={ad.title} onChange={(e) => editAd("title", e.target.value)} />
          <label htmlFor="ad-desc" className="label">Description</label>
          <textarea id="ad-desc" className="listing" style={{ marginTop: 0 }} value={ad.description} onChange={(e) => editAd("description", e.target.value)} />
          {myPrice !== null && platform !== "ebay" && <p className="small" style={{ margin: "0 0 0.75rem" }}>Votre prix : <strong className="num">{euros(myPrice)}</strong>, à saisir sur le site.</p>}

          <div className="stack">
            {platform === "ebay" ? (
              <button className="btn btn-primary" onClick={() => copy("title")}>{copied === "title" ? "Titre copié" : "Copier le titre"}</button>
            ) : (
              <button className="btn btn-primary" onClick={() => copy("annonce")}>{copied === "annonce" ? "Annonce copiée" : "Copier l'annonce"}</button>
            )}
            {canShare && (
              <button type="button" className="btn btn-quiet" style={{ background: "#fff" }} onClick={shareAd}>
                Partager photos et annonce
              </button>
            )}
            {publish && (
              <a
                className="btn btn-quiet"
                style={{ background: "#fff" }}
                href={publish.url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => { if (canTrack) onPublish(publish.name); }}
              >
                {copied ? `Coller sur ${publish.name}` : `Publier sur ${publish.name}`}
              </a>
            )}
          </div>

          {shareMsg && <p className="notice warn" style={{ marginTop: "0.75rem" }}>{shareMsg}</p>}

          {/* Fiche eBay : ce qu'il faut remplir sur eBay, dans l'ordre. L'utilisateur publie lui-même. */}
          {platform === "ebay" && (
            <div style={{ marginTop: "0.9rem" }}>
              <p className="small" style={{ margin: "0 0 0.35rem", fontWeight: 600, color: "var(--ink)" }}>Ensuite, sur eBay</p>
              <ol className="small" style={{ margin: 0, paddingLeft: "1.2rem", display: "grid", gap: "0.35rem" }}>
                <li><strong>Titre</strong> : collez-le dans le premier champ.</li>
                <li>
                  <strong>Catégorie</strong> :{" "}
                  {ebayCat === null
                    ? "on la demande à eBay…"
                    : ebayCategory
                      ? <>{ebayCategory.path}, si eBay vous demande de choisir.</>
                      : "celle qu'eBay propose pour votre titre."}
                </li>
                <li><strong>État</strong> : {ebayCondition(condition)}. L&apos;état précis est déjà dans la description.</li>
                <li><strong>Photos</strong> : ajoutez celles de votre téléphone.</li>
                <li>
                  <strong>Description</strong> :{" "}
                  <button type="button" className="link-btn" onClick={() => copy("description")}>
                    {copied === "description" ? "description copiée" : "copiez-la ici"}
                  </button>
                  , puis collez-la.
                </li>
                <li>
                  <strong>Prix</strong> : {myPrice !== null && <><strong className="num">{euros(myPrice)}</strong>, </>}
                  en « Achat immédiat ». Nos prix eBay viennent d&apos;annonces à prix fixe.
                </li>
              </ol>
            </div>
          )}
          <p className="small" style={{ marginTop: "0.6rem" }}>
            {adState === "ok" ? "Annonce générée par IA. Relisez-la avant de publier. " : ""}
            C&apos;est vous qui publiez : on ne se connecte jamais à votre compte.
          </p>
        </>
      )}
    </div>
  );
}

function priceRange(prices: number[]) {
  const low = Math.min(...prices);
  const high = Math.max(...prices);
  return low === high ? euros(low) : `${euros(low)} – ${euros(high)}`;
}

function ebaySellRange(r: EbayResult | null) {
  return r?.block ? { low: r.block.sell_low, high: r.block.sell_high, median: r.block.sell_price } : null;
}

// Bloc « Vendre seul (eBay) », séparé des boutiques (licence eBay).
function EbayPanel({ result }: { result: EbayResult | null }) {
  if (result?.state === "non_configure") return null;
  const b = result?.block;
  return (
    <div className="panel" aria-live="polite">
      <h3>Vendre seul (eBay)</h3>
      {!result && <p className="small" style={{ margin: 0 }}>On regarde les annonces eBay…</p>}
      {result?.state === "indisponible" && <p className="small" style={{ margin: 0 }}>eBay ne répond pas pour l&apos;instant.</p>}
      {result && result.state !== "indisponible" && !b && (
        <p className="small" style={{ margin: 0 }}>Trop peu d&apos;annonces eBay de ce modèle pour donner un prix.</p>
      )}
      {b && (
        <>
          <div className="slider-value num">{euros(b.sell_price)}</div>
          <p className="small" style={{ margin: "0 0 0.5rem" }}>
            Prix conseillé pour vendre vous-même. Fourchette : {euros(b.sell_low)} – {euros(b.sell_high)}.
          </p>
        </>
      )}
      {result && result.items.length > 0 && (
        <details className="site-detail">
          <summary>
            <span>Annonces eBay, même modèle</span>
            <span className="num muted">{priceRange(result.items.map((o) => o.price_eur))}</span>
          </summary>
          {result.items.map((o, i) => (
            <div key={i} className="offer">
              <span>{o.url ? <a href={o.url} target="_blank" rel="noopener noreferrer">{o.title}</a> : o.title}{o.condition ? <span className="small">, {o.condition}</span> : null}</span>
              <span className="num">{euros(o.price_eur)}</span>
            </div>
          ))}
        </details>
      )}
      <p className="small" style={{ margin: "0.5rem 0 0" }}>Annonces d&apos;occasion en cours sur eBay, en France.</p>
    </div>
  );
}

// Photos pour l'annonce, avec leur version studio (objet détouré sur fond clair, objet non modifié).
function StudioPhotos({ photos, onShareable }: { photos: string[]; onShareable: (urls: string[]) => void }) {
  const [studio, setStudio] = useState<(string | null)[]>(photos.map(() => null));
  const [show, setShow] = useState<("studio" | "original")[]>(photos.map(() => "studio"));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Le bouton « Partager » de l'annonce envoie exactement ce qui est affiché ici.
  useEffect(() => {
    onShareable(photos.map((p, i) => (show[i] === "studio" && studio[i] ? studio[i]! : p)));
  }, [photos, studio, show]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => () => studio.forEach((u) => u && URL.revokeObjectURL(u)), []); // eslint-disable-line react-hooks/exhaustive-deps

  async function run() {
    setBusy(true);
    setError(null);
    for (let i = 0; i < photos.length; i++) {
      if (studio[i]) continue;
      try {
        const src = await fetch(photos[i]).then((r) => r.blob());
        const out = await makeStudio(src);
        const url = URL.createObjectURL(out);
        setStudio((s) => s.map((v, j) => (j === i ? url : v)));
      } catch (e) {
        setError((e as Error).message);
      }
    }
    setBusy(false);
  }

  const done = studio.some(Boolean);
  return (
    <div className="panel">
      <h3>Vos photos pour l&apos;annonce</h3>
      <p className="small" style={{ margin: "0 0 0.75rem" }}>
        {done
          ? "Version studio : fond retouché, objet non modifié. Enregistrez celles que vous voulez publier."
          : "Créez une version studio : l'objet détouré sur un fond clair, comme sur les sites de seconde main haut de gamme."}
      </p>
      <div className="studio-grid">
        {photos.map((p, i) => {
          const url = show[i] === "studio" && studio[i] ? studio[i]! : p;
          return (
            <figure key={i} className="studio-item">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={url} alt={`Photo ${i + 1}${studio[i] && show[i] === "studio" ? ", version studio" : ""}`} />
              {studio[i] && (
                <figcaption>
                  <div className="seg" role="group" aria-label={`Photo ${i + 1}`}>
                    <button type="button" aria-pressed={show[i] === "studio"} onClick={() => setShow((s) => s.map((v, j) => (j === i ? "studio" : v)))}>Studio</button>
                    <button type="button" aria-pressed={show[i] === "original"} onClick={() => setShow((s) => s.map((v, j) => (j === i ? "original" : v)))}>Originale</button>
                  </div>
                  <a className="small" href={url} download={`snapncash-photo-${i + 1}${show[i] === "studio" ? "-studio" : ""}.jpg`}>Enregistrer</a>
                </figcaption>
              )}
            </figure>
          );
        })}
      </div>
      {error && <p className="notice error" style={{ marginTop: "0.75rem" }}>{error}</p>}
      {studio.some((s) => !s) && (
        <button className="btn btn-quiet" style={{ marginTop: "0.75rem", background: "var(--bg)" }} onClick={run} disabled={busy}>
          {busy ? "Création des photos studio…" : done ? "Réessayer les photos manquantes" : `Créer ${photos.length > 1 ? "les photos" : "la photo"} studio`}
        </button>
      )}
      <p className="small" style={{ margin: "0.6rem 0 0" }}>
        Détourage par un modèle d&apos;IA (Bria, via Hugging Face). Vos photos ne sont pas conservées.
      </p>
    </div>
  );
}
