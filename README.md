<p align="center"><img src="frontend/app/icon.png" alt="Logo Snap N Cash" width="120"></p>

<h1 align="center">Snap N Cash</h1>

<p align="center"><strong>Ce qui dort chez vous a un prix.</strong> Une photo, le bon prix, l'annonce prête.</p>

<p align="center">Team 13 · Hackathon Eugenia School × H Company × Vercel × Hugging Face · 16 au 20 novembre 2026</p>

<p align="center"><strong>Essayer : <a href="https://snapncash.vercel.app">snapncash.vercel.app</a></strong></p>

<p align="center"><strong>Vidéo de démonstration (5 min) : <a href="https://www.loom.com/share/4b8604d3a9c24aed80c212bbae01643f">loom.com</a></strong></p>

---

## Tester le prototype
1. Ouvrez **https://snapncash.vercel.app**, sur ordinateur ou sur téléphone.
2. Touchez **Estimer**, puis prenez en photo un objet high-tech ou un jeu vidéo (téléphone, console, tablette, ordinateur portable, jeu). Sans objet sous la main, tapez son nom, par exemple « Apple iPhone 13 128 Go ».
3. Regardez les agents H Company travailler : leurs écrans s'affichent en direct sous la barre de progression, une session par boutique. Une estimation prend environ 1 à 2 min : toutes les boutiques sont visitées en même temps.
4. Lisez le verdict : vendre soi-même (prix des annonces eBay en cours) ou revendre en magasin (rachat estimé à partir des prix relevés par les agents en boutique), avec le gain en euros.
5. Ouvrez l'annonce : titre, description, caractéristiques et photos studio, prêts à publier sur eBay, Vinted ou Leboncoin.

Le mode démo (écrans des agents) est actif par défaut. Il se coupe dans **Réglages**. Une adresse IP a droit à un nombre limité de recherches par heure : en cas de refus, réessayez un peu plus tard.

Serveur : https://judebkn95-snapncash.hf.space/api/health répond `ok`.

