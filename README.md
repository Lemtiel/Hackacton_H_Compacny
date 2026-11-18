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
.venv/bin/python tests/test_matching.py   # tri des annonces par modèle : 52 cas
.venv/bin/python tests/test_ebay.py       # bloc eBay sur une réponse simulée : 14 vérifications
.venv/bin/python tests/test_garde_fous.py # arrêt des agents, limites d'usage, coefficient de rachat : 13 vérifications
.venv/bin/python -m agents.test_agents --site gamecash --product "Nintendo Switch" --category console   # agent réel
```
Ces trois scripts tournent à chaque push (onglet Actions).

## Mesurer
```bash
# Remplir mesures/objets_a_mesurer.csv (objet, catégorie, état, prix réellement vendu sur eBay, photos facultatives)
.venv/bin/python -m agents.mesure_objets
```
Sortie : taux de réussite par boutique (au moins 3 prix), durée d'une estimation, écart entre le prix conseillé et le prix vendu, identification correcte, cas d'échec, face aux objectifs des Specs. Les sessions d'agent sont aussi dans [`mesures/agent_runs.csv`](mesures/agent_runs.csv), les décisions et cas d'échec dans [`JOURNAL.md`](JOURNAL.md).

## Mettre en ligne
- **Serveur (Space Hugging Face) :** variables `HAI_API_KEY`, `HF_TOKEN`, `ALLOWED_ORIGINS` (adresse Vercel), `DEMO_KEY`, `DEMO_SHOTS=1`, et au besoin `HAI_MAX_PARALLEL`, `SEARCH_PER_HOUR`, `MAX_SEARCHES` (voir `.env.example`). Une clé H réservée à la démo évite de partager les 10 sessions du compte avec les mesures.
- **Interface (Vercel) :** dossier `frontend/`, variable `NEXT_PUBLIC_API_URL` = adresse du Space.
- **Démo :** ouvrir une fois l'interface avec `?cle=<DEMO_KEY>` pour lever la limite par adresse IP, et activer le mode démo dans Réglages.

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
**Testé :** parcours complet sur ordinateur et sur téléphone, 3 photos guidées, agents sur les 6 boutiques, studio photo, nouvelle interface (clair et sombre), espace revendeurs, arrêt des agents quand l'utilisateur quitte une recherche (en réel), limites d'usage, coefficient de rachat mesuré (0,59).
**Pas encore :** appel réel à eBay (validation du compte en attente), déploiement en ligne, mesure sur 10 objets. Point faible mesuré le 18/11 : peu de boutiques rendent 3 prix avec la consigne d'état stricte. Suivi dans les [issues](https://github.com/Lemtiel/Hackacton_H_Compacny/issues).

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
