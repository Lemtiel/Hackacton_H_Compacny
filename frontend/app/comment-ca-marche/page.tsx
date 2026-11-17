import Link from "next/link";

export const metadata = { title: "Comment ça marche · Snap N Cash" };

export default function HowItWorks() {
  return (
    <main className="page screen">
      <h1 className="display">Comment ça marche</h1>
      <p className="lede">Snap N Cash compare des prix d&apos;occasion à votre place. Voici ce que nous consultons et comment nous calculons.</p>

      <h2>Les sites consultés</h2>
      <p className="muted">
        Nos agents IA visitent Easy Cash, Gamecash, Troc.com, Cash Converters, Certideal et Swappie, comme le ferait une personne, pour relever les prix des
        objets en vente. Les prix eBay viennent de l&apos;API officielle d&apos;eBay. La comparaison n&apos;est pas exhaustive : d&apos;autres
        sites vendent aussi ces objets.
      </p>
      <p className="muted">
        Vinted et Leboncoin interdisent la lecture automatisée de leurs annonces. Nous ouvrons donc leur recherche dans votre navigateur, et
        c&apos;est vous qui consultez leurs prix.
      </p>

      <h2 style={{ marginTop: "2rem" }}>Le calcul</h2>
      <p className="muted">
        Les prix très éloignés des autres sont écartés. Le prix « en magasin » estime ce qu&apos;une boutique vous proposerait : il part du prix
        auquel les boutiques revendent l&apos;objet, multiplié par un coefficient. C&apos;est une estimation basse, l&apos;offre réelle se fait
        en boutique après inspection.
      </p>
      <p className="muted">Aucun site n&apos;est mis en avant contre paiement. Les résultats sont classés par prix.</p>

      <h2 style={{ marginTop: "2rem" }}>Vos données</h2>
      <p className="muted">
        Une intelligence artificielle reconnaît l&apos;objet sur votre photo. Une photo où apparaît un visage est refusée. Nous ne gardons ni la
        photo, ni vos recherches : votre historique reste dans votre navigateur.
      </p>

      <p style={{ marginTop: "2.5rem" }}>
        <Link href="/" className="btn btn-quiet">
          Estimer un objet
        </Link>
      </p>
    </main>
  );
}