## Le problème
86 % des Français gardent des objets inutilisés, 320 € par foyer en moyenne, mais 17 % seulement les ont déjà revendus. Ils citent le manque de temps (29 %), des démarches jugées complexes (20 %) et la peur de se tromper de prix (16 %) ([OpinionWay pour Leboncoin](https://www.cbnews.fr/etudes/320-euros-dorment-les-placards-francais), en ligne du 24 au 26 septembre 2025, 1 054 personnes ; les 320 € sont une valeur estimée par les répondants). Pour le high-tech, 46 millions de téléphones dorment dans les tiroirs, dont 59 % de smartphones ([Harris Interactive et Crédoc pour ecosystem et Ecologic](https://www.ecosystem.eco/document/155), juin 2023, 5 614 ménages).

## La solution
L'utilisateur photographie son objet high-tech ou son jeu vidéo. Un modèle Hugging Face le reconnaît. **Des agents H Company visitent en direct jusqu'à cinq boutiques d'occasion françaises** qui n'ont pas d'API (3 ou 4 par objet, selon sa catégorie), et relèvent les prix. L'app répond en moins de deux minutes :
- **où vendre** : vendre soi-même ou en magasin, avec le gain en euros ;
- **à quel prix** : fourchette, prix conseillé, curseur « vente rapide, prix juste, ambitieux » ;
- **l'annonce prête** aux formats Vinted, Leboncoin, eBay et texte libre, plus des **photos studio** (objet détouré sur fond clair, objet non modifié).

**Pourquoi un agent et pas un script :** aucune ligne de code n'est propre à un site. Une boutique s'ajoute par une entrée de configuration ; Certideal et Swappie ont été ajoutés ainsi le 17/11 et ont marché au premier essai.

## Parcours
1. **Découverte** : trois écrans au premier lancement.
2. **Trois photos guidées** : l'objet de face, le dos ou l'étiquette, un détail. Une photo avec un visage est refusée.
3. **Identification** : marque, modèle, capacité, catégorie, en 1 à 3 s.
4. **Les agents au travail** : une barre de progression et, en mode démo (actif par défaut, réglable), les écrans des agents côte à côte.
5. **Verdict « Où vendre ? »**, échelle des prix, curseur.
6. **Annonce** en 4 formats et **photos studio**, puis publication par l'utilisateur.
7. **Mon grenier** : objets estimés, statut, gains, gardés dans le navigateur.
8. **Espace revendeurs** (`/pro`) : annonces des boutiques classées par marge de revente.

## Architecture

```
Téléphone ou ordinateur                Notre serveur                         Services
┌──────────────────────┐   HTTPS   ┌──────────────────────────┐   ┌──────────────────────────────────┐
│ Next.js 15 (Vercel)  │ ────────▶ │ FastAPI (Space HF)        │──▶│ Hugging Face : gemma-4-31B-it     │
│ Mon grenier dans le  │ ◀──────── │ /api/identify  /api/search│   │  (identification, annonce)        │
│ navigateur           │  site par │ /api/ebay  /api/listing   │──▶│ H Company Agent API               │
└──────────────────────┘   site    │ /api/studio  /api/shot    │   │  h/web-surfer-flash, 5 boutiques  │
                                   │ Tri par modèle, médianes, │──▶│ eBay API Browse (bloc séparé)     │
                                   │ contrôle des visages      │──▶│ Bria RMBG-2.0 via fal.ai (studio) │
                                   └──────────────────────────┘   └──────────────────────────────────┘
```

| Brique | Choix | Mesuré |
|---|---|---|
| Interface | Next.js 15, déployée sur Vercel | en ligne |
| Serveur | FastAPI, dans un Space Hugging Face (Docker, CPU upgrade) | en ligne |
| Agents | H Company Agent API, `h/web-surfer-flash`, une session par site, jusqu'à 10 en parallèle (limite de notre organisation H, relevée par H Company le 19/11) | 24 à 90 s par site en test, 82 à 97 s en ligne le 19/11 |
| Identification | `google/gemma-4-31B-it` via le routeur Hugging Face, jusqu'à 3 photos | 1 à 3 s |
| Annonce | `google/gemma-4-31B-it` | 1 à 4 s |
| Contrôle des visages | `opencv/face_detection_yunet`, sur notre serveur | 10 à 300 ms |
| Studio photo | `briaai/RMBG-2.0` via fal.ai ; secours `ZhengPeng7/BiRefNet_lite` en local | 1 à 2 s en local, 20 s en ligne (19/11) |
| Prix entre particuliers | eBay API Browse (annonces en cours), dans un bloc séparé | 1 à 2 s, 61 annonces pour un iPhone 13 |

Boutiques consultées par les agents : Easy Cash, Gamecash, Cash Converters, Certideal, Swappie (iPhone et iPad seulement). Troc.com est en pause depuis le 19/11 : 0 prix sur 10 objets mesurés. Vinted ([CGU, article 6](https://www.vinted.fr/terms-and-conditions) : bots et programmes de scraping interdits) et Leboncoin ([robots.txt](https://www.leboncoin.fr/robots.txt) : « It's forbidden to use search robots or other automatic methods ») interdisent l'accès automatisé : un bouton ouvre leur recherche chez l'utilisateur.

## Retours sur l'Agent API de H Company
Ce que l'Agent API nous a permis de faire, ce qui nous a freinés (preuves et mesures à l'appui) et ce que nous demanderions à H : **[docs/retours-agent-api-h.md](docs/retours-agent-api-h.md)**.
En bref : un agent pour cinq boutiques sans code propre à chacune, 33 sessions sur 33 abouties le 19/11 ; nos demandes portent sur la vidéo en direct, les offres partielles d'une session coupée et une grille de prix publique.

## Règles que le produit respecte
- **Aucun agent sur un site qui l'interdit**, aucun contournement d'anti-robot (Fnac, qui bloque l'agent, est sorti de la liste).
- **robots.txt respecté** : Easy Cash et Certideal par leurs catégories, Swappie sans filtres.
- **Rien n'est conservé côté serveur** : ni photo, ni annonce relevée, ni pseudonyme de vendeur.
- **Les données eBay restent dans leur bloc** et ne passent dans aucun modèle de texte.
- **Prix indicatifs**, mention « générée par IA », sites consultés listés dans « Comment ça marche ».
- **Captures des agents** montrées en direct pendant la recherche, jamais conservées (relais sans enregistrement, jeton valable 10 min).

## Lancer en local
Prérequis : Python 3.12 ou plus, Node 20 ou plus, et les clés dans un fichier `.env` à la racine (modèle : `.env.example`). Le fichier `.env` n'est jamais versionné.

```bash
# Serveur
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn backend.main:app --reload --port 8000

# Interface (autre terminal)
cd frontend
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev                         # http://localhost:3000
```

Pour voir les écrans des agents en local, ajouter `DEMO_SHOTS=1` dans le `.env` (le mode démo est actif par défaut dans l'interface). Pour le brouillon eBay par agent sur ce Mac, ajouter aussi `EBAY_DRAFT_LOCAL=1` (voir plus bas). Relancer le serveur après chaque modification du `.env`.

Une recherche lance de vrais agents H : environ 80 s et des crédits par site.

## Tests
```bash
.venv/bin/python tests/test_matching.py   # tri des annonces par modèle et par état : 92 cas
.venv/bin/python tests/test_ebay.py       # bloc eBay sur une réponse simulée : 19 vérifications
.venv/bin/python tests/test_ebay_categorie.py # catégorie eBay suggérée, 15 réponses réelles de l'API : 49 vérifications
.venv/bin/python tests/test_garde_fous.py # arrêt des agents, limites d'usage, coefficient de rachat par catégorie, offres gardées après délai : 23 vérifications
.venv/bin/python tests/test_brouillon_ebay.py  # brouillon eBay par agent, sans réseau : 25 vérifications
.venv/bin/python tests/test_mesure_objets.py   # script de mesure (eBay, objets en parallèle, pic de sessions) : 9 vérifications
.venv/bin/python -m agents.test_agents --site gamecash --product "Nintendo Switch" --category console   # agent réel
```
Ces scripts tournent à chaque push (onglet Actions), sauf `test_ebay_categorie.py`.

## Mesurer
```bash
# Remplir mesures/objets_a_mesurer.csv (objet, catégorie, état, prix réellement vendu sur eBay, photos facultatives)
.venv/bin/python -m agents.mesure_objets               # un objet après l'autre
.venv/bin/python -m agents.mesure_objets --parallele 2  # deux objets à la fois : 10 sessions H ensemble avec deux smartphones
```
Sortie : taux de réussite par boutique (au moins 3 prix), durée d'une estimation, écart entre le prix conseillé et le prix vendu, identification correcte, cas d'échec, face aux objectifs des Specs. Les sessions d'agent sont aussi dans [`mesures/agent_runs.csv`](mesures/agent_runs.csv), les décisions et cas d'échec dans [`JOURNAL.md`](JOURNAL.md).

**Mesure du 19/11 (10 objets, 10 agents simultanés)**, fichiers [`mesures/mesure_objets_2026-11-19_10h30.csv`](mesures/mesure_objets_2026-11-19_10h30.csv) et [`mesures/mesure_sites_2026-11-19_10h30.csv`](mesures/mesure_sites_2026-11-19_10h30.csv) **:**
- **Mesuré :** 33 sessions d'agent sur 33 abouties (prix ou absence de stock vérifiée), 21 avec au moins un prix ; prix eBay pour 10 objets sur 10 ; prix magasin complet (au moins 3 prix) pour 6 objets sur 10 ; durée médiane d'une estimation 91 s (toutes sous 100 s) ; 506 000 jetons par estimation en moyenne.
- **Pas encore mesuré :** l'identification par photo sur le jeu de 10 objets (la mesure est partie du nom de l'objet), l'écart entre le prix conseillé et le prix réellement vendu sur eBay, la part des prix vendus comprise dans la fourchette, et le temps gagné avec 3 testeurs. Les colonnes existent dans le fichier de mesure, elles sont vides : aucun chiffre n'est avancé pour ces critères.

## Brouillon eBay par un agent H (démo sur le Mac)
Un agent H Company pilote **le Chrome de cet ordinateur**, où tu t'es connecté toi-même à eBay : ni mot de passe ni cookie ne quittent l'ordinateur. Il ouvre l'éditeur prérempli, dépose les photos (par un outil à nous, car ce mode n'a pas d'envoi de fichier), colle la description, règle le prix et **enregistre un brouillon**. Il ne publie jamais : tu cliques toi-même sur « Mettre en vente ». Réservé à la démo : il agit sur un seul compte eBay, la route est fermée sans clé de démo et absente du Space.

**Pourquoi pas en ligne :** l'agent doit agir dans un navigateur où le vendeur est connecté à eBay, et nous refusons de faire passer ses identifiants par notre serveur. Depuis le 20 février 2026, l'[accord d'utilisation d'eBay](https://www.ebay.com/help/policies/member-behaviour-policies/user-agreement?id=4259) interdit aussi, sans son autorisation préalable, les « LLM-driven bots » et les agents « buy-for-me » ([résumé du changement](https://www.valueaddedresource.net/ebay-bans-ai-agents-updates-arbitration-user-agreement-feb-2026/)). Pour ouvrir cette fonction à tous, nous passerons par le programme partenaire d'eBay et son [API de gestion des annonces](https://developer.ebay.com/api-docs/sell/inventory/overview.html).
1. `.venv/bin/pip install -r requirements-demo.txt` (une fois).
2. `scripts/ebay_chrome.sh` : ouvre un Chrome dédié ; **connecte-toi à eBay dans cette fenêtre** et laisse-la ouverte.
3. Lancer le serveur avec `EBAY_DRAFT_LOCAL=1` et `DEMO_KEY=<ta clé>`, ouvrir l'interface une fois avec `?cle=<ta clé>`.
4. Après l'estimation, onglet eBay du bloc « Votre annonce » : bouton « Laisser un agent H préparer le brouillon eBay ».
Tests sans réseau : `.venv/bin/python tests/test_brouillon_ebay.py`.

## Mettre en ligne
Le serveur va sur un Space Hugging Face, l'interface sur Vercel. L'image du serveur est testée en local (démarre, lit les clés, répond).

**1. Serveur (Space Hugging Face)**
1. Créer un jeton **avec droit d'écriture** sur huggingface.co/settings/tokens (celui du `.env` n'a que l'inférence).
2. Créer le Space : New Space, SDK **Docker**, modèle « Blank », visibilité **Public** (l'interface Vercel doit pouvoir l'appeler). Le 19/11, la création d'un Space Docker sur « CPU basic » gratuit a renvoyé une erreur 402 (compte PRO exigé, les Spaces Docker figurent dans l'offre PRO sur la [page des tarifs](https://huggingface.co/pricing)) : nous utilisons « CPU upgrade » ([0,03 $/h](https://huggingface.co/pricing)), payé par les crédits du hackathon, avec une mise en veille après 48 h d'inactivité.
3. Envoyer le code : `scripts/deploy_space.sh <compte>/<nom-du-space>` (Git demande l'identifiant, puis le jeton d'écriture comme mot de passe).
4. Dans Settings du Space, **Secrets** : `HAI_API_KEY`, `HF_TOKEN` (le jeton d'inférence), `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `DEMO_KEY`.
   **Variables** : `ALLOWED_ORIGINS` (adresse Vercel, voir 2), `DEMO_SHOTS=1`, `TRUSTED_PROXIES=1`, `SEARCH_PER_HOUR=200` (une salle partage une adresse IP).
5. Ouvrir `https://<compte>-<nom-du-space>.hf.space/api/health` : tout doit être à `true`. Un Space inactif s'endort : l'ouvrir 5 minutes avant la démo.

**2. Interface (Vercel)**
Le plan gratuit Hobby est réservé à un usage personnel et non commercial ([règles de Vercel](https://vercel.com/docs/limits/fair-use-guidelines)) : un lancement commercial passe par Vercel Pro (20 $ par mois).
Le projet Vercel n'est pas relié à GitHub : une fusion dans `main` ne change pas le site en ligne. Chaque mise en ligne se fait depuis `frontend/` avec `vercel deploy --prod`.
1. `cd frontend && vercel login`, puis `vercel` (dossier racine : `frontend`).
2. Variable d'environnement `NEXT_PUBLIC_API_URL` = adresse du Space (`https://<compte>-<nom-du-space>.hf.space`), puis `vercel --prod`.
3. Reporter l'adresse Vercel dans `ALLOWED_ORIGINS` du Space (le Space redémarre).

**3. Démo**
Ouvrir l'interface une fois avec `?cle=<DEMO_KEY>` pour lever la limite par adresse IP. Le mode démo est actif par défaut. Une clé H réservée à la démo évite de partager les sessions avec les mesures.

## Organisation du dépôt
| Dossier ou fichier | Contenu |
|---|---|
| `frontend/` | Interface Next.js |
| `backend/` | Serveur FastAPI : identification, tri, prix, eBay, annonce, studio |
| `agents/` | Agents H Company : consigne, configuration des boutiques, script de test |
| `tests/` | 7 fichiers de tests sans réseau : tri par modèle, bloc et catégorie eBay, garde-fous, brouillon eBay, pages de départ des agents, script de mesure |
| `mesures/` | Journal chiffré des sessions d'agent et mesures sur 10 objets (19/11) |
| `docs/produit/` | Parcours d'écrans, mentions, espace revendeurs |
| `docs/business-model/` | Modèle économique, coût de run et projections sur 3 ans (document et tableur) |
| `docs/sondage/` | Sondage maison et réponses anonymes |
| `docs/retours-agent-api-h.md` | Nos retours sur l'Agent API de H Company |
| `docs/pitch/` | Contenu du pitch deck |
| `docs/demo/` | Simulation vidéo pour le pitch (imitation, marquée comme telle) |
| `Specs.md`, `CONTEXT.md`, `JOURNAL.md` | Ce qu'on construit, le cadre, les décisions datées |

## État au 19/11
**En ligne et vérifié le 19/11 au soir :** interface sur Vercel, serveur sur le Space. Recherche « Nintendo Switch » : 7 prix sur 3 boutiques et le bloc eBay, en 98 s. Identification par photo (3 photos d'un téléphone) : « Apple iPhone 13 », confiance 0,9. Annonce rédigée par IA dans les 4 formats. Photo studio détourée en 20 s. Écrans des agents relayés en direct, y compris dans l'espace revendeurs (`/pro`).
**Testé en local seulement :** espace revendeurs de bout en bout (classement par marge, panier), brouillon eBay par agent sur le Mac de la démo.
**Vidéo de démonstration (5 min) :** [https://www.loom.com/share/4b8604d3a9c24aed80c212bbae01643f](https://www.loom.com/share/4b8604d3a9c24aed80c212bbae01643f), enregistrée en local en mode démo : agents au travail, verdict, annonce, brouillon eBay par un agent, espace revendeurs.

### Historique : au 18/11
**Testé :** parcours complet sur ordinateur et sur téléphone, 3 photos guidées (réduites à 1600 px avant l'envoi), agents sur les 6 boutiques, studio photo, nouvelle interface (clair et sombre), espace revendeurs, arrêt des agents quand l'utilisateur quitte une recherche (en réel), limites d'usage, coefficient de rachat mesuré par catégorie sur 30 objets ([docs/calibrage-rachat.md](docs/calibrage-rachat.md)), **API eBay en réel** (annonces « Vendre seul », catégorie suggérée sur 15 produits), classement des offres par état (Gamecash n'est plus à 0 prix), lien « Publier sur eBay » qui ouvre l'éditeur avec titre, catégorie et état remplis (vérifié sur un compte connecté).
**Pas encore :** mesure sur 10 objets, bouton « Partager photos et annonce » sur un vrai iPhone (testé avec un partage simulé ; il exige du HTTPS), publication en 1 clic sur eBay (maquette et plan dans [docs/produit/publication-ebay.md](docs/produit/publication-ebay.md), hors Specs actuelles). Le prix, la description et les photos ne passent pas par le lien eBay. Suivi dans les [issues](https://github.com/Lemtiel/Hackacton_H_Compacny/issues).

## Pour aller plus loin
Ce que nous aurions aimé faire avec plus de temps, ou qui demande l'accord d'une plateforme.

### Un partenariat avec Vinted et Leboncoin
Leurs règles interdisent les robots ([CGU de Vinted, article 6](https://www.vinted.fr/terms-and-conditions), [robots.txt de Leboncoin](https://www.leboncoin.fr/robots.txt)) : nous n'y envoyons aucun agent. Avec leur accord (une API, ou des agents identifiés et limités en rythme), le partenariat profite aux trois parties.
- **Pour la plateforme :** de nouvelles annonces d'objets qui dormaient dans les tiroirs (83 % des Français n'ont jamais revendu leurs objets inutilisés, [OpinionWay pour Leboncoin](https://www.cbnews.fr/etudes/320-euros-dorment-les-placards-francais), 2025), des annonces complètes (photos studio, caractéristiques, prix cohérent avec le marché), donc moins d'annonces bâclées, moins de litiges et plus de ventes sur lesquelles elle touche ses frais.
- **Pour le vendeur :** le prix entre particuliers mesuré sur la plateforme où il vend, et une publication en un clic au lieu de recopier l'annonce.
- **Pour Snap N Cash :** des prix de vente réels pour mesurer la précision de nos estimations, et un revenu par annonce publiée, puis une licence (voir le [modèle économique](docs/business-model/business-model-snap-n-cash.md)).

### Le programme partenaire d'eBay
Publier en un clic par l'[API de gestion des annonces d'eBay](https://developer.ebay.com/api-docs/sell/inventory/overview.html), à la place de notre agent qui ne tourne que sur l'ordinateur du vendeur. L'accord d'utilisation d'eBay serait respecté et la fonction s'ouvrirait à tous les utilisateurs.

### Une extension de navigateur
Une extension installée par le vendeur préparerait le brouillon dans son propre navigateur, là où il est déjà connecté : ses identifiants ne passeraient jamais par notre serveur. Elle suppose l'accord de chaque plateforme, comme le partenariat.

### Choisir sa vitesse de vente
Le curseur « vente rapide, prix juste, ambitieux » existe déjà sur l'écran de prix. L'étape suivante : demander dès le départ « vendre vite » ou « au meilleur prix », appliquer ce choix au prix de l'annonce et du brouillon eBay, et afficher un délai de vente estimé une fois les ventes réelles connues.

### Mesurer la précision des prix
Comparer le prix conseillé au prix réellement obtenu, sur des ventes conclues ([API Marketplace Insights d'eBay](https://developer.ebay.com/api-docs/buy/marketplace-insights/static/overview.html), à accès restreint, ou données d'une plateforme partenaire). Le critère des Specs (écart médian de 15 % au plus) n'est pas encore mesuré.

### Une marge revendeur plus réaliste
L'espace revendeurs calcule la marge sur le prix médian des boutiques. Un revendeur revend plutôt entre particuliers : prendre le prix eBay comme référence de revente donnerait une marge plus prudente.

### Plus de boutiques, puis d'autres pays
Une boutique s'ajoute par une ligne de configuration, sans code propre. Les mêmes agents peuvent couvrir d'autres catégories et d'autres pays.

## Sources
Chaque chiffre du README vient d'une source publique ou d'une mesure de l'équipe, versionnée dans ce dépôt.

**Sources publiques** (vérifiées le 19/11/2026) :
| Affirmation | Source |
|---|---|
| 86 % gardent des objets inutilisés, 320 € par foyer (estimation des répondants), 17 % ont déjà revendu, freins : temps 29 %, démarches 20 %, prix 16 % | [Sondage OpinionWay pour Leboncoin](https://www.cbnews.fr/etudes/320-euros-dorment-les-placards-francais), en ligne du 24 au 26 septembre 2025, 1 054 personnes de 18 ans et plus |
| 46 millions de téléphones dans les tiroirs (59 % de smartphones, dont 3 sur 4 encore en état de marche) | [Infographie ecosystem](https://www.ecosystem.eco/document/155) : étude Harris Interactive et Crédoc pour ecosystem et Ecologic, juin 2023, 5 614 ménages |
| Vinted interdit les bots et le scraping | [Conditions d'utilisation de Vinted](https://www.vinted.fr/terms-and-conditions), article 6 |
| Leboncoin interdit les robots et méthodes automatiques | [robots.txt de Leboncoin](https://www.leboncoin.fr/robots.txt) |
| eBay interdit les agents IA sans autorisation depuis le 20 février 2026 | [Accord d'utilisation d'eBay](https://www.ebay.com/help/policies/member-behaviour-policies/user-agreement?id=4259) ; [résumé du changement](https://www.valueaddedresource.net/ebay-bans-ai-agents-updates-arbitration-user-agreement-feb-2026/) |
| Space « CPU upgrade » à 0,03 $/h, Spaces Docker dans l'offre PRO | [Tarifs Hugging Face](https://huggingface.co/pricing) |
| Vercel Hobby réservé à un usage non commercial | [Règles d'usage de Vercel](https://vercel.com/docs/limits/fair-use-guidelines) |
| Ventes conclues eBay et publication par API | [Marketplace Insights](https://developer.ebay.com/api-docs/buy/marketplace-insights/static/overview.html), [API de gestion des annonces](https://developer.ebay.com/api-docs/sell/inventory/overview.html) |

**Mesures de l'équipe** (dans ce dépôt) :
| Affirmation | Fichier |
|---|---|
| 33 sessions sur 33 abouties, 91 s en médiane, prix eBay 10 sur 10, prix magasin complet 6 sur 10, 506 000 jetons | [`mesures/mesure_objets_2026-11-19_10h30.csv`](mesures/mesure_objets_2026-11-19_10h30.csv), [`mesures/mesure_sites_2026-11-19_10h30.csv`](mesures/mesure_sites_2026-11-19_10h30.csv) |
| Durées et jetons par session d'agent | [`mesures/agent_runs.csv`](mesures/agent_runs.csv) |
| Coefficient de rachat (0,60 pour les smartphones) | [`docs/calibrage-rachat.md`](docs/calibrage-rachat.md) |
| Coût par estimation (0,26 € à l'usage, 0,02 € au forfait) et projections | [`docs/business-model/`](docs/business-model/business-model-snap-n-cash.md) |
| Fnac bloque l'agent, Troc.com sans prix, PS5 corrigée | [`JOURNAL.md`](JOURNAL.md) |
| Tests en ligne du 19/11 au soir (recherche, photo, annonce, studio) | Section « État au 19/11 » ci-dessus |

## Équipe
| | Rôle |
|---|---|
| Stephen Morlot | CEO |
| Jude Buyikana | CTO, pilote du projet |
| Josias Tatou | CAO, orchestration des agents et espace revendeurs |
| Sebastian Espinosa | CAIO, modèles et calibrage |
| Kevin Assombi | CDO, données et mesures |
| Tristan David | CPO, produit et modèle économique |

Prix indicatifs, comparaison non exhaustive. Estimation et annonce générées par IA. Prototype de hackathon, non commercialisé.
