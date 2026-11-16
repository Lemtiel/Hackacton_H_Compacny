# Snap N Cash

## Contexte et objectif
86 % des Français gardent des objets inutilisés (19 en moyenne, 320 € par foyer selon leur estimation), mais 17 % seulement les ont déjà revendus. Ils citent trois freins : le manque de temps (29 %), des démarches jugées complexes (20 %) et la peur de se tromper de prix (16 %) (OpinionWay pour Leboncoin, septembre 2025, 1 054 personnes). Pour le high-tech, 46 millions de téléphones dorment dans les tiroirs (Harris Interactive et Crédoc pour Ecologic, 2023).

Snap N Cash vise les 18-35 ans qui veulent revendre du high-tech ou des jeux vidéo. Le projet sert de MVP au hackathon Eugenia × H Company (Team 13), avec une démo live le vendredi 20 novembre 2026.

## Solution retenue
L'utilisateur décrit son objet (photo, questions d'état ou texte libre). Un modèle Hugging Face l'identifie. L'API eBay et des agents H Company relèvent les prix sur des sites d'occasion autorisés. L'app affiche une fourchette, un prix conseillé, le prix « vendre seul », le prix « revendre en magasin » et une annonce prête à copier.

H Company sert à une seule tâche : naviguer sur les sites sans API. Hugging Face et notre code font le reste.

## Périmètre
**Inclus :**
- Site web adapté au mobile et à l'ordinateur.
- Catégories : high-tech et jeux vidéo.
- Entrées : photo seule, photo suivie de questions d'état (état, boîte, accessoires), texte libre.
- Sources de prix :
  - eBay via l'API Browse officielle ;
  - agents H sur Easy Cash (pages de catégorie uniquement), Gamecash, Troc.com et Cash Converters.
- Boutons qui ouvrent la recherche de l'objet sur Vinted, Leboncoin, Cdiscount et TikTok Shop, dans le navigateur de l'utilisateur.
- Annonce générée en 4 formats : Vinted, Leboncoin, eBay, texte générique.
- Historique des estimations stocké dans le navigateur de l'utilisateur.
- Utilisation anonyme : ni compte ni paiement.

