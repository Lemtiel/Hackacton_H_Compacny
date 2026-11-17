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

### Soir : test complémentaire de Jude (Nintendo Switch OLED, 4 sites)
Lancé en parallèle du test de Stephen, avec un réglage différent : départ sur la page d'accueil, sans réponse forcée, 150 s maximum par site. Les 4 sessions sont ajoutées à `mesures/agent_runs.csv`.

| Site | Résultat | Durée | Étapes | Tokens (entrée + sortie) | Prix relevés |
|---|---|---|---|---|---|
| Easy Cash | OK, terminé seul, navigation par les menus | 167 s | 22 | 365 000 | 8 |
| Gamecash | OK, terminé seul | 76 s | 13 | 185 000 | 4 |
| Cash Converters | OK, pas de blocage Cloudflare | 124 s | 8 | 107 000 | 8 |
| Troc.com | Accès OK, aucune Switch OLED | 86 s | 15 | 212 000 | 0 |

- Sans réponse forcée, Easy Cash relève 8 prix au lieu de 3, mais met plus de 2 min 30 : partir de l'URL de catégorie (comme dans `agents/sites.py`) reste indispensable.
- Les 4 sessions lancées en même temps ont toutes abouti, sans rester bloquées en file d'attente. La limite de 3 sessions simultanées reste à clarifier avec les mentors.
- Estimation complète sur 4 sites : environ 870 000 tokens.

## Mardi 17 novembre 2026

### Business model
Préparé par Claude pour Tristan (CPO) et Stephen (CEO). Fichiers : `docs/business-model/business-model-snap-n-cash.md` et `docs/business-model/snap-n-cash-projections.xlsx`.

Décisions de l'équipe (17/11, transmises par Tristan) :
- 3 premières photos gratuites, puis abonnements Bronze 4,99 € TTC, Silver 14,99 € TTC, Entreprise 149 € HT par mois.
- Cible Entreprise : dépôts-vente et brocanteurs d'abord. Horizon des projections : 3 ans. Fondateurs non payés en an 1.
- Partenariat Vinted et Leboncoin : 0,30 € par annonce publiée pendant 12 mois, pour que les plateformes mesurent l'efficacité de l'outil, puis licence (4 000 € HT par mois et par plateforme, hypothèse).
- Pourquoi : le partenariat donne un accès officiel à leurs prix, ce qui règle l'interdiction actuelle des CGU (règle 1).

Chiffres clés (scénario central, hypothèses) :
- Coût d'une estimation : 0,17 € dans le pire cas (mesures du 16/11, modèle Holo le plus cher, agents payés à l'usage), environ 0,02 € dans le forfait H Builder.
- Marge brute par abonné, pire cas : 70 à 76 % du prix HT. Aucun abonnement ne perd d'argent tant que le coût par estimation reste sous 0,58 €.
- Chiffre d'affaires : 22 100 € en an 1, 149 500 € en an 2, 375 200 € en an 3. Résultat : +1 200 €, −23 300 €, +14 700 €. Besoin de financement : environ 37 000 €.

Points d'attention :
- Compter les 3 photos gratuites impose un compte (e-mail) : politique de confidentialité RGPD à prévoir.
- Dès qu'une plateforme nous rémunère, la page « Comment ça marche » doit le dire (elle affirme aujourd'hui qu'aucun site ne nous paie).
- Licence non exclusive : l'application Snap N Cash garde la comparaison neutre de toutes les sources.

Non vérifié : le modèle derrière `web-surfer-flash`, l'usage commercial de l'API H, le prix réaliste d'une licence, le coût d'acquisition (3 € par inscrit retenus).

