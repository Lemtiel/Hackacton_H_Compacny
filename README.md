<p align="center"><img src="frontend/app/icon.png" alt="Logo Snap N Cash" width="120"></p>

<h1 align="center">Snap N Cash</h1>

<p align="center"><strong>Ce qui dort chez vous a un prix.</strong> Une photo, le bon prix, l'annonce prête.</p>

<p align="center">Team 13 · Hackathon Eugenia School × H Company × Vercel × Hugging Face · 16 au 20 novembre 2026</p>

---

## Le problème
86 % des Français gardent des objets inutilisés, 320 € par foyer en moyenne, mais 17 % seulement les ont déjà revendus. Ils citent le manque de temps (29 %), des démarches jugées complexes (20 %) et la peur de se tromper de prix (16 %) (OpinionWay pour Leboncoin, septembre 2025). Pour le high-tech, 46 millions de téléphones dorment dans les tiroirs (Harris Interactive et Crédoc pour Ecologic, 2023).

## La solution
L'utilisateur photographie son objet high-tech ou son jeu vidéo. Un modèle Hugging Face le reconnaît. **Des agents H Company visitent en direct six boutiques d'occasion françaises** qui n'ont pas d'API, et relèvent les prix. L'app répond en moins de deux minutes :
- **où vendre** : vendre soi-même ou en magasin, avec le gain en euros ;
- **à quel prix** : fourchette, prix conseillé, curseur « vente rapide, prix juste, ambitieux » ;
- **l'annonce prête** aux formats Vinted, Leboncoin, eBay et texte libre, plus des **photos studio** (objet détouré sur fond clair, objet non modifié).

**Pourquoi un agent et pas un script :** aucune ligne de code n'est propre à un site. Une boutique s'ajoute par une entrée de configuration ; Certideal et Swappie ont été ajoutés ainsi le 17/11 et ont marché au premier essai.

## Parcours
1. **Découverte** : trois écrans au premier lancement.
2. **Trois photos guidées** : l'objet de face, le dos ou l'étiquette, un détail. Une photo avec un visage est refusée.
3. **Identification** : marque, modèle, capacité, catégorie, en 1 à 3 s.
4. **Les agents au travail** : une barre de progression ; en mode démo (`?demo=1`), les écrans des agents côte à côte.
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
└──────────────────────┘   site    │ /api/studio  /api/shot    │   │  h/web-surfer-flash, 6 boutiques  │
                                   │ Tri par modèle, médianes, │──▶│ eBay API Browse (bloc séparé)     │
                                   │ contrôle des visages      │──▶│ Bria RMBG-2.0 via fal.ai (studio) │
                                   └──────────────────────────┘   └──────────────────────────────────┘
```

| Brique | Choix | Mesuré |
|---|---|---|
| Interface | Next.js 15, déployée sur Vercel | — |
| Serveur | FastAPI, dans un Space Hugging Face | — |
| Agents | H Company Agent API, `h/web-surfer-flash`, une session par site, 3 en parallèle | 24 à 81 s par site |
| Identification | `google/gemma-4-31B-it` via le routeur Hugging Face, jusqu'à 3 photos | 1 à 3 s |
| Annonce | `google/gemma-4-31B-it` | 1 à 4 s |
| Contrôle des visages | `opencv/face_detection_yunet`, sur notre serveur | 10 à 300 ms |
| Studio photo | `briaai/RMBG-2.0` via fal.ai ; secours `ZhengPeng7/BiRefNet_lite` en local | 1 à 2 s |
| Prix entre particuliers | eBay API Browse, dans un bloc séparé | clés en attente |

Boutiques consultées par les agents : Easy Cash, Gamecash, Troc.com, Cash Converters, Certideal, Swappie. Vinted et Leboncoin interdisent l'accès automatisé : un bouton ouvre leur recherche chez l'utilisateur.

## Règles que le produit respecte
- **Aucun agent sur un site qui l'interdit**, aucun contournement d'anti-robot (Fnac, qui bloque l'agent, est sorti de la liste).
- **robots.txt respecté** : Easy Cash et Certideal par leurs catégories, Swappie sans filtres.
- **Rien n'est conservé côté serveur** : ni photo, ni annonce relevée, ni pseudonyme de vendeur.
- **Les données eBay restent dans leur bloc** et ne passent dans aucun modèle de texte.
- **Prix indicatifs**, mention « générée par IA », sites consultés listés dans « Comment ça marche ».

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
npm run dev                         # http://localhost:3000, mode démo : http://localhost:3000/?demo=1
```

