# Calibrage du prix de rachat en magasin

Issue #11 · Sebastian Espinosa · mesures du 17 et du 18 novembre 2026

## Le problème

L'écran de résultat affiche « En magasin » : ce qu'une boutique d'occasion paierait à l'utilisateur pour son objet. L'application le calcule à partir du prix de vente relevé par les agents :

```
offre de rachat estimée = prix de vente médian en boutique × coefficient
```

Le coefficient était une hypothèse des Specs (0,40), jamais mesurée. Après une première mesure sur 7 objets, il est passé à 0,59 le 18/11. Mais un seul chiffre pour toutes les catégories ne tient pas : une boutique ne garde pas la même marge sur un jeu à 25 € que sur un ordinateur à 600 €.

## La méthode

Pour chaque objet, deux prix relevés chez **Easy Cash**, la seule enseigne de notre liste qui donne une offre de rachat en ligne pour toutes nos catégories :

- **prix de vente** : catalogue `bons-plans.easycash.fr`, pages de catégorie ;
- **offre de rachat en « bon état »** : outil de reprise `prix.easycash.fr`.

Règles de mesure :

- même modèle, même capacité, même couleur ou édition, mêmes accessoires (nombre de manettes) des deux côtés ; sinon l'objet est écarté ;
- coefficient = offre de rachat ÷ prix de vente ;
- valeur retenue par catégorie : la **médiane**, moins sensible qu'une moyenne à un objet atypique.

Relevé à la main, sans agent, donc sans crédits H. Navigation par les pages de catégorie et les pages `/vendez/` uniquement : jamais le moteur de recherche d'Easy Cash ni d'URL de recherche, conformément à son robots.txt et à la règle 3 du `CLAUDE.md`.

## Les résultats

30 objets, détail dans [`mesures/calibrage_rachat_easycash_30_objets.csv`](../mesures/calibrage_rachat_easycash_30_objets.csv).

| Catégorie | Objets | Médiane | Écart observé |
|---|---|---|---|
| Informatique | 3 | 66,9 % | 67 à 69 % |
| Smartphone | 7 | 59,6 % | 47 à 70 % |
| Tablette | 3 | 49,7 % | 44 à 50 % |
| Console | 8 | 48,9 % | 38 à 78 % |
| Jeu vidéo | 9 | 43,3 % | 26 à 56 % |

Les consoles se séparent nettement selon leur prix :

| Console | Objets | Médiane |
|---|---|---|
| Moins de 300 € (PS4, Switch, Switch Lite, Switch OLED) | 5 | 44,4 % |
| 300 € et plus (PS5, PS5 Slim, Xbox Series X) | 3 | 73,8 % |

Objets mesurés :

- **Smartphone** : iPhone 11, 12, 13, 13 mini, 14, 15 ; Samsung Galaxy S21 Ultra.
- **Console** : Switch OLED, Switch, Switch Lite, PS4 500 Go, PS4 1 To, PS5, PS5 Slim, Xbox Series X.
- **Jeu vidéo** (Switch) : Advance Wars 1+2, Another Code Recollection, Super Mario Galaxy 1+2, Stardew Valley, Xenoblade Chronicles 2, Astral Chain, Bayonetta 2, Tomodachi Life, Marvel Ultimate Alliance 3.
- **Tablette** : iPad 10, iPad Mini 6, Samsung Galaxy Tab S10 FE.
- **Informatique** : MacBook Air M1 ; MacBook Air M2, sous deux références distinctes du catalogue Easy Cash.

## La règle proposée

Implémentée dans la même PR que ce document, à valider par Jude avant la fusion.

| Catégorie | Coefficient |
|---|---|
| Informatique | 0,67 |
| Smartphone | 0,60 |
| Tablette | 0,50 |
| Jeu vidéo | 0,43 |
| Console de moins de 300 € | 0,44 |
| Console de 300 € et plus | 0,74 |
| Catégorie inconnue (par défaut) | 0,59 |

Changement de code : la table remplace la constante unique dans `backend/pricing.py` (fonction `buyback_coef`), et `backend/main.py` transmet la catégorie, qu'il connaît déjà au moment du calcul. Sans catégorie, le calcul reste à 0,59 comme avant. Vérifié par `tests/test_garde_fous.py` (18 vérifications).

Vérification faite : pour chaque objet, son offre a été recalculée avec une table construite **sans lui**, puis comparée à l'offre réelle d'Easy Cash. La table par catégorie s'en approche davantage que le coefficient unique de 0,59, surtout pour les jeux et les consoles.

## Les limites

- **Une seule enseigne.** Le coefficient d'Easy Cash est appliqué à des prix venus de six boutiques. Certideal, Swappie et Gamecash peuvent avoir une autre marge.
- **Peu d'objets en tablette et en informatique** : 3 chacun, et en informatique deux modèles seulement, tous Apple.
- **Prix de vente « à partir de ».** Le catalogue affiche souvent le prix du grade le moins cher, alors que l'offre de rachat est prise en « bon état ». À grade égal, les coefficients réels seraient un peu plus bas.
- **Jeux vidéo** : forte variation d'un titre à l'autre, sur de petits montants (offres de 7 à 21 €).
- **Prix du 17 et du 18 novembre.** Ils bougent d'un jour à l'autre.
- Objets écartés : iPad Air 5 Cellular (pas d'offre en ligne pour cette version), Galaxy S24+ (page inaccessible), Overcooked et Fire Emblem Warriors (l'offre de rachat portait sur une autre édition).

## L'étape suivante : un agent de rachat en direct

Plutôt qu'estimer le rachat, le lire. Pendant la recherche, un agent H de plus va sur l'outil de reprise d'Easy Cash, choisit le modèle, la capacité et l'état, et lit l'offre réelle.

- Easy Cash donne une offre : l'application affiche ce **prix réel**.
- Easy Cash demande une cotation manuelle sur photos, ce qui arrive pour les modèles récents ou rares (iPhone 18 Pro, Sony Xperia 1 III, Xiaomi 12 Lite le 17/11) : l'application garde **la table ci-dessus en secours**.

Coût estimé : une session de plus par recherche (6 au lieu de 5, toujours deux vagues de 3), environ 0,03 € de crédits.

Faisabilité du rachat en ligne par enseigne, vérifiée les 17 et 18/11 :

| Enseigne | Accès automatique (robots.txt) | Offre de rachat en ligne | Verdict |
|---|---|---|---|
| Easy Cash | autorisé sur `/vendez/` | oui, instantanée | retenue |
| Gamecash | aucune interdiction | cote affichée en ligne | à confirmer |
| Certideal | autorisé, module `certidealinstantrebuy` | probable | à confirmer |
| Swappie | autorisé hors filtres | rachat d'iPhone | à confirmer |
| Troc.com | autorisé | non : estimation en magasin ou à domicile | exclue |
| Cash Converters | `Disallow: /` sur tout le site de reprise | oui, mais interdit | exclue (règle 2) |

État : code écrit (`agents/buyback_agent.py`, et `agents/test_buyback.py` qui le teste sur 11 objets dont 7 avec la bonne réponse connue), testé hors réseau avec une API H simulée, **jamais lancé en réel**. Il n'est branché nulle part. Premier test réel : `.venv/bin/python -m agents.test_buyback --all` (11 sessions, environ 0,35 € de crédits). Son intégration demande le feu vert de Jude et Josia, et un premier test réel.

Question ouverte pour les mentors H : peut-on répartir les sessions sur les 6 comptes de l'équipe ? Si oui, Gamecash et Certideal pourraient s'ajouter sans allonger la recherche.
