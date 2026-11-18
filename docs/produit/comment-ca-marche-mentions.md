# Snap N Cash : page « Comment ça marche » et mentions obligatoires

16/11/2026 · Tristan (CPO)

Ce document livre le texte complet de la page « Comment ça marche » et les mentions à placer sur chaque écran de Snap N Cash, prêts à coller dans v0. Il suit le dépôt de l'équipe (Specs.md point 10, CLAUDE.md règles 1, 4, 5, 8 et 9, CONTEXT.md « Cadre légal retenu »), relu le 16/11 au soir.

**Pour la présentation de demain :** montrer la section 1 (ce que l'utilisateur lira), puis la section 2 (où chaque mention apparaît), et finir sur la section 4 : les trois décisions à prendre en équipe avant de figer l'interface.

Les textes entre crochets \[ \] sont à compléter une fois la valeur connue (coefficient, décote, nom de l'éditeur).

## 1. Texte de la page « Comment ça marche »

Texte final, à coller tel quel. Les titres sont les intertitres de la page.

### Comment ça marche

Snap N Cash vous aide à fixer le prix d'un objet high-tech ou d'un jeu vidéo que vous voulez revendre. Vous prenez une photo, nous relevons des prix d'occasion sur une sélection de sites, et nous vous préparons une annonce. Les prix affichés sont indicatifs : ils ne garantissent ni une vente ni une offre de rachat.

### 1. Vous montrez l'objet

Prenez une photo de l'objet seul, répondez aux questions sur son état (boîte, accessoires), ou tapez simplement son nom. Si un visage apparaît sur la photo, nous la refusons et vous demandons d'en prendre une autre.

### 2. Une IA reconnaît l'objet

Un modèle d'intelligence artificielle identifie la marque, le modèle et l'état. Vérifiez le résultat : vous pouvez le corriger avant la recherche des prix.

### 3. Nous relevons les prix sur ces sites

Nous consultons uniquement les sites suivants, en même temps :

- **eBay**, par son interface officielle (API) : annonces de particuliers et de professionnels, et catégorie suggérée pour publier votre annonce sur eBay.
- **Easy Cash**, **Gamecash**, **Troc.com** et **Cash Converters** : des agents d'IA de H Company parcourent leurs pages comme le ferait une personne, et notent les prix des objets d'occasion en vente.

Cette comparaison n'est pas exhaustive. D'autres sites vendent des objets d'occasion et ne sont pas consultés. Un site qui ne répond pas en 90 secondes est affiché « indisponible », et l'estimation se fait sans lui. Les stocks d'occasion changent chaque jour : deux recherches peuvent donner des résultats différents.

**Vinted, Leboncoin, Cdiscount et TikTok Shop ne sont pas consultés.** Les boutons à leur nom ouvrent leur propre recherche dans votre navigateur, pour que vous compariez vous-même.

### 4. Nous calculons deux prix

Les deux prix sont calculés par notre programme, sans intelligence artificielle, et ne sont jamais mélangés.

- **Vendre seul (eBay)** : à partir des annonces eBay uniquement. Nous écartons les prix anormalement hauts ou bas, nous donnons la fourchette, puis un prix conseillé égal au prix médian moins \[10\] %, pour vendre plus vite.
- **Revendre en magasin** : à partir des prix de vente d'Easy Cash, Gamecash, Troc.com et Cash Converters. Un magasin rachète en général moins cher qu'il ne revend : nous appliquons donc un coefficient de \[40\] %. Ce prix est une estimation basse, et seule l'offre du magasin fait foi.

### 5. Comment les résultats sont classés

Dans chaque bloc, les sites s'affichent dans l'ordre où ils répondent, puis leurs offres sont classées du prix le plus bas au plus haut. Aucun site ne nous paie pour apparaître ou pour être mieux placé. Nous n'avons aucun lien commercial avec les sites consultés. Chaque prix est accompagné d'un lien vers l'offre d'origine.

### 6. Une IA rédige votre annonce

Un modèle d'intelligence artificielle rédige une annonce en quatre formats (Vinted, Leboncoin, eBay, texte générique). Relisez-la avant de la publier : elle peut contenir des erreurs. Vous la copiez et la publiez vous-même, nous ne publions rien à votre place.

### Vos données

- Pas de compte, pas de paiement.
- Votre photo sert à l'analyse puis est supprimée. Nous ne conservons ni photo, ni annonce relevée, ni nom de vendeur.
- L'historique de vos estimations reste dans votre navigateur. Vous pouvez l'effacer à tout moment depuis l'écran Historique.

### Qui fait Snap N Cash

Snap N Cash est un prototype réalisé par l'équipe 13 du hackathon Eugenia School × H Company (16 au 20 novembre 2026). Les agents de navigation sont fournis par H Company, les modèles d'IA sont hébergés sur Hugging Face. Contact : \[adresse de l'équipe\].

## 2. Mentions écran par écran

Chaque mention a un texte fixe et un emplacement. Le texte entre guillemets est à reprendre mot pour mot.

| Écran | Emplacement | Texte |
| --- | --- | --- |
| Accueil | Sous le bouton principal | « Prix indicatifs relevés sur eBay, Easy Cash, Gamecash, Troc.com et Cash Converters. Estimation et annonce générées par IA. » + lien « Comment ça marche » |
| Prise de photo | Au-dessus du viseur | « Photographiez l'objet seul, sans personne dans le cadre. » |
| Prise de photo | Message de refus | « Un visage apparaît sur la photo. Reprenez-la en ne montrant que l'objet. » |
| Prise de photo | Sous le bouton d'envoi | « Votre photo sert à l'analyse puis est supprimée. » |
| Identification | Sous le résultat | « Identifié par IA : vérifiez la marque et le modèle. » |
| Recherche en cours | Par site | « En cours », « Aucun résultat » ou « Indisponible » (au-delà de 90 s). Les étapes de l'agent en texte, jamais une capture du site. |
| Résultats | En tête | « Estimation générée par IA. Prix indicatifs, relevés le \[date et heure\] sur \[n\] sites. Comparaison non exhaustive. » + lien « Comment ça marche » |
| Résultats | Bloc « Vendre seul (eBay) » | Titre du bloc avec le mot eBay. Prix détaillés eBay uniquement, chacun avec son lien. |
| Résultats | Bloc « Revendre en magasin » | « Estimation basse : seule l'offre du magasin fait foi. » Prix détaillés par site, chacun avec son lien. |
| Résultats | Boutons Vinted, Leboncoin, Cdiscount, TikTok Shop | « Ces sites ne sont pas consultés par Snap N Cash. Le bouton ouvre leur recherche. » |
| Annonce | Au-dessus du texte | « Annonce rédigée par IA. Relisez-la avant de la publier. » |
| Historique | En tête | « Votre historique reste sur cet appareil. Rien n'est enregistré sur nos serveurs. » + bouton « Effacer l'historique » |
| Toutes les pages | Pied de page | « Prototype · Prix indicatifs · Généré par IA · Comment ça marche · Mentions légales » |

**Mentions légales (page courte, lien du pied de page) :** éditeur \[nom des membres ou de l'école\], contact \[adresse e-mail de l'équipe\], hébergeurs Vercel Inc. (interface) et Hugging Face (serveur), nature du site (prototype réalisé dans le cadre d'un hackathon, sans activité commerciale).

**Mots interdits partout :** « tous les sites », « le meilleur prix », « prix garanti », « valeur réelle ».

## 3. Pourquoi chaque mention

Les trois premières lignes viennent du dépôt (Specs.md point 10). Les autres sont des ajouts que je propose. Les textes de loi sont cités de mémoire et n'ont pas été relus sur Légifrance ce soir.

| Mention | Fondement | Source |
| --- | --- | --- |
| Liste des sites, comparaison non exhaustive, critère de classement, absence de rémunération | Code de la consommation, art. L111-7 (information loyale des plateformes et comparateurs), précisé par l'art. D111-7 et suivants | Specs.md, point 10 |
| « Estimation et annonce générées par IA » | AI Act (règlement UE 2024/1689), art. 50, transparence des contenus générés, applicable depuis le 2 août 2026 | Specs.md, point 10 |
| Prix indicatifs, jamais « tous les sites » | Éviter une pratique commerciale trompeuse (Code de la consommation, art. L121-2) | Specs.md point 10, CLAUDE.md règle 8 |
| Bloc eBay séparé, aucune donnée eBay dans l'IA de texte | Licence de l'API eBay | CLAUDE.md règle 4 |
| Aucune capture des sites sources, prix et lien seulement | Interdiction de reproduction dans les CGU des sites | CLAUDE.md règle 9 |
| Refus des photos avec visage, « objet seul » | Ne pas traiter l'image d'une personne (RGPD) | CLAUDE.md règle 6 |
| « Votre photo est supprimée », historique dans le navigateur | Information des personnes (RGPD, art. 13), même sans stockage | Ajout, appuyé sur CLAUDE.md règle 5 |
| Page Mentions légales | Loi pour la confiance dans l'économie numérique (LCEN), art. 6 : identifier l'éditeur et l'hébergeur | Ajout |
| « Vinted, Leboncoin… ne sont pas consultés » | Cohérence avec la liste des sites (L111-7) : éviter de laisser croire qu'ils sont comparés | Ajout, appuyé sur CLAUDE.md règle 1 |

## 4. À trancher en équipe et hypothèses à valider

Trois décisions bloquent le texte final : le critère de classement, l'éditeur légal et le droit de corriger l'identification. Le reste est à vérifier avant vendredi.

**Décisions à prendre demain :**

1. **Critère de classement.** Specs.md ne le fixe pas. Je propose : sites dans l'ordre de réponse, offres par prix croissant. Jude doit confirmer que le code fait exactement ça, sinon le texte devient faux.
2. **Éditeur légal.** Qui signe les mentions légales : les six membres, Eugenia School, ou un seul responsable ? Et quelle adresse de contact (pas celle du PDF du brief, qui ne doit pas être publiée).
3. **Correction de l'identification et bouton « Effacer l'historique ».** Le texte les promet, Specs.md ne les prévoit pas. On les ajoute à l'interface, ou je retire les deux phrases.

**Hypothèses juridiques à faire valider (mentors ou juriste de l'école) :**

- **L111-7 s'applique à un prototype gratuit.** Le dépôt le pose comme règle. La liste exacte des informations exigées (art. D111-7 et suivants, notamment le nombre de sites référencés et la date de mise à jour) est à relire sur Légifrance.
- **Portée de l'art. 50 de l'AI Act.** L'obligation vise surtout le fournisseur (marquage lisible par machine des textes générés). La mention visible couvre l'esprit du texte, mais un marquage technique de l'annonce n'est pas prévu. À confirmer.
- **Le prix « en magasin » n'est pas généré par IA.** C'est un calcul de notre code. La mention « estimation générée par IA » reste vraie car l'identification de l'objet l'est. Formulation à garder telle que dans les Specs.
- **Détection de visage sans donnée biométrique.** Détecter un visage pour refuser la photo n'identifie personne. Je suppose que ce n'est pas un traitement biométrique au sens du RGPD (art. 9). À confirmer, et le modèle doit tourner sans rien garder.
- **Historique dans le navigateur sans bandeau cookies.** Un stockage local demandé par l'utilisateur et nécessaire au service est en principe exempté de consentement (loi Informatique et Libertés, art. 82). Valable seulement si aucun outil de mesure d'audience n'est ajouté.
- **Noms des sites sans logos.** Citer Easy Cash, Gamecash, Troc.com, Cash Converters et eBay en texte est une référence nécessaire. Leurs logos ne sont pas utilisés.
- **Licence eBay.** Elle peut imposer une mention d'attribution ou une fréquence de mise à jour. Lecture complète prévue par Jude mercredi 18/11 (action 8 des Specs).
- **Valeurs entre crochets.** Décote eBay \[10 %\] et coefficient magasin \[40 %\] sont des hypothèses des Specs, à remplacer par les valeurs mesurées par Kevin jeudi 19/11.

## 5. Checklist d'intégration

À cocher dans v0, puis à repasser lors du garde-fou de conformité avant vendredi 11h.

- [ ] La page « Comment ça marche » est accessible depuis l'accueil, les résultats et le pied de page.
- [ ] Elle nomme les 5 sources : eBay, Easy Cash, Gamecash, Troc.com, Cash Converters.
- [ ] Si un site sort de la liste (blocage, Cloudflare), il est retiré de la page le jour même.
- [ ] « Comparaison non exhaustive » figure sur la page et en tête des résultats.
- [ ] Le critère de classement affiché correspond au code.
- [ ] « Généré par IA » est visible sur l'identification, les résultats et l'annonce, sans dérouler la page.
- [ ] Les blocs « Vendre seul (eBay) » et « Revendre en magasin » sont visuellement séparés, sans total commun.
- [ ] Aucune capture d'un site source n'apparaît, ni dans les résultats ni dans l'affichage des agents.
- [ ] Le texte « tous les sites » n'apparaît nulle part (recherche dans le code et dans les slides).
- [ ] Le refus de photo avec visage fonctionne et affiche le bon message.
- [ ] La page Mentions légales est remplie (éditeur, contact, hébergeurs).
- [ ] Aucun outil de mesure d'audience ni cookie tiers n'est ajouté.

**Testé :** rien. Ce document est un texte, il n'a pas encore été intégré ni relu par un juriste.
