# Journal de bord

## Lundi 16 novembre 2026

### Matin : cadrage
- Lecture du brief du hackathon (28 slides). Création d'un doc d'équipe pour cadrer et collaborer.
- Exploration des startups fintech YC 2026-2027 pour trouver une idée.

### Idées étudiées puis écartées
| Idée | Pourquoi écartée |
|---|---|
| VL-Check : contrôle des VL de fonds sur les sites des sociétés de gestion | Cible pointue, difficile à expliquer au jury, concurrence proche (Zomma, YC Summer 2026) |
| Veille d'appels d'offres pour PME | Abandonnée au profit de la seconde main |
| Le Grenier avec lecture de Leboncoin et Vinted | Interdit : robots.txt et CGU de Leboncoin, procès gagnés contre Entreparticuliers et Jinka, CGU de Vinted contre le scraping et le « screen scraping » |
| Contourner les anti-robots avec un agent | Refusé : contournement interdit, et contraire aux CGU de H Company |
| Simuler un faux Leboncoin | Le jury attend de vrais sites, et une imitation pose un problème de marque |
| Changer de marché (États-Unis) | Le risque se déplace sans disparaître |

### Après-midi : vérifications légales
- robots.txt et CGU lus pour 25 sites français et 14 marketplaces étrangères.
- Sources retenues : API eBay, Easy Cash, Gamecash, Troc.com, Cash Converters.
- Constat clé : les CGU de H Company (§5.3) imposent de respecter les CGU des sites visités. Vinted est donc exclu, même en simple lecture.
- Un concurrent français existant utilise seulement eBay. Notre différence : les enseignes françaises d'occasion et le choix « vendre seul ou en magasin ».

