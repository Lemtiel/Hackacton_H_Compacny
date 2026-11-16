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
