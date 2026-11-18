import Link from "next/link";
import { notFound } from "next/navigation";
import { LAST_UPDATE, LEGAL_PAGES, legalPage } from "@/lib/legal";

export function generateStaticParams() {
  return LEGAL_PAGES.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const page = legalPage((await params).slug);
  return { title: page ? `${page.title} · Snap N Cash` : "Snap N Cash" };
}

export default async function LegalPage({ params }: { params: Promise<{ slug: string }> }) {
  const page = legalPage((await params).slug);
  if (!page) notFound();
  return (
    <main className="page screen legal">
      <Link href="/reglages" className="back-link">← Réglages</Link>
      <h1 className="display search-title">{page.title}</h1>
      <p className="small">Mise à jour : {LAST_UPDATE}. Prototype de hackathon, sans activité commerciale.</p>
      <article className="legal-body">{page.body}</article>
    </main>
  );
}