Une recherche lance de vrais agents H : environ 80 s et des crédits par site.

## Tests
```bash
.venv/bin/python tests/test_matching.py   # tri des annonces par modèle et par état : 92 cas
.venv/bin/python tests/test_ebay.py       # bloc eBay sur une réponse simulée : 19 vérifications
.venv/bin/python tests/test_ebay_categorie.py # catégorie eBay suggérée, 15 réponses réelles de l'API : 49 vérifications
.venv/bin/python tests/test_garde_fous.py # arrêt des agents, limites d'usage, coefficient de rachat par catégorie, offres gardées après délai : 23 vérifications
.venv/bin/python -m agents.test_agents --site gamecash --product "Nintendo Switch" --category console   # agent réel
```
Ces quatre scripts tournent à chaque push (onglet Actions).

## Mesurer
```bash
# Remplir mesures/objets_a_mesurer.csv (objet, catégorie, état, prix réellement vendu sur eBay, photos facultatives)
.venv/bin/python -m agents.mesure_objets
```
Sortie : taux de réussite par boutique (au moins 3 prix), durée d'une estimation, écart entre le prix conseillé et le prix vendu, identification correcte, cas d'échec, face aux objectifs des Specs. Les sessions d'agent sont aussi dans [`mesures/agent_runs.csv`](mesures/agent_runs.csv), les décisions et cas d'échec dans [`JOURNAL.md`](JOURNAL.md).

## Brouillon eBay par un agent H (démo sur le Mac)
Un agent H Company pilote **le Chrome de cet ordinateur**, où tu t'es connecté toi-même à eBay : ni mot de passe ni cookie ne quittent l'ordinateur. Il ouvre l'éditeur prérempli, dépose les photos (par un outil à nous, car ce mode n'a pas d'envoi de fichier), colle la description, règle le prix et **enregistre un brouillon**. Il ne publie jamais : tu cliques toi-même sur « Mettre en vente ». Réservé à la démo : il agit sur un seul compte eBay, la route est fermée sans clé de démo et absente du Space.
1. `.venv/bin/pip install -r requirements-demo.txt` (une fois).
2. `scripts/ebay_chrome.sh` : ouvre un Chrome dédié ; **connecte-toi à eBay dans cette fenêtre** et laisse-la ouverte.
3. Lancer le serveur avec `EBAY_DRAFT_LOCAL=1` et `DEMO_KEY=<ta clé>`, ouvrir l'interface une fois avec `?cle=<ta clé>`.
4. Après l'estimation, onglet eBay du bloc « Votre annonce » : bouton « Laisser un agent H préparer le brouillon eBay ».
Tests sans réseau : `.venv/bin/python tests/test_brouillon_ebay.py`.

## Mettre en ligne
Le serveur va sur un Space Hugging Face, l'interface sur Vercel. L'image du serveur est testée en local (démarre, lit les clés, répond).