### Décisions
- Projet retenu : **Snap N Cash** (d'abord nommé Le Grenier, puis Attic). Cible : 18-35 ans, high-tech et jeux vidéo.
- H Company sert uniquement à la navigation sur les sites sans API. Hugging Face et notre code font le reste.
- Prix « vendre seul » = médiane eBay moins une décote. Prix « en magasin » = prix de revente en boutique multiplié par un coefficient, affiché comme estimation basse.
- Une fourchette par bloc, sans mélanger eBay et les boutiques (licence eBay).
- Démo : Redmi Note 10S, puis Nintendo Switch.
- Interview de cadrage menée, Specs.md validé.

### Livrable
- Validation de l'idée déposée : 5 slides Canva (nom, problème, solution, personae, stack, rôles).

### Points ouverts
- Rôles : le doc d'équipe et les slides ne concordent pas. À trancher en équipe.
- Usage commercial de l'API H (§9.4 de leurs CGU) : question aux mentors H, mardi 11h.
- Accès des agents aux 4 sites : test mardi matin.

### À faire ce soir
- Jude : créer le compte développeur eBay et la clé API.
- Tristan : sondage maison (5 à 10 personnes) sur le temps passé à fixer un prix et publier une annonce.
- Tous : peer review avant 9h.

### Soir : relecture du brief officiel
- Brief « Build The Future » (28 slides) comparé aux Specs. Le cadrage y répond : agent sur de vrais sites, usage justifié, mesures chiffrées, retours sur l'Agent API.
- Écarts corrigés dans Specs.md et CONTEXT.md :
  - section « Modèle économique et coût de run » ajoutée (à trancher par Stephen et Tristan pour le point business du mercredi) ;
  - plan B de la démo : vidéo enregistrée la veille et replay des sessions d'agent ;
  - fiche projet dans le README pour vendredi 11h ;
  - crédits corrigés : Hugging Face 50 €, v0 30 $ ;
  - rôles du brief rattachés au projet (CAO : orchestration des agents ; CDO : jeu de test et journal des sessions).
- Le PDF du brief contient des identifiants : il reste hors du dépôt.

### Soir : premiers tests de l'Agent API H
Script : `agents/test_agents.py`, agent `h/web-surfer-flash`, même consigne pour tous les sites, réponse forcée à 70 s, annulation à 90 s. Mesures brutes dans `mesures/agent_runs.csv`.

| Site | Objet | Résultat | Durée | Étapes | Tokens (entrée + sortie) | Prix relevés |
|---|---|---|---|---|---|---|
| Troc.com | Redmi Note 10S | Aucun résultat (le site n'en vend pas) | 35 s | 5 | 62 000 | 0 |
| Gamecash | Nintendo Switch | OK, réponse forcée | 80 s | 12 | 201 000 | 4 |
| Easy Cash | Nintendo Switch | OK, réponse forcée, pages de catégorie seulement | 84 s | 10 | 158 000 | 3 |
| Cash Converters | Nintendo Switch | OK, réponse forcée, pas de blocage Cloudflare | 84 s | 8 | 115 000 | 2 |
| Troc.com | Nintendo Switch | Jamais démarré : 4e session en file d'attente | 95 s | 0 | 0 | 0 |

Ce qui a marché :
- Les 3 boutiques testées sur la Switch ont laissé passer l'agent, sans captcha ni blocage.
- La réponse structurée (titre, prix, état, lien) arrive bien au format demandé.
- Chaque session a un lien Agent View (direct et replay) : l'affichage de l'agent en direct est possible.

Ce qui a cassé ou surpris :
- Le compte est limité à 3 sessions simultanées : la 4e attend. Il faut plus de slots (question aux mentors) ou lancer les sites en deux vagues.
- Aucune session n'a fini seule avant 70 s sur la Switch : toutes ont eu besoin de la réponse forcée. L'objectif de 3 prix par site n'est tenu que sur 2 sites sur 3.
- L'agent finit en statut `idle` et non `completed` : il faut annuler la session pour libérer le slot.
- Qualité : une offre Gamecash a un titre tronqué et un lien de recherche au lieu d'un lien produit ; une offre Cash Converters regroupe plusieurs annonces en une ligne.
- Le coût en dollars n'est pas calculé : le prix par token au-delà du forfait reste à trouver.

Non testé : Redmi Note 10S sur Easy Cash, Gamecash et Cash Converters ; Troc.com sur la Switch ; répétabilité (un seul essai par site).

### Soir : Redmi Note 10S sur les 3 autres boutiques
| Site | Résultat | Durée | Étapes | Tokens (entrée + sortie) | Prix relevés |
|---|---|---|---|---|---|
| Easy Cash | Aucun 10S (4 pages Xiaomi parcourues, réponse forcée) | 85 s | 19 | 313 000 | 0 |
| Gamecash | Aucun résultat : le site ne vend pas de téléphones | 18 s | 2 | 21 000 | 0 |
| Cash Converters | Aucun 10S (seulement des Redmi Note 10 Pro) | 29 s | 3 | 35 000 | 0 |

Constat : le 16/11, aucune des 4 boutiques n'a de Redmi Note 10S en vente. Le « résultat minimum acceptable » des Specs (parcours Redmi avec eBay et au moins une boutique) ne peut pas s'afficher avec cet objet. À trancher en équipe : changer l'objet de démo (la Switch donne des prix sur 3 boutiques) ou accepter les modèles proches (Redmi Note 10, 10 Pro) en les signalant comme tels.

Autre mesure : sur Easy Cash, sans recherche, l'agent consomme beaucoup plus (313 000 tokens, 19 étapes) parce qu'il feuillette les pages de catégorie.

### Décision : la démo principale passe sur la Nintendo Switch
- Décidé par Stephen le 16/11 au soir, après les tests d'agents. À confirmer avec Jude et l'équipe.
- Pourquoi : la Switch a donné des prix sur 3 boutiques (Gamecash, Easy Cash, Cash Converters), alors qu'aucune des 4 n'avait de Redmi Note 10S en vente.
- Le Redmi Note 10S reste le second objet : il montre le cas « aucun résultat en magasin », où seul le bloc eBay s'affiche.
- Specs.md mis à jour : résultat minimum acceptable, ordre de la démo, prochaines étapes.
- À revérifier la veille de la démo : les stocks d'occasion changent d'un jour à l'autre.

### Soir : test de l'iPhone 12 (Gamecash exclu, il ne vend pas de téléphones)
| Site | Résultat | Durée | Étapes | Tokens (entrée + sortie) | Prix relevés |
|---|---|---|---|---|---|
| Easy Cash | OK, réponse forcée, pages de catégorie seulement | 83 s | 10 | 155 000 | 2 (médiane 197 €) |
| Cash Converters | OK, réponse forcée | 80 s | 13 | 210 000 | 4 (médiane 225 €) |
| Troc.com | OK, terminé seul | 60 s | 10 | 136 000 | 1 (235 €) |

- Premier objet high-tech qui donne des prix sur 3 boutiques. Troc.com répond pour la première fois.
- Défauts : Cash Converters rend le lien de la recherche au lieu des liens produit, et sans l'état. Easy Cash n'a relevé que 2 prix alors que la page en montrait au moins 6 : le temps manque, pas les annonces. L'unique offre Troc.com est dans un magasin de Bruxelles.
- Les capacités sont mélangées (64 et 128 Go) : il faudra préciser la capacité dans la consigne ou la demander à l'utilisateur.

### Soir : première version du parcours « photo puis recherche »
Demandé par Stephen. Branche `photo-et-recherche`.

Ce qui est construit :
- `backend/main.py` (FastAPI) : `POST /api/identify` (photo) et `GET /api/search` (résultats envoyés site par site).
- `backend/photo.py` : contrôle de visage puis identification. La photo reste en mémoire, rien n'est écrit sur disque.
- `backend/pricing.py` : bloc « Revendre en magasin », sans IA. Prix hors de la plage [médiane ÷ 2 ; médiane × 2] écartés, puis médiane × 40 %.
- `backend/static/index.html` : page de test (photo ou texte, agents en cours, prix par site, estimation). Elle sert à tester le parcours en attendant l'interface v0.
- Un site qui ne vend pas la catégorie n'ouvre pas d'agent (Gamecash pour un téléphone) : c'est une ligne de configuration, pas du code par site.
- 3 agents au plus en même temps : le 4e site attend, et l'écran l'indique.

Modèles Hugging Face PROPOSÉS, à valider par Jude avant usage en production :
| Rôle | Modèle | Pourquoi | Coût et temps |
|---|---|---|---|
| Visages | `opencv/face_detection_yunet` (230 Ko) | Tourne sur le serveur : la photo ne part chez aucun tiers | Gratuit, 10 à 300 ms mesurés |
| Identification | `google/gemma-4-31B-it` par le routeur HF | Modèle vision généraliste, peu cher, plusieurs fournisseurs | 0,14 à 0,20 $ par million de tokens en entrée, non mesuré |

Alternatives pour l'identification, à comparer sur le jeu de 30 objets : `Qwen/Qwen3-VL-30B-A3B-Instruct` (spécialisé vision, 0,15 $) et `Qwen/Qwen3.5-9B` (le moins cher, 0,10 $). Le modèle se change par la variable `HF_VISION_MODEL`.

Testé :
- photo avec visage refusée, photo d'objet acceptée par le contrôle, fichier illisible refusé ;
- recherche de bout en bout dans la page, en texte, sur la Nintendo Switch (voir mesures) ;
- calcul du bloc magasin sur des prix d'exemple.

Non testé :
- l'identification par le modèle vision : il manque `HF_TOKEN` dans `.env` ;
- la prise de photo sur un vrai téléphone.

Points à trancher :
- Contradiction dans les Specs : montrer « les agents en train de naviguer » (comportement 5) revient à montrer les pages des sites, ce que la règle « pas de capture des pages sources » interdit. La page affiche donc seulement les étapes.
- Le contrôle de visage refusera une jaquette de jeu vidéo qui montre un visage.
- Le bloc « Vendre seul » (eBay) n'existe pas encore : la page ouvre seulement la recherche sur Vinted, Leboncoin et eBay.

Mesure du test dans la page (Nintendo Switch, 4 sites, 3 agents en parallèle) : Easy Cash 1 prix en 83 s, Gamecash 2 prix en 80 s, Troc.com aucun résultat, Cash Converters 8 prix en 69 s après attente d'un agent libre. Estimation magasin affichée : 56 €.
Défaut constaté : les 8 prix de Cash Converters sont des Switch Lite, un autre modèle. Ils tirent l'estimation vers le bas. La consigne « même modèle exact » ne suffit pas : il faudra un contrôle des titres dans notre code.

Validation : Stephen valide `google/gemma-4-31B-it` et `opencv/face_detection_yunet` pour les tests (16/11 au soir). La validation de Jude reste nécessaire avant la démo.

### Soir : test de l'identification par la photo (`google/gemma-4-31B-it`)
| Image de test | Résultat | Temps |
|---|---|---|
| Nintendo Switch (photo produit) | Nintendo Switch, console, confiance 1,0 | 4,4 s |
| Dos d'iPhone 12 (dessin) | « Apple iPhone », sans le numéro, confiance 0,7 | 5,3 s |
| Tasse de café | Refusée : pas un objet high-tech | 8,3 s |
| Portrait | Refusée par le contrôle de visage, avant tout appel au modèle | moins de 0,3 s |

- Le modèle ne devine pas le modèle exact d'un iPhone vu de dos : il faudra demander le modèle à l'utilisateur quand la confiance est basse ou le nom trop vague.
- Bug corrigé : une variable `HF_VISION_MODEL` vide dans `.env` faisait échouer l'appel.
- Limites : 4 images seulement, des photos propres et non des photos d'utilisateurs. La précision réelle reste à mesurer sur le jeu de 30 objets.

### Soir : annonce générée en 4 formats (Vinted, Leboncoin, eBay, texte générique)
Fait : `backend/listing.py`, route `POST /api/listing`, bloc « 3. Votre annonce » dans la page de test (état, boîte, accessoires, détails, 4 onglets, titre et description modifiables, boutons de copie).

Choix :
- **Modèle de texte PROPOSÉ : `google/gemma-4-31B-it`**, le même que pour l'identification, changeable par `HF_TEXT_MODEL`. Justification : déjà en place, un seul modèle à valider et à payer, français correct sur les essais. Stephen a donné le feu vert pour coder ; la validation de Jude reste nécessaire.
- Le modèle ne reçoit que ce que l'utilisateur a saisi (nom, état, boîte, accessoires, détails). **Aucun prix et aucune annonce relevée n'y passent**, donc aucune donnée eBay (règle 4). L'annonce ne contient pas de prix : il se saisit à part sur chaque site.
- Un seul appel rend les 4 formats. Notre code coupe les titres à la longueur de chaque site (Vinted 60, Leboncoin 50, eBay 80). Ces longueurs sont à vérifier sur les sites.
- Mention « Annonce générée par IA. Relisez-la avant de publier » sous l'annonce.

| Test | Résultat | Temps |
|---|---|---|
| Nintendo Switch, bon état, sans boîte, 2 Joy-Con + dock + chargeur, rayures au dos | 4 annonces fidèles, rien d'inventé, défaut cité | 28 s |
| iPhone 12, 64 Go noir, micro-rayure, câble (dans la page) | 4 annonces fidèles, boîte « non précisé » non mentionnée | environ 30 s |

Limites :
- 28 s, c'est long. Pistes : un modèle de texte plus petit, ou un appel par format affiché au fur et à mesure.
- 2 objets testés seulement. Pas de test avec un texte hostile dans le champ « détails ».
- Copie dans le presse-papiers non testée sur téléphone.

### Soir : tri des annonces par modèle (défaut « Switch Lite » corrigé)
Fait : `backend/matching.py` (notre code, sans IA), branché dans `/api/search`. Cas types dans `tests/test_matching.py`.

Une annonce est écartée si son titre : ne contient pas tous les mots du modèle cherché (la marque est facultative) ; contient un mot de déclinaison absent de la recherche (Lite, OLED, Pro, Max, Mini, Slim...) ; porte un numéro collé au nom (« Switch 2 ») ; désigne un accessoire (« Coque... », « Manette... », « ... pour ... »). Si l'utilisateur écrit la capacité (« iPhone 12 64 Go »), seules les annonces de cette capacité restent. La page affiche le nombre d'annonces écartées par boutique.

Aussi : quand la photo ne donne pas le modèle exact (marque seule, téléphone sans numéro, confiance sous 0,6), la page demande de compléter le nom avant la recherche.

| Test | Résultat |
|---|---|
| 25 cas types (Switch, iPhone 12, Redmi Note 10S, PlayStation 4, un jeu) | 25 corrects |
| Recherche réelle « Nintendo Switch », 4 boutiques | Gamecash 3 prix, Easy Cash 3 prix, Troc.com aucun résultat, Cash Converters 1 prix gardé et 4 écartés |

Effet : la médiane en boutique passe à 166 € sur 7 prix (de 145 à 200 €), et l'estimation magasin de 56 € à 66 €.

Limites :
- Sans capacité saisie, toutes les capacités sont mélangées dans la médiane.
- Un jeu dont le titre ne commence pas par « Jeu » (« Zelda Switch ») passe encore pour une console ; le retrait des valeurs aberrantes le rattrape en partie.
- La liste des mots de déclinaison est tenue à la main. Une faute ou une abréviation dans un titre écarte une bonne annonce.
- La demande du modèle exact n'a pas été retestée avec une photo.
- 1 seul objet testé en réel.