**Exclu (pour l'instant) :**
- Code-barres (roadmap).
- Comptes utilisateurs et paiement des packs (roadmap).
- Offre revendeurs, ou détecteur de bonnes affaires (roadmap).
- Chef d'orchestre smolagents (option jeudi si tout tourne).
- Publication automatique des annonces.
- Tout agent sur Vinted, Leboncoin, Cdiscount, TikTok Shop, Back Market ou Label Emmaüs.

## Comportements attendus
1. **Entrée.** L'utilisateur prend une photo, répond aux questions d'état ou tape le nom de l'objet. Le texte libre sert aussi de secours si la photo échoue.
2. **Contrôle de la photo.** Un modèle de détection de visages vérifie la photo. Si un visage apparaît, l'app la refuse et demande d'en reprendre une. La consigne « photo de l'objet seul » s'affiche à la prise de vue.
3. **Identification.** Un modèle vision Hugging Face extrait la marque, le modèle et l'état.
4. **Recherche des prix, en parallèle :**
   - un appel à l'API eBay Browse ;
   - une session d'agent H par site. Chaque session reçoit la même consigne, sans code propre au site. Sur Easy Cash, l'agent navigue par les menus de catégorie et n'utilise pas la recherche, bloquée par le robots.txt.
5. **Affichage progressif.** Chaque site s'affiche dès qu'il répond. L'écran montre les agents en train de naviguer si l'API H le permet. Sinon, il affiche les étapes de chaque agent (« ouvre Easy Cash », « catégorie Smartphones », « 6 prix trouvés »), puis le replay de la session. Un site qui dépasse 90 secondes passe en « indisponible », et l'estimation se fait sans lui. Un site sans résultat, par exemple Gamecash pour un téléphone, affiche « aucun résultat ».
6. **Calcul (notre code, sans IA), une fourchette par bloc, sans jamais mélanger eBay et les autres sites (licence eBay) :**
   - **Vendre seul :** à partir des annonces eBay seules. Valeurs aberrantes retirées, fourchette, puis médiane moins une décote. Ce prix est le prix conseillé.
   - **Revendre en magasin :** à partir des boutiques seules (Easy Cash, Gamecash, Troc.com, Cash Converters). Valeurs aberrantes retirées, fourchette, puis prix de revente multiplié par un coefficient. L'écran l'affiche comme une estimation basse.
7. **Résultat :** deux blocs séparés, « Vendre seul (eBay) » et « Revendre en magasin », chacun avec sa fourchette, son prix et ses prix détaillés par site avec leurs liens. Le prix conseillé est celui de « vendre seul ».
8. **Annonce.** Un modèle de texte Hugging Face rédige l'annonce dans les 4 formats. L'utilisateur la copie et la publie lui-même. Les données eBay ne passent pas dans le modèle de texte.
9. **Historique.** Le navigateur garde les estimations passées. Notre serveur ne conserve rien.
10. **Mentions obligatoires :**
    - une page « Comment ça marche » qui liste les sites consultés, précise que la comparaison n'est pas exhaustive et donne le critère de classement (article L111-7 du Code de la consommation) ;
    - la mention « estimation et annonce générées par IA » (AI Act, article 50) ;
    - des prix présentés comme indicatifs, sans jamais promettre « tous les sites ».

## Architecture
- **Interface :** Next.js générée avec v0, hébergée sur Vercel.
- **Serveur :** Python (FastAPI) dans un Space Hugging Face. Il envoie les résultats site par site au fur et à mesure.
- **Modèles Hugging Face :** détection de visages, vision pour l'identification, texte pour l'annonce. Jude valide chaque modèle sur proposition justifiée avant son utilisation.
- **Agents :** Agent API de H Company.
- **Prix eBay :** API Browse.
- **Code :** github.com/Lemtiel/Hackacton_H_Compacny.

## Règles de conformité
- Aucun agent sur un site dont les CGU ou le robots.txt interdisent l'accès automatisé. Les CGU de H Company (§5.3) l'exigent aussi.
- Aucun contournement d'anti-robot : un site qui bloque l'agent sort de la liste.
- Aucune donnée conservée côté serveur : ni photo, ni annonce relevée, ni pseudonyme de vendeur.
- Aucune capture des pages des sites sources affichée à l'utilisateur, pour respecter leur interdiction de reproduction : le prix et le lien suffisent.

## Alternatives écartées
- **Lire Leboncoin et Vinted avec un agent :** leurs CGU l'interdisent, ainsi que celles de H Company (§5.3). Leboncoin a gagné ses procès contre Entreparticuliers et Jinka.
- **Simuler Leboncoin :** le jury attend de vrais sites, et une imitation pose un problème de marque.
- **Changer de marché (États-Unis) :** le risque se déplace sans disparaître, et la stratégie de lancement devient difficile à défendre en 4 jours.
- **Remplacer H par un agent Hugging Face :** le brief exige l'Agent API de H Company, et un autre outil ne rend pas légal un site interdit.
- **Code-barres pour vendredi :** il ne sert que pour les produits encore dans leur boîte et demande une base de codes-barres.
- **VL-Check, veille d'appels d'offres :** idées écartées au profit de la seconde main.

## Hypothèses assumées et risques
| Hypothèse | Ce qui fait changer d'avis |
|---|---|
| Les agents H accèdent à au moins 2 des 4 sites | Moins de 2 au test de mardi : chercher d'autres sources autorisées (Certideal, Recommerce, Largo, après vérification de leurs CGU) |
| Une session d'agent coûte moins de 0,25 $ et dure moins de 90 s | Dépassement au test de mardi : passer aux scripts sur les sites simples (décision de Josia) |
| Coefficient de rachat en magasin autour de 40 % | Les 5 offres réelles relevées jeudi le remplacent |
| Décote eBay autour de 10 % | Les 30 objets de test la recalculent |
| L'API H permet d'afficher l'agent en direct | Non au test de mardi : afficher les étapes de chaque agent, puis le replay de la session |
| L'usage commercial de l'API H est autorisé | Réponse négative des mentors : modèle économique à revoir (modèles Holo en accès libre, licence à vérifier) |

**Risques :**
- Cash Converters est derrière Cloudflare et peut bloquer l'agent.
- La licence eBay complète n'a pas encore été lue.
- Un juré peut objecter qu'un script ferait le même travail que l'agent. Réponse : zéro code par site, navigation réelle, et un 5e site ajouté en démo par une simple ligne de configuration, testé à l'avance.
- Face à Reprizo (eBay seul), la différence repose sur trois atouts combinés : plus de sources, le choix entre vendre seul et vendre en magasin, et des agents visibles en direct.
- Les chiffres du problème viennent de sondages déclaratifs commandés par des acteurs de la revente.
- Doute principal de l'équipe : l'accès des agents aux sites.

## Critères de succès
Mesurés sur un jeu de 30 objets high-tech et jeux vidéo. Le prix de référence est le prix réellement vendu sur eBay, relevé à la main.

| Mesure | Objectif |
|---|---|
| Identification correcte (marque et modèle) | ≥ 90 % |
| Écart médian entre le prix conseillé et la référence | ≤ 15 % |
| Prix de référence compris dans la fourchette | ≥ 80 % |
| Sessions d'agent qui rapportent au moins 3 prix, par site, quand le site vend ce type d'objet | ≥ 80 % |
| Temps de la photo au résultat (médiane) | < 2 min |
| Coût par estimation | < 0,25 $ |
| Temps gagné (3 testeurs, à la main contre avec l'app) | Chiffre mesuré, cité dans le pitch seulement s'il est prouvé |

**Résultat minimum acceptable :** le parcours Nintendo Switch tourne en live de bout en bout, avec eBay et au moins une boutique, pour que les deux blocs s'affichent. Les mesures sont présentées avec leurs cas d'échec.

## Modèle économique et coût de run
Le brief exige de dire qui paie, combien et pourquoi, ainsi que le coût de run (slide dédiée du pitch deck).

- **MVP :** gratuit et anonyme, sans compte ni paiement.
- **Pistes déjà notées (roadmap) :** packs d'estimations payants, offre revendeurs.
- **Coût de run :** objectif < 0,25 $ par estimation. Il se calcule à partir des mesures réelles : sessions d'agent H (tokens, durée), appels Hugging Face (vision, texte, visages), hébergement (Vercel, Space).
- **À trancher :** qui paie (particulier, revendeur, enseigne), le prix, et la marge par rapport au coût de run. Dépend aussi de la réponse des mentors sur l'usage commercial de l'API H (§9.4).

Responsables : Stephen (CEO) et Tristan (CPO). Présenté au point business du mercredi.

## Contraintes
- **Temps :** livrables lundi 16/11 17h, mercredi 18/11 17h, vendredi 20/11 11h (prototype, repo, vidéo) et 15h (pitch deck).
- **Budget :** crédits du hackathon (H Company, Hugging Face 50 €, v0 30 $), rien de payant en plus.
- **Stack imposée :** H Company, Hugging Face, GitHub.
- **Équipe :** Stephen (CEO), Jude (CTO, pilote du projet), Josia (CAO), Sebastian (CAIO), Kevin (CDO), Tristan (CPO).
- **Démo :** Nintendo Switch d'abord (prix relevés sur 3 boutiques au test du 16/11). Le Redmi Note 10S passe en second : aucune boutique n'en avait en vente au test, il sert donc à montrer le cas « aucun résultat en magasin », avec le seul bloc eBay. Objet préparé à l'avance et recherche en direct, avec adaptation si besoin.
- **Plan B de la démo (exigé du CTO par le brief) :** une vidéo du parcours complet enregistrée la veille, plus le replay des sessions d'agent H. Si un site bloque ou dépasse 90 s en live, on bascule dessus sans improviser.
- **Fiche projet sur GitHub (vendredi 11h) :** le README contient le problème, la solution, la stack, l'architecture, le lien du proto et « comment tester ». Tous les liens sont vérifiés en navigation privée avant le dépôt.

## Actions avant démarrage
| # | Action | Responsable | Échéance |
|---|---|---|---|
| 1 | Créer le compte développeur eBay et la clé API | Jude | Lundi 16/11 au soir |
| 2 | Tester les agents H sur les 4 sites (accès, temps, coût) | Jude et Josia | Mardi 17/11 midi |
| 3 | Demander aux mentors H si l'usage commercial de l'API est autorisé (§9.4) | Jude | Mardi 17/11 11h |
| 4 | Décider script ou agent, site par site, selon le test | Josia | Mardi 17/11 au soir |
| 5 | Sondage maison sur le temps passé à fixer un prix et publier (5 à 10 personnes) | Tristan | Lundi 16/11 au soir |
| 6 | Constituer le jeu de 30 objets avec leur prix eBay réellement vendu | Kevin | Mercredi 18/11 17h |
| 7 | Relever 5 offres de rachat réelles pour caler le coefficient | Kevin | Jeudi 19/11 midi |
| 8 | Lire la licence de l'API eBay en entier | Jude | Mercredi 18/11 |
| 9 | Mesure avec 3 testeurs, à la main puis avec l'app | Tristan | Jeudi 19/11 |
| 10 | Proposer le modèle économique et le calcul du coût de run | Stephen et Tristan | Mercredi 18/11 (point business) |
| 11 | Enregistrer la vidéo plan B et garder les replays des sessions | Jude | Jeudi 19/11 au soir |
| 12 | Rédiger la fiche projet dans le README et vérifier les liens | Jude | Vendredi 20/11 11h |

## Prochaines étapes
1. Déposer la validation de l'idée (livrable de lundi 17h).
2. Lancer le garde-fou de conformité en mode rapide avant d'écrire du code.
3. Créer la clé API H Company et la clé eBay.
4. Tester les agents sur les 4 sites (mardi matin).
5. Construire le parcours de bout en bout sur la Nintendo Switch.
6. Mesurer sur 10 objets (mercredi), puis sur 30 (jeudi).
7. Préparer la démo, la vidéo de 5 min et le pitch deck.
