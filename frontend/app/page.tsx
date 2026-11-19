"use client";

import { type ReactNode, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { CATEGORY_LABELS, type Category, euros, identifyPhotos, wakeServer } from "@/lib/api";
import { onGrenierChange, readGrenier, totals } from "@/lib/grenier";
import { CONDITIONS, type Condition } from "@/lib/listing";
import { applyVariant, guessCategory, variantSuggestion } from "@/lib/variants";
import SearchScreen, { type SearchInput } from "@/components/SearchScreen";
import { onPendingPhoto, takePendingPhoto } from "@/lib/pending";

type Step = "home" | "capture" | "identifying" | "confirm" | "search";

// Prise de vue guidée : chaque photo a un rôle. Les 3 servent à reconnaître l'objet, puis à l'annonce.
const SHOTS = [
  { title: "L'objet de face", tip: "En entier, sur un fond uni, face à une fenêtre. Écran éteint pour éviter les reflets.", required: true },
  { title: "Le dos ou l'étiquette", tip: "Là où sont écrits le modèle et la capacité : dos du téléphone, dessous de la console, tranche du jeu.", required: false },
  { title: "Un détail", tip: "Une rayure, la boîte, les manettes ou le chargeur. Utile pour l'état et pour l'annonce.", required: false },
];

const CATEGORIES = Object.keys(CATEGORY_LABELS) as Category[];
const CAPACITY = /\b\d{2,4}\s?(go|gb|to|tb)\b/i; // « 128 GB » rendu en anglais par le modèle compte aussi

export default function Home() {
  const [step, setStep] = useState<Step>("home");
  useEffect(() => wakeServer(), []); // réveille le serveur pendant que l'utilisateur prend sa photo
  const [error, setError] = useState<string | null>(null);
  const [photos, setPhotos] = useState<string[]>([]);
  const [shots, setShots] = useState<(File | null)[]>([null, null, null]);
  const [extras, setExtras] = useState<File[]>([]); // jusqu'à 5 photos en plus, pour l'annonce et le studio
  const [product, setProduct] = useState("");
  const [category, setCategory] = useState<Category>("console");
  const [lowConfidence, setLowConfidence] = useState(false);
  const [hint, setHint] = useState("");
  const [condition, setCondition] = useState<Condition>("Bon état");
  const [withBox, setWithBox] = useState(true);
  const [accessories, setAccessories] = useState("");
  const [details, setDetails] = useState("");
  const [search, setSearch] = useState<SearchInput | null>(null);

  // Première photo prise depuis l'accueil : on ouvre la prise de vue guidée avec la case 1 remplie.
  function onPhoto(file?: File) {
    if (!file) return;
    reset();
    setShots([file, null, null]);
    setStep("capture");
    window.scrollTo({ top: 0 });
  }

  // Photo prise avec le bouton central de la barre du bas.
  useEffect(() => {
    const take = () => {
      const f = takePendingPhoto();
      if (f) onPhoto(f);
    };
    take();
    return onPendingPhoto(take);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function setShot(i: number, file: File | null) {
    setShots((cur) => cur.map((f, j) => (j === i ? file : f)));
  }

  async function identify() {
    const files = shots.filter((f): f is File => !!f);
    if (files.length === 0) return;
    setError(null);
    // Les 3 photos guidées servent à reconnaître l'objet ; toutes (jusqu'à 8) servent à l'annonce et au studio.
    setPhotos([...files, ...extras].map((f) => URL.createObjectURL(f)));
    setStep("identifying");
    try {
      const ident = await identifyPhotos(files);
      // Seule la capacité aide la recherche. La couleur (souvent en anglais : « Midnight ») ferait
      // écarter les annonces des boutiques : elle va dans les détails, pour l'annonce.
      const variant = ident.variant?.trim() || "";
      const capacity = variant.match(CAPACITY)?.[0];
      setProduct([ident.product, capacity].filter(Boolean).join(" "));
      setHint(ident.kind?.trim() || "");
      const rest = capacity ? variant.replace(capacity, "").replace(/^[\s,]+|[\s,]+$/g, "") : variant;
      if (rest) setDetails(`Couleur ou édition : ${rest}`);
      if (CATEGORIES.includes(ident.category as Category)) setCategory(ident.category as Category);
      setLowConfidence(ident.confidence < 0.7 || !ident.model);
    } catch (e) {
      setError((e as Error).message);
      setLowConfidence(true);
    }
    setStep("confirm");
  }

  function reset() {
    setError(null);
    setPhotos([]);
    setShots([null, null, null]);
    setExtras([]);
    setProduct("");
    setAccessories("");
    setDetails("");
    setLowConfidence(false);
    setHint("");
    setSearch(null);
  }

  function startOver() {
    reset();
    setStep("home");
    window.scrollTo({ top: 0 });
  }

  function launch() {
    setSearch({ product: product.trim(), category, condition, withBox, accessories, details, photos, hint });
    setStep("search");
    window.scrollTo({ top: 0 });
  }

  const suggestion = variantSuggestion(product, category);

  return (
    <main className="page">
      {step === "home" && (
        <HomeScreen
          onPhoto={onPhoto}
          onText={(p) => { reset(); setProduct(p); setCategory(guessCategory(p) ?? "console"); setStep("confirm"); window.scrollTo({ top: 0 }); }}
        />
      )}

      {step === "capture" && (
        <CaptureScreen
          shots={shots}
          onShot={setShot}
          extras={extras}
          onExtras={setExtras}
          onIdentify={identify}
          onText={() => { reset(); setStep("home"); }}
        />
      )}

      {step === "identifying" && (
        <section className="screen" aria-live="polite">
          {photos[0] && <img src={photos[0]} alt="Votre photo" className="photo photo-scan" />}
          <h2 style={{ marginTop: "1.5rem" }}>On reconnaît votre objet…</h2>
          <p className="muted">
            Quelques secondes. Vos photos ne sont pas conservées.
          </p>
        </section>
      )}

      {step === "confirm" && (
        <section className="screen">
          {photos.length > 0 && (
            <div className="thumbs" style={{ marginBottom: "0.5rem" }}>
              {photos.map((p, i) => <img key={i} src={p} alt={`Photo ${i + 1}`} className={i === 0 ? "photo" : "thumb"} />)}
            </div>
          )}
          {photos.length > 0 && <p className="small">Vos photos restent sur votre téléphone, pour l&apos;annonce.</p>}

          {error && <p className="notice error" style={{ marginTop: "1rem" }}>{error}</p>}

          <label className="label" htmlFor="product">Votre objet</label>
          <input id="product" className="field" value={product} onChange={(e) => setProduct(e.target.value)} placeholder="Ex. Nintendo Switch OLED" autoComplete="off" />
          {lowConfidence && !error && (
            <p className="small" style={{ marginTop: "0.5rem" }}>Vérifiez le modèle exact : le prix en dépend.</p>
          )}

          {suggestion && (
            <>
              <span className="label">{suggestion.label}</span>
              <div className="chips">
                {suggestion.options.map((o) => {
                  const next = applyVariant(product, suggestion, o);
                  return (
                    <button key={o} type="button" className="chip" aria-pressed={next.toLowerCase() === product.trim().toLowerCase()} onClick={() => setProduct(next)}>
                      {o}
                    </button>
                  );
                })}
              </div>
            </>
          )}

          <span className="label">Catégorie</span>
          <div className="chips">
            {CATEGORIES.map((c) => (
              <button key={c} type="button" className="chip" aria-pressed={category === c} onClick={() => setCategory(c)}>{CATEGORY_LABELS[c]}</button>
            ))}
          </div>

          <span className="label">État</span>
          <div className="chips" role="group" aria-label="État">
            {CONDITIONS.map((c) => (
              <button key={c} type="button" className="chip" aria-pressed={condition === c} onClick={() => setCondition(c)}>{c}</button>
            ))}
          </div>

          <span className="label">Boîte d&apos;origine</span>
          <div className="seg" role="group" aria-label="Boîte d'origine">
            <button type="button" aria-pressed={withBox} onClick={() => setWithBox(true)}>Avec</button>
            <button type="button" aria-pressed={!withBox} onClick={() => setWithBox(false)}>Sans</button>
          </div>

          <label className="label" htmlFor="accessories">Accessoires fournis <span className="small">(facultatif)</span></label>
          <input id="accessories" className="field" value={accessories} maxLength={200} onChange={(e) => setAccessories(e.target.value)} placeholder="Ex. chargeur, coque, câble" autoComplete="off" />

          <label className="label" htmlFor="details">Détails <span className="small">(facultatif)</span></label>
          <textarea id="details" className="field" rows={2} value={details} maxLength={400} onChange={(e) => setDetails(e.target.value)} placeholder="Couleur, défauts visibles, état de la batterie" />
          <p className="small" style={{ marginTop: "0.4rem" }}>Ces informations servent à rédiger votre annonce. Rien n&apos;est inventé.</p>

          <div className="stack" style={{ marginTop: "2rem" }}>
            <button className="btn btn-primary" disabled={product.trim().length < 2} onClick={launch}>Estimer le prix</button>
            <button className="link-btn" onClick={startOver}>Recommencer</button>
          </div>
        </section>
      )}

      {step === "search" && search && <SearchScreen input={search} onRestart={startOver} />}
    </main>
  );
}

function HomeScreen({ onPhoto, onText }: { onPhoto: (f?: File) => void; onText: (product: string) => void }) {
  const cameraRef = useRef<HTMLInputElement>(null);
  const galleryRef = useRef<HTMLInputElement>(null);
  const [text, setText] = useState("");
  const [summary, setSummary] = useState<{ count: number; value: number } | null>(null);

  useEffect(() => {
    const refresh = () => {
      const t = totals(readGrenier());
      setSummary(t.count ? { count: t.count, value: t.sleepingValue } : null);
    };
    refresh();
    return onGrenierChange(refresh);
  }, []);

  return (
    <section className="screen">
      <div className="hero">
        <div className="hero-card">
          <span className="hero-tag" aria-hidden><span className="hero-tag-hole" />€</span>
          <h1 className="display hero-title"><span className="hero-sticker">Vendez</span> ce qui dort chez vous.</h1>
          <p className="lede">Une photo de l&apos;objet : vous savez combien il vaut, où le vendre, et votre annonce est prête.</p>
        </div>
      </div>

      <div className="stack">
        <button className="btn btn-primary" onClick={() => cameraRef.current?.click()}>
          <CameraIcon /> Prendre une photo
        </button>
        <button className="btn btn-quiet" onClick={() => galleryRef.current?.click()}>Choisir une photo</button>
      </div>
      <input ref={cameraRef} type="file" accept="image/*" capture="environment" className="sr-only" onChange={(e) => onPhoto(e.target.files?.[0])} />
      <input ref={galleryRef} type="file" accept="image/*" className="sr-only" onChange={(e) => onPhoto(e.target.files?.[0])} />

      <ul className="tips" aria-label="Conseils pour la photo">
        <li><TipIcon kind="seul" /> Objet seul, aucun visage sur la photo.</li>
        <li><TipIcon kind="lumiere" /> Lumière franche, face à une fenêtre.</li>
        <li><TipIcon kind="etiquette" /> Téléphone : visez le dos ou l&apos;étiquette.</li>
      </ul>

      <ExampleCards onPick={onText} />

      <div className="or">ou</div>
      <form className="stack" onSubmit={(e) => { e.preventDefault(); if (text.trim().length >= 2) onText(text.trim()); }}>
        <label htmlFor="text" className="sr-only">Nom de l&apos;objet</label>
        <input id="text" className="field" value={text} onChange={(e) => setText(e.target.value)} placeholder="Tapez le nom de l'objet" autoComplete="off" />
        <button className="btn btn-quiet" type="submit" disabled={text.trim().length < 2}>Continuer</button>
      </form>

      <p className="pro-entry">
        <Link href="/pro">Vous êtes revendeur ?</Link>
      </p>

      {summary && (
        <Link href="/grenier" className="grenier-teaser">
          <span>
            <span className="small">Mon grenier, {summary.count} objet{summary.count > 1 ? "s" : ""}</span>
            <span className="grenier-teaser-value num">{euros(summary.value)}</span>
          </span>
          <span className="small" aria-hidden>Voir</span>
        </Link>
      )}
    </section>
  );
}

// Prix médians réellement relevés par nos agents (JOURNAL.md) : ce sont les prix AFFICHÉS PAR LES BOUTIQUES,
// pas ce que touche le vendeur. La carte le dit ; l'estimation donne ensuite le rachat et la vente entre particuliers.
// Switch : 16/11, 7 prix. iPhone 13 128 Go : 17/11, Certideal. DualSense : 17/11, 7 prix.
const EXAMPLES = [
  { name: "Nintendo Switch", price: 166, art: "console" },
  { name: "Apple iPhone 13 128 Go", price: 266, art: "phone" },
  { name: "Sony DualSense", price: 53, art: "pad" },
] as const;

function ExampleCards({ onPick }: { onPick: (product: string) => void }) {
  return (
    <section className="examples" aria-labelledby="examples-title">
      <h2 id="examples-title" className="examples-title">Combien vous en tireriez ?</h2>
      <div className="examples-row">
        {EXAMPLES.map((e) => (
          <button key={e.name} type="button" className="example-card" data-art={e.art} onClick={() => onPick(e.name)}>
            <span className="example-art" aria-hidden>{ART[e.art]}</span>
            <span className="example-name">{e.name.replace("Apple ", "").replace(" 128 Go", "")}</span>
            <span className="example-shop small">En boutique <span className="num">≈ {e.price} €</span></span>
            <span className="example-cta">Estimer le mien →</span>
          </button>
        ))}
      </div>
      <p className="small" style={{ margin: "0.5rem 0 0" }}>Prix de revente affichés par les boutiques d&apos;occasion (relevés les 16 et 17/11). Ce que vous touchez est plus bas : l&apos;estimation vous dit combien, en magasin et entre particuliers.</p>
    </section>
  );
}

const ART: Record<string, ReactNode> = {
  console: (
    <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="8" width="26" height="16" rx="6" /><path d="M9 13v6M6 16h6" /><circle cx="21" cy="14" r="1.6" /><circle cx="24" cy="18" r="1.6" /></svg>
  ),
  phone: (
    <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="3" width="14" height="26" rx="3.5" /><path d="M14 25.5h4" /></svg>
  ),
  pad: (
    <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 11h16a5 5 0 0 1 5 5v3a4 4 0 0 1-7 2.6L20 19h-8l-2 2.6A4 4 0 0 1 3 19v-3a5 5 0 0 1 5-5Z" /><path d="M9 14v4M7 16h4" /><circle cx="22" cy="15" r="1.3" /></svg>
  ),
};

const MAX_EXTRAS = 5;

function CaptureScreen({ shots, onShot, extras, onExtras, onIdentify, onText }: {
  shots: (File | null)[];
  onShot: (i: number, f: File | null) => void;
  extras: File[];
  onExtras: (files: File[]) => void;
  onIdentify: () => void;
  onText: () => void;
}) {
  const count = shots.filter(Boolean).length;
  return (
    <section className="screen">
      <h1 className="display search-title">Trois photos, un prix plus juste.</h1>
      <p className="lede" style={{ marginBottom: "1.25rem" }}>
        Chaque photo aide à reconnaître le modèle exact. Seule la première est obligatoire.
      </p>
      <p className="notice" style={{ marginBottom: "1rem" }}>L&apos;objet seul, sans personne : une photo avec un visage est refusée.</p>
      <ol className="shots">
        {SHOTS.map((s, i) => (
          <ShotSlot key={s.title} index={i} title={s.title} tip={s.tip} required={s.required} file={shots[i]} onFile={(f) => onShot(i, f)} />
        ))}
      </ol>
      <ExtraPhotos files={extras} onChange={onExtras} />
      <div className="stack" style={{ marginTop: "1.5rem" }}>
        <button className="btn btn-primary" disabled={count === 0} onClick={onIdentify}>
          Reconnaître mon objet{count > 1 ? ` (${count} photos)` : ""}
        </button>
        <button className="link-btn" onClick={onText}>Taper le nom à la place</button>
      </div>
    </section>
  );
}

// Photos en plus des 3 guidées : jamais envoyées pour la reconnaissance, seulement pour l'annonce et le studio.
function ExtraPhotos({ files, onChange }: { files: File[]; onChange: (f: File[]) => void }) {
  const ref = useRef<HTMLInputElement>(null);
  const [urls, setUrls] = useState<string[]>([]);
  useEffect(() => {
    const u = files.map((f) => URL.createObjectURL(f));
    setUrls(u);
    return () => u.forEach((x) => URL.revokeObjectURL(x));
  }, [files]);
  const left = MAX_EXTRAS - files.length;
  return (
    <section className="extras" aria-labelledby="extras-title">
      <div className="extras-head">
        <span id="extras-title" className="shot-title">Photos en plus pour l&apos;annonce <span className="small">(facultatif, {MAX_EXTRAS} max)</span></span>
        <span className="small num">{files.length}/{MAX_EXTRAS}</span>
      </div>
      <p className="small" style={{ margin: "0.2rem 0 0.6rem" }}>Autres angles, accessoires, défauts. Elles servent à votre annonce et aux photos studio.</p>
      <div className="extras-grid">
        {urls.map((u, i) => (
          <div key={u} className="extra">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={u} alt={`Photo en plus ${i + 1}`} />
            <button type="button" className="extra-remove" aria-label={`Retirer la photo en plus ${i + 1}`} onClick={() => onChange(files.filter((_, j) => j !== i))}>×</button>
          </div>
        ))}
        {left > 0 && (
          <button type="button" className="extra-add" onClick={() => ref.current?.click()} aria-label="Ajouter des photos en plus">+</button>
        )}
      </div>
      <input
        ref={ref}
        type="file"
        accept="image/*"
        multiple
        className="sr-only"
        onChange={(e) => {
          const picked = Array.from(e.target.files ?? []);
          onChange([...files, ...picked].slice(0, MAX_EXTRAS));
          e.target.value = "";
        }}
      />
    </section>
  );
}

function ShotSlot({ index, title, tip, required, file, onFile }: {
  index: number; title: string; tip: string; required: boolean; file: File | null; onFile: (f: File | null) => void;
}) {
  const ref = useRef<HTMLInputElement>(null);
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    if (!file) { setUrl(null); return; }
    const u = URL.createObjectURL(file);
    setUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);
  const id = `shot-${index}`;
  return (
    <li className="shot" data-filled={!!file}>
      <button type="button" className="shot-pic" onClick={() => ref.current?.click()} aria-label={file ? `Changer la photo : ${title}` : `Ajouter la photo : ${title}`}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        {url ? <img src={url} alt="" /> : <span aria-hidden>+</span>}
      </button>
      <div className="shot-text">
        <span className="shot-title">{index + 1}. {title} {!required && <span className="small">(facultatif)</span>}</span>
        <span className="small">{tip}</span>
        {file && <button type="button" className="link-btn small-link" onClick={() => onFile(null)}>Retirer</button>}
      </div>
      {/* Sans « capture » : le téléphone propose l'appareil photo ou la galerie. */}
      <input id={id} ref={ref} type="file" accept="image/*" className="sr-only" onChange={(e) => { onFile(e.target.files?.[0] ?? null); e.target.value = ""; }} />
    </li>
  );
}

function CameraIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.3l1.2-1.6A1 1 0 0 1 9.8 4h4.4a1 1 0 0 1 .8.4L16.2 6h1.3A2.5 2.5 0 0 1 20 8.5v8a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 16.5v-8Z" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="12" cy="12.5" r="3.5" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function TipIcon({ kind }: { kind: "seul" | "lumiere" | "etiquette" }) {
  const paths = {
    seul: <rect x="5" y="5" width="14" height="14" rx="3" stroke="currentColor" strokeWidth="1.8" />,
    lumiere: <><circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.8" /><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></>,
    etiquette: <><path d="M4 12.5V5a1 1 0 0 1 1-1h7.5L20 11.5 12.5 19 4 12.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><circle cx="8.5" cy="8.5" r="1.3" fill="currentColor" /></>,
  };
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>{paths[kind]}</svg>;
}
