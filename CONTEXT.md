# Contexte du projet Snap N Cash

## Le hackathon
- **Événement :** Hackathon 2026 « Build The Future », Eugenia School avec H Company, Vercel et Hugging Face.
- **Dates :** du lundi 16 au vendredi 20 novembre 2026.
- **Équipe :** Team 13.
- **Brief :** construire en 4 jours une startup autour d'un agent IA qui utilise un ordinateur comme un humain, sur de vrais sites, avec l'Agent API de H Company.
- **Stack imposée :** H Company, Hugging Face, GitHub.

## Critères du jury
| Critère | Poids |
|---|---|
| Excellence technique et usage de l'Agent API | 30 % |
| Pertinence et impact | 25 % |
| Faisabilité, adoption et apprentissages | 25 % |
| UX, démo et pitch | 20 % |

Le jury attend avant tout une démo live sur un vrai cas, avec des résultats chiffrés : taux de réussite, latence, cas d'échec. Nos retours sur l'Agent API font partie du livrable.

## Échéances
| Quand | Livrable | Statut |
|---|---|---|
| Lun. 16/11, 17h | Validation de l'idée (5 slides) | Déposé |
| Mer. 18/11, 17h | Parcours utilisateur, architecture, Loom de 2 min, roadmap | À faire |
| Ven. 20/11, 11h | Prototype live, fiche projet et repo GitHub, vidéo de 5 min | À faire |
| Ven. 20/11, 15h | Pitch deck de 8 à 12 slides (dont le coût de run) | À faire |
| Chaque soir, 17h à 9h | Peer review | En cours |

**Détail des livrables (brief du 16/11) :**
- **Mercredi :** parcours utilisateur (maquette ou schéma papier), architecture technique (même dessinée à la main), mini pitch Loom de 2 min max (problème, solution, avancement), roadmap jusqu'à jeudi.
- **Vendredi 11h :** prototype démontrable en live ; fiche projet sur GitHub (problème, solution, stack, architecture, repo, lien du proto, comment tester) ; vidéo démo de 5 min.
- **Pitch deck, dans cet ordre :** problème, solution, démo, business model, go-to-market, architecture technique, limites et roadmap, estimation du coût de run.
- **Pitchs :** le jury sélectionne un top 6. Chaque équipe a 6 min de pitch puis 4 min de questions.

## Planning de la semaine
- **Mardi :** session tech H Company pour les CTO de 11h à 12h, point technique de 15h à 16h.
- **Mercredi :** point business pour les CEO.
- **Jeudi :** point business pour les CEO l'après-midi, finalisation et tests.
- **Vendredi :** livrables le matin, pitchs l'après-midi.

## Ce que le brief attend d'un bon projet
1. Un problème réel et précis.
2. Une cible identifiable.
3. Un usage justifié de l'agent plutôt qu'une API ou un script (chez nous : pas d'API sur les sites des boutiques).
4. Un MVP réaliste : un parcours de bout en bout plutôt que dix fonctionnalités à moitié faites.
5. Un modèle crédible : qui paie, combien, pourquoi, et combien coûte la solution à faire tourner.

Pièges cités : ne pas mesurer, présenter des slides sans prototype, sur-concevoir, laisser des liens inaccessibles, venir au support sans diagnostic (le bug, ce qui a été testé, une capture).

## Ressources
- Crédits : Hugging Face 50 €, v0 30 $, Agent API de H Company (code à échanger sur platform.hcompany.ai).
- Le PDF du brief contient le mot de passe de l'adresse de l'équipe et les codes de crédits : il ne doit jamais être ajouté au dépôt, qui est public.

## Le projet en bref
L'utilisateur photographie un objet high-tech ou un jeu vidéo. Un modèle Hugging Face l'identifie. L'API eBay et des agents H Company relèvent les prix sur des sites d'occasion autorisés. L'app rend deux prix (vendre seul, revendre en magasin) et une annonce prête à copier. Le détail est dans [Specs.md](Specs.md).

## Équipe
| Personne | Rôle sur les slides déposées |
|---|---|
| Stephen | CEO |
| Jude | CTO, et pilote du projet |
| Josia | CAO, conception des agents |
| Sebastian | CAIO, modèles IA |
| Kevin | CDO, données et mesures |
| Tristan | CPO, expérience utilisateur |

À confirmer : le doc d'équipe indique une autre répartition (Tristan CTO, Jude CAIO, Sebastian CPO). L'équipe doit trancher.

**Rôles décrits par le brief, rattachés au projet :**
- **CEO :** vision, arbitrages, planning des livrables ; porte le pitch final et les questions du jury.
- **CTO :** architecture, qualité du code, documentation (README, schémas), proto de bout en bout et démo live avec plan B.
- **CAO :** workflows automatisés et tests de fiabilité. Chez nous : l'orchestration des agents H et le choix script ou agent, site par site.
- **CAIO :** fonctions IA, prompts reproductibles, comparaison des modèles (précision, coût, latence).
- **CDO :** collecte de données et base propre. Chez nous : le jeu de 30 objets, les offres de rachat et le journal des sessions d'agent, dans un tableur. Aucune donnée utilisateur.
- **CPO :** persona, parcours utilisateur, interface, business model, go-to-market et pitch deck.

## Cadre légal retenu (vérifié le 16/11/2026)
| Source | Accès | Statut |
|---|---|---|
| eBay | API Browse officielle, résultats affichés dans un bloc séparé | Autorisé |
| Easy Cash | Agent H, pages de catégorie seulement (recherche bloquée par le robots.txt) | Autorisé |
| Gamecash | Agent H | Autorisé |
| Troc.com | Agent H | Autorisé |
| Cash Converters | Agent H, derrière Cloudflare | Autorisé si l'agent passe sans artifice |
| Vinted, Leboncoin, Cdiscount, TikTok Shop | Bouton qui ouvre leur recherche chez l'utilisateur | Agent interdit (CGU ou robots.txt) |

Les CGU de H Company (§5.2 et §5.3) imposent de respecter les CGU des sites visités et interdisent de contourner un anti-robot.

## Concurrence
Un acteur français fait déjà l'estimation par photo à partir des seules annonces eBay. Notre différence : les enseignes françaises d'occasion en plus d'eBay, le choix chiffré entre vendre seul et vendre en magasin, et des agents visibles en direct. On ne cite pas ce concurrent dans les supports.
