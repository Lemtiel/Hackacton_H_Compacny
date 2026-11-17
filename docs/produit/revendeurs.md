# Espace revendeurs : cahier des charges

Responsable : Tristan. Branche : `revendeurs` (partie de `interface`). Décision de Jude du 17/11.

## L'idée
Un revendeur tape un objet (« Nintendo Switch »). Nos agents relèvent les prix dans les 6 boutiques, comme pour un particulier. La page classe les annonces de la moins chère à la plus chère par rapport au marché, et montre la marge possible en revendant l'objet.

Aucun agent en plus, aucun appel serveur en plus : tout se calcule dans le navigateur à partir des résultats de la recherche existante.

## Ce qui existe déjà dans la branche
La page `frontend/app/pro/page.tsx` tourne déjà :
- champ objet et catégorie, bouton « Chercher les bonnes affaires » ;
- même barre de progression que l'app (et les écrans des agents avec `?demo=1`) ;
- médiane du marché, prix aberrants retirés ;
- liste des annonces triées par marge, avec l'étiquette « Bonne affaire ».

Lancer en local (serveur et interface) : voir le README.

## Ce qu'il reste à faire (par priorité)
1. **Curseur des frais de revente** : aujourd'hui fixé à 10 % (commission et envoi). Le rendre réglable de 0 à 25 %, la marge se recalcule.
2. **Accès depuis l'app** : un lien discret « Vous êtes revendeur ? » sur l'accueil (`frontend/app/page.tsx`) et dans `comment-ca-marche`.
3. **Cas vides** : moins de 3 prix → message « trop peu de prix pour juger » ; aucune boutique → renvoi vers la recherche classique.
4. **Habillage** : titre, textes, mise en forme des cartes. Garder les couleurs et composants de `globals.css`.
5. **Plus tard, avec eBay** : la référence de revente deviendra la médiane eBay (`fetchEbay` dans `lib/api.ts`). En attendant, l'écran dit que la référence est la médiane des boutiques.

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