**1. Serveur (Space Hugging Face)**
1. Créer un jeton **avec droit d'écriture** sur huggingface.co/settings/tokens (celui du `.env` n'a que l'inférence).
2. Créer le Space : New Space, SDK **Docker**, modèle « Blank », CPU basic, visibilité **Public** (l'interface Vercel doit pouvoir l'appeler).
3. Envoyer le code : `scripts/deploy_space.sh <compte>/<nom-du-space>` (Git demande l'identifiant, puis le jeton d'écriture comme mot de passe).
4. Dans Settings du Space, **Secrets** : `HAI_API_KEY`, `HF_TOKEN` (le jeton d'inférence), `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `DEMO_KEY`.
   **Variables** : `ALLOWED_ORIGINS` (adresse Vercel, voir 2), `DEMO_SHOTS=1`, `TRUSTED_PROXIES=1`, `SEARCH_PER_HOUR=200` (une salle partage une adresse IP).
5. Ouvrir `https://<compte>-<nom-du-space>.hf.space/api/health` : tout doit être à `true`. Un Space inactif s'endort : l'ouvrir 5 minutes avant la démo.

**2. Interface (Vercel)**
1. `cd frontend && vercel login`, puis `vercel` (dossier racine : `frontend`).
2. Variable d'environnement `NEXT_PUBLIC_API_URL` = adresse du Space (`https://<compte>-<nom-du-space>.hf.space`), puis `vercel --prod`.
3. Reporter l'adresse Vercel dans `ALLOWED_ORIGINS` du Space (le Space redémarre).

**3. Démo**
Ouvrir l'interface une fois avec `?cle=<DEMO_KEY>` pour lever la limite par adresse IP, et activer le mode démo dans Réglages. Une clé H réservée à la démo évite de partager les sessions avec les mesures.

## Organisation du dépôt
| Dossier ou fichier | Contenu |
|---|---|
| `frontend/` | Interface Next.js |
| `backend/` | Serveur FastAPI : identification, tri, prix, eBay, annonce, studio |
| `agents/` | Agents H Company : consigne, configuration des boutiques, script de test |
| `tests/` | Tests du tri par modèle et du bloc eBay |
| `mesures/` | Journal chiffré des sessions d'agent |
| `docs/produit/` | Parcours d'écrans, mentions, espace revendeurs |
| `docs/business-model/` | Modèle économique, coût de run et projections sur 3 ans (document et tableur) |
| `docs/sondage/` | Sondage maison et réponses anonymes |
| `docs/demo/` | Simulation vidéo pour le pitch (imitation, marquée comme telle) |
| `Specs.md`, `CONTEXT.md`, `JOURNAL.md` | Ce qu'on construit, le cadre, les décisions datées |

## État au 18/11
**Testé :** parcours complet sur ordinateur et sur téléphone, 3 photos guidées (réduites à 1600 px avant l'envoi), agents sur les 6 boutiques, studio photo, nouvelle interface (clair et sombre), espace revendeurs, arrêt des agents quand l'utilisateur quitte une recherche (en réel), limites d'usage, coefficient de rachat mesuré par catégorie sur 30 objets ([docs/calibrage-rachat.md](docs/calibrage-rachat.md)), **API eBay en réel** (annonces « Vendre seul », catégorie suggérée sur 15 produits), classement des offres par état (Gamecash n'est plus à 0 prix), lien « Publier sur eBay » qui ouvre l'éditeur avec titre, catégorie et état remplis (vérifié sur un compte connecté).
**Pas encore :** déploiement en ligne, mesure sur 10 objets, bouton « Partager photos et annonce » sur un vrai iPhone (testé avec un partage simulé ; il exige du HTTPS), publication en 1 clic sur eBay (maquette et plan dans [docs/produit/publication-ebay.md](docs/produit/publication-ebay.md), hors Specs actuelles). Le prix, la description et les photos ne passent pas par le lien eBay. Suivi dans les [issues](https://github.com/Lemtiel/Hackacton_H_Compacny/issues).

## Équipe
| | Rôle |
|---|---|
| Stephen Morlot | CEO |
| Jude Buyikana | CTO, pilote du projet |
| Josia Tatou | CAO, orchestration des agents |
| Sebastian Espinosa | CAIO, modèles et calibrage |
| Kevin Assombi | CDO, données et mesures |
| Tristan David | CPO, produit et modèle économique |

Prix indicatifs, comparaison non exhaustive. Estimation et annonce générées par IA. Prototype de hackathon, non commercialisé.
