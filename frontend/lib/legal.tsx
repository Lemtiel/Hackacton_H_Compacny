// Pages légales de Snap N Cash. Base : docs/produit/comment-ca-marche-mentions.md (Tristan) et le fonctionnement réel
// de l'app (JOURNAL.md). Textes de prototype, à faire relire par un juriste avant tout lancement.
import type { ReactNode } from "react";

// À compléter par l'équipe : l'adresse de contact publique (jamais celle du PDF du brief).
export const CONTACT_EMAIL = "";
export const LAST_UPDATE = "18 novembre 2026";

export const SITES = "Easy Cash, Gamecash, Troc.com, Cash Converters, Certideal et Swappie";

function Contact() {
  return CONTACT_EMAIL ? <strong className="selectable">{CONTACT_EMAIL}</strong> : <strong>adresse de l&apos;équipe, communiquée sur demande auprès d&apos;Eugenia School</strong>;
}

export type LegalPage = { slug: string; title: string; summary: string; body: ReactNode };

export const LEGAL_PAGES: LegalPage[] = [
  {
    slug: "mentions-legales",
    title: "Mentions légales",
    summary: "Qui édite et héberge Snap N Cash.",
    body: (
      <>
        <h2>Éditeur</h2>
        <p>
          Snap N Cash est un prototype réalisé par l&apos;équipe 13 du hackathon Eugenia School × H Company × Vercel × Hugging Face
          (16 au 20 novembre 2026) : Stephen Morlot, Jude Buyikana, Josia Tatou, Sebastian Espinosa, Kevin Assombi et Tristan David.
          Ce projet étudiant n&apos;a aucune activité commerciale.
        </p>
        <p>Directeur de la publication : Jude Buyikana, pilote du projet. Contact : <Contact />.</p>
        <h2>Hébergement</h2>
        <p>Interface : Vercel Inc. (vercel.com). Serveur : Hugging Face (huggingface.co).</p>
        <h2>Services utilisés</h2>
        <p>
          Navigation sur les sites de prix : Agent API de H Company. Reconnaissance des objets et rédaction des annonces : modèles d&apos;IA
          via Hugging Face. Photos studio : modèle Bria, hébergé par fal.ai. Prix entre particuliers et catégorie suggérée pour publier sur eBay : API officielle d&apos;eBay.
        </p>
        <h2>Marques</h2>
        <p>
          Les noms {SITES}, eBay, Vinted et Leboncoin appartiennent à leurs titulaires. Ils sont cités pour indiquer la source des prix,
          sans logo et sans lien de partenariat.
        </p>
      </>
    ),
  },
  {
    slug: "cgu",
    title: "Conditions générales d'utilisation",
    summary: "Les règles d'usage de l'app.",
    body: (
      <>
        <h2>1. Objet</h2>
        <p>
          Snap N Cash estime le prix de revente d&apos;un objet high-tech ou d&apos;un jeu vidéo d&apos;occasion, conseille un canal de vente et
          rédige une annonce. L&apos;utiliser vaut acceptation des présentes conditions.
        </p>
        <h2>2. Accès</h2>
        <p>L&apos;app est gratuite, sans compte et sans paiement. Il s&apos;agit d&apos;un prototype : elle peut être interrompue ou modifiée à tout moment.</p>
        <h2>3. Les prix sont indicatifs</h2>
        <p>
          Les prix sont relevés sur {SITES}, et sur eBay par son API officielle. La comparaison n&apos;est pas exhaustive : d&apos;autres sites
          vendent ces objets. L&apos;estimation « en magasin » est une estimation typique : seule l&apos;offre faite en boutique, après inspection, fait foi.
          Snap N Cash ne garantit ni un prix de vente ni une vente.
        </p>
        <h2>4. Contenus générés par IA</h2>
        <p>
          La reconnaissance de l&apos;objet et l&apos;annonce sont générées par intelligence artificielle. Vérifiez le modèle reconnu et relisez
          l&apos;annonce avant de la publier : vous restez responsable de ce que vous publiez. La version studio d&apos;une photo change le fond,
          jamais l&apos;objet.
        </p>
        <h2>5. Vos engagements</h2>
        <ul>
          <li>Photographier uniquement l&apos;objet : une photo où apparaît une personne est refusée.</li>
          <li>Ne pas utiliser l&apos;app de manière automatisée ou pour surcharger les sites consultés.</li>
          <li>Publier vous-même vos annonces, dans le respect des règles de chaque site.</li>
        </ul>
        <h2>6. Sites tiers</h2>
        <p>
          Les liens vers les annonces, Vinted, Leboncoin ou eBay ouvrent des sites que Snap N Cash ne contrôle pas. Vinted et Leboncoin ne sont
          pas consultés par nos agents : le bouton ouvre leur recherche dans votre navigateur.
        </p>
        <h2>7. Données personnelles</h2>
        <p>Voir la page « Confidentialité ».</p>
        <h2>8. Droit applicable</h2>
        <p>Les présentes conditions relèvent du droit français.</p>
      </>
    ),
  },
  {
    slug: "cgv",
    title: "Conditions générales de vente",
    summary: "Aucun service payant à ce jour.",
    body: (
      <>
        <p>
          Snap N Cash ne vend rien aujourd&apos;hui : l&apos;app est un prototype gratuit, sans abonnement ni paiement. Aucune somme ne peut vous être
          demandée.
        </p>
        <p>
          Si une offre payante voit le jour, ses conditions de vente (prix, durée, résiliation, droit de rétractation de 14 jours) seront publiées ici
          avant toute souscription.
        </p>
      </>
    ),
  },
  {
    slug: "confidentialite",
    title: "Confidentialité",
    summary: "Les données traitées et vos droits (RGPD).",
    body: (
      <>
        <h2>En bref</h2>
        <p>Pas de compte. Nous ne conservons ni vos photos, ni vos recherches, ni les annonces relevées. Votre historique reste sur votre appareil.</p>
        <h2>Ce que nous traitons, et pourquoi</h2>
        <ul>
          <li>
            <strong>Vos photos (jusqu&apos;à 8).</strong> Les 3 photos guidées servent à reconnaître l&apos;objet. Un contrôle refuse toute photo où apparaît
            un visage, sur notre serveur, avant tout envoi. Les photos sont traitées en mémoire puis effacées.
          </li>
          <li>
            <strong>Le nom de l&apos;objet, son état, ses accessoires et vos précisions.</strong> Ils servent à chercher des prix comparables et à rédiger l&apos;annonce.
          </li>
          <li>
            <strong>Votre historique (Mon grenier) et vos réglages.</strong> Ils restent dans votre navigateur, sur cet appareil.
          </li>
        </ul>
        <p>Base légale : l&apos;exécution du service que vous demandez.</p>
        <h2>Qui reçoit quoi</h2>
        <ul>
          <li>Hugging Face et les fournisseurs de modèles qu&apos;il sélectionne : les photos guidées, pour la reconnaissance ; la description de l&apos;objet, pour l&apos;annonce.</li>
          <li>fal.ai (modèle Bria) : une photo, seulement si vous créez sa version studio.</li>
          <li>H Company : le nom de l&apos;objet, son état, la présence de la boîte, les accessoires et les détails que vous saisissez, pour que nos agents relèvent des prix comparables. N&apos;y écrivez aucune information personnelle. Les captures de leur navigation suivent la politique de conservation de H Company.</li>
          <li>eBay : le nom de l&apos;objet, pour sa recherche officielle et pour suggérer la catégorie de votre annonce.</li>
          <li>Vercel et Hugging Face : l&apos;hébergement de l&apos;app.</li>
        </ul>
        <p>Certains de ces prestataires sont situés hors de l&apos;Union européenne, notamment aux États-Unis.</p>
        <h2>Vos droits</h2>
        <p>
          Vous pouvez demander l&apos;accès, la rectification, l&apos;effacement ou vous opposer au traitement : <Contact />. Comme nous ne gardons rien,
          il n&apos;y a en pratique rien à effacer sur nos serveurs. Vous pouvez effacer Mon grenier dans Réglages. Vous pouvez aussi saisir la CNIL (cnil.fr).
        </p>
      </>
    ),
  },
  {
    slug: "cookies",
    title: "Cookies",
    summary: "Pas de cookie, pas de mesure d'audience.",
    body: (
      <>
        <p>Snap N Cash ne dépose aucun cookie et n&apos;utilise aucun outil de mesure d&apos;audience ni de publicité.</p>
        <p>L&apos;app garde seulement, dans le stockage local de votre navigateur :</p>
        <ul>
          <li>Mon grenier : vos objets estimés, leur statut et vos prix ;</li>
          <li>vos réglages : thème, animations, mode démo ;</li>
          <li>le fait d&apos;avoir vu l&apos;écran de découverte.</li>
        </ul>
        <p>
          Ces informations sont nécessaires au service que vous demandez : elles ne nécessitent pas votre consentement et ne quittent pas votre appareil.
          Vous pouvez les effacer dans Réglages, ou en vidant les données du site dans votre navigateur.
        </p>
      </>
    ),
  },
  {
    slug: "contact",
    title: "Nous contacter",
    summary: "Une question, un bug, une demande sur vos données.",
    body: (
      <>
        <p>Écrivez à l&apos;équipe : <Contact />.</p>
        <p>Pour un bug, indiquez l&apos;objet recherché, l&apos;heure et ce que vous avez vu. N&apos;envoyez pas de photo où apparaît une personne.</p>
      </>
    ),
  },
];

export const legalPage = (slug: string) => LEGAL_PAGES.find((p) => p.slug === slug);
