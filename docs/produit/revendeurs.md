# Espace revendeurs : cahier des charges

Responsable : Tristan. Branche : `revendeurs` (partie de `interface`). Décision de Jude du 17/11.

## L'idée
Un revendeur tape un objet (« Nintendo Switch »). Nos agents relèvent les prix dans les 6 boutiques, comme pour un particulier. La page classe les annonces de la moins chère à la plus chère par rapport au marché, et montre la marge possible en revendant l'objet.

Aucun agent en plus, aucun appel serveur en plus : tout se calcule dans le navigateur à partir des résultats de la recherche existante.

## Ce qui existe dans la branche
La page `frontend/app/pro/page.tsx` tourne :
- champ objet, catégorie et état comparable, bouton « Chercher les bonnes affaires » ;
- même barre de progression que l'app (et les écrans des agents avec `?demo=1`) ;
- médiane du marché, prix aberrants retirés ;
- liste des annonces triées par marge, avec l'étiquette « Bonne affaire » ;
- curseur de frais de revente de 0 à 25 %, cas vides et accès depuis l'app.

La collecte est partagée avec le parcours principal. Chaque agent reçoit le modèle, la variante,
la capacité et l'état recherchés. Une offre ne participe au calcul que si elle correspond au modèle,
affiche un état équivalent à celui demandé et possède une URL de fiche produit vérifiable. Tous les sites compatibles sont
lancés en parallèle, dans la limite de 10 sessions H.

Lancer en local (serveur et interface) : voir le README.

## Suite possible
1. **Après validation de Jude :** remplacer le coefficient de rachat de 0,40 par la calibration retenue.
2. **Plus tard, avec eBay :** la référence de revente deviendra la médiane eBay (`fetchEbay` dans `lib/api.ts`). En attendant, l'écran dit que la référence est la médiane des boutiques.

## Règles du calcul (ne pas changer sans Jude)
- Médiane des prix des boutiques, après retrait des prix sous la moitié ou au-dessus du double de la médiane (même règle que `backend/pricing.py`).
- Marge = médiane × (1 − frais) − prix d'achat.
- « Bonne affaire » quand le prix est au moins 15 % sous la médiane.
- Un prix retiré comme aberrant s'affiche à part, avec « à vérifier » (souvent un autre modèle ou un objet en panne).

## Règles à respecter
- Les prix restent indicatifs, et la page le dit.
- Pas de compte, pas de paiement, rien de stocké côté serveur.
- Les noms des boutiques et les liens vers leurs annonces restent visibles (on dit d'où viennent les prix).
- Snap N Cash reste un prototype de hackathon : cet espace ne sera pas commercialisé (décision de Jude, JOURNAL.md du 17/11).

## Fichiers utiles
- `frontend/lib/api.ts` : `searchPrices` (recherche des agents, résultats site par site), `euros`, `isDemo`.
- `frontend/components/SearchScreen.tsx` : `SearchProgress` (barre et écrans des agents), type `Row`.
- `frontend/lib/variants.ts` : `guessCategory` (catégorie devinée depuis le nom).
