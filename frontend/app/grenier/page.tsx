"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { euros } from "@/lib/api";
import { CountUp } from "@/components/CashFx";
import {
  type GrenierItem,
  type ItemStatus,
  STATUS_LABELS,
  itemValue,
  onGrenierChange,
  readGrenier,
  removeItem,
  totals,
  updateItem,
} from "@/lib/grenier";

const PRO_CART_KEY = "snapncash.pro.cart.v1";

export default function GrenierPage() {
  const [items, setItems] = useState<GrenierItem[] | null>(null);
  const [filter, setFilter] = useState<ItemStatus | "tous">("tous");
  const [proCartCount, setProCartCount] = useState(0);

  useEffect(() => {
    const refresh = () => setItems(readGrenier());
    refresh();
    return onGrenierChange(refresh);
  }, []);

  useEffect(() => {
    const refresh = () => {
      try {
        const saved = JSON.parse(localStorage.getItem(PRO_CART_KEY) || "[]");
        setProCartCount(Array.isArray(saved) ? saved.length : 0);
      } catch { setProCartCount(0); }
    };
    refresh();
    window.addEventListener("storage", refresh);
    return () => window.removeEventListener("storage", refresh);
  }, []);

  if (items === null) return <main className="page" />;
  const t = totals(items);
  const shown = filter === "tous" ? items : items.filter((x) => x.status === filter);

  return (
    <main className="page screen">
      <h1 className="display">Mon grenier</h1>

      <Link href="/pro#pro-cart" className="grenier-pro-cart">
        <span className="grenier-pro-cart-icon" aria-hidden><CartGlyph /></span>
        <span>
          <strong>Panier revendeur</strong>
          <span className="small">Retrouvez les bonnes affaires que vous avez retenues.</span>
        </span>
        <span className="grenier-pro-cart-count num">{proCartCount}</span>
      </Link>

      {items.length === 0 ? (
        <>
          <p className="lede">Votre grenier est vide. Estimez un premier objet : il apparaîtra ici avec sa valeur.</p>
          <Link href="/" className="btn btn-primary">Estimer un objet</Link>
        </>
      ) : (
        <>
          <div className="grenier-total">
            <p className="muted" style={{ margin: 0 }}>Ce qui dort encore chez vous vaut environ</p>
            <div className="verdict-price"><CountUp value={t.sleepingValue} /></div>
            <p className="small" style={{ margin: "0.4rem 0 0" }}>
              {t.count} objet{t.count > 1 ? "s" : ""} estimé{t.count > 1 ? "s" : ""}
              {t.soldCount > 0 ? `, ${euros(t.earned)} déjà gagnés sur ${t.soldCount} vente${t.soldCount > 1 ? "s" : ""}` : ""}.
            </p>
          </div>

          <div className="seg" role="group" aria-label="Filtrer" style={{ margin: "1.5rem 0 0.5rem" }}>
            {(["tous", "a_vendre", "en_vente", "vendu"] as const).map((f) => (
              <button key={f} type="button" aria-pressed={filter === f} onClick={() => setFilter(f)}>
                {f === "tous" ? "Tous" : STATUS_LABELS[f]}
              </button>
            ))}
          </div>

          <ul className="grenier-list">
            {shown.map((x) => <ItemRow key={x.id} item={x} />)}
          </ul>
          {shown.length === 0 && <p className="muted">Aucun objet dans cette liste.</p>}
          <p className="small" style={{ marginTop: "1.5rem" }}>Votre grenier est gardé uniquement sur cet appareil.</p>
        </>
      )}
    </main>
  );
}

function CartGlyph() {
  return <svg viewBox="0 0 24 24" fill="none"><path d="M3 4h2l2.1 10.2a2 2 0 0 0 2 1.6h7.8a2 2 0 0 0 2-1.6L20 8H6.1M9 20h.01M17 20h.01" /></svg>;
}

function ItemRow({ item }: { item: GrenierItem }) {
  const [selling, setSelling] = useState(false);
  const [sold, setSold] = useState(String(Math.round(item.myPrice ?? item.sellAloneLow ?? item.buyback ?? 0)));

  return (
    <li className="grenier-item">
      <div className="grenier-head">
        <span>
          <span className="site-name">{item.product}</span>
          <br />
          <span className="site-step">
            {item.condition}, estimé le {new Date(item.date).toLocaleDateString("fr-FR")}
            {item.platform ? `, en vente sur ${item.platform}` : ""}
          </span>
        </span>
        <span className="grenier-value num">{euros(itemValue(item))}</span>
      </div>

      <div className="grenier-actions">
        <span className="status-pill" data-status={item.status}>{STATUS_LABELS[item.status]}</span>
        {item.status !== "vendu" && !selling && (
          <button className="link-btn" onClick={() => setSelling(true)}>Marquer comme vendu</button>
        )}
        {item.status === "vendu" && (
          <button className="link-btn" onClick={() => updateItem(item.id, { status: "en_vente", soldPrice: null })}>Annuler la vente</button>
        )}
        <button className="link-btn" style={{ color: "var(--ink-soft)" }} onClick={() => removeItem(item.id)}>Retirer</button>
      </div>

      {selling && (
        <form
          className="sold-form"
          onSubmit={(e) => {
            e.preventDefault();
            const v = Number(sold.replace(",", "."));
            if (v > 0) updateItem(item.id, { status: "vendu", soldPrice: v });
            setSelling(false);
          }}
        >
          <label htmlFor={`sold-${item.id}`} className="small">Vendu à</label>
          <input id={`sold-${item.id}`} className="field num" inputMode="decimal" value={sold} onChange={(e) => setSold(e.target.value)} style={{ maxWidth: "7rem" }} />
          <span className="small">€</span>
          <button className="btn btn-primary" style={{ width: "auto", padding: "0.6rem 1rem" }} type="submit">Valider</button>
        </form>
      )}
    </li>
  );
}
