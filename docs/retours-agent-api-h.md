# Retours sur l'Agent API de H Company

*Team 13, Snap N Cash. Rédigé le 19/11/2026 à partir de nos essais du 16 au 19/11. Chaque constat renvoie à une mesure du dépôt : `mesures/agent_runs.csv`, `mesures/mesure_*.csv` et [JOURNAL.md](../JOURNAL.md).*

## Notre usage
Nos agents relèvent des prix d'occasion sur cinq boutiques françaises sans API : Easy Cash, Gamecash, Cash Converters, Certideal et Swappie (Troc.com mis en pause le 19/11 : 0 prix sur 10 objets). Chaque estimation ouvre une session `h/web-surfer-flash` par boutique concernée (3 ou 4 selon la catégorie de l'objet), toutes en parallèle, avec une réponse structurée (titre, prix, état, lien) et un délai de 90 s. Un second agent, en démo sur notre Mac, prépare un brouillon d'annonce eBay dans le Chrome du vendeur (mode `user_device`).

## Ce qui marche bien
- **Un agent pour cinq sites.** Aucune ligne de code n'est propre à une boutique. Nous avons ajouté Certideal et Swappie le 17/11 par une simple entrée de configuration, et ils ont marché au premier essai.
- **Le passage des protections ordinaires.** Cash Converters et Swappie sont derrière Cloudflare : l'agent est passé sans captcha. Fnac l'a bloqué en 15,7 s (« You have been blocked ») : nous l'avons retiré de la liste, sans chercher à contourner.
- **La réponse structurée.** Le schéma Pydantic (`Offers`) nous rend des offres directement exploitables. Nos contrôles (modèle, état, lien) écartent le reste.
- **Le parallélisme.** Le 19/11 en ligne, cinq sessions ont tourné ensemble et ont rendu leurs prix en 82 à 89 s. Le test à 10 sessions simultanées figure plus bas.
- **Les captures pas à pas** (`ObservationEvent.image`). Notre serveur les relaie à l'interface avec la clé API, sans jamais exposer la clé : 41 captures sur une recherche « Nintendo Switch ». C'est ce qui rend la démo lisible.
- **Les fichiers joints** pour un navigateur cloud : 10 fichiers, 7 Mo au plus. Un agent a déposé une image sur une page d'envoi en 23 s.

## Ce qui nous a freinés
| Constat | Preuve | Ce que nous avons fait |
|---|---|---|
| Pas de vidéo en direct avec `h/web-surfer-flash` : aucun `LiveViewUrlEvent` reçu | essai du 17/11 | Captures pas à pas relayées par notre serveur |
| En mode `user_device`, impossible de joindre des fichiers (« files: the agent needs a workstation or a cloud browser ») et pas d'outil d'envoi de fichier | essais du 18/11 | Outil à nous (`upload_listing_photos`, Playwright sur le Chrome local) appelé par l'agent |
| Le pont `holo local browser` s'arrête quand le Chrome n'a aucun onglet ouvert, et l'agent reste à « étape 0 » sans message d'erreur | 18/11, 23h55 | Notre serveur ouvre l'onglet s'il manque et signale l'arrêt du pont |
| Une session coupée au délai renvoie un statut d'échec, même quand elle a déjà trouvé des offres valides | Easy Cash, 2 offres « Bon état » perdues le 18/11 | Nous gardons les offres valides d'une session coupée |
| Durée très variable selon le site : 24 à 124 s pour la même consigne | `mesures/agent_runs.csv` | Réponse forcée à 70 s, annulation à 90 s |
| Consommation de jetons élevée sur les sites à feuilleter : 313 000 jetons et 19 étapes sur Easy Cash sans moteur de recherche | 16/11 | Navigation par catégorie imposée par robots.txt, nous l'acceptons |
| Coût par session difficile à prévoir : le prix du jeton au-delà du forfait n'est pas publié clairement | 16/11 | Pire cas estimé à 0,25 € par estimation (6 boutiques) |
| Limite de sessions simultanées invisible : au-delà de 3 (offre gratuite), les sessions attendent dans la file de H sans le signaler, puis sont coupées sans avoir consommé un jeton | mesure du 19/11 : 10 sessions demandées, plusieurs « indisponibles » à 0 jeton après 92 s | File d'attente de notre côté, plafond `HAI_MAX_PARALLEL` réglé sur l'offre (3, puis 10 après le relèvement de la limite par H le 19/11) |
| La réponse structurée arrive parfois en texte JSON glissé dans la liste (`{"offers": ["[{…}]"]}`) au lieu d'objets | Easy Cash, iPad 9, 19/11 : offres valides perdues | Lecture tolérante (`coerce_answer`) |
| Quota visible seulement par le SDK (`quota.get_token_quota`), pas la limite de sessions ni l'offre en cours | 19/11 | Contrôle manuel avant la démo |

## Ce que nous demanderions à H
1. **La vidéo en direct** (ou une adresse de capture publique et temporaire) pour `web-surfer-flash`, afin d'éviter un relais par notre serveur.
2. **Les offres partielles** d'une session coupée au délai, renvoyées dans le résultat avec un statut « partiel ».
3. **Un outil d'envoi de fichier** en mode `user_device`, comme pour le navigateur cloud.
4. **Une erreur explicite** quand le pont local perd son onglet.
5. **Une grille de prix publique** au jeton ou à la session, et la limite de sessions simultanées écrite par offre.
6. **Un statut « en file d'attente »** distinct, et la limite de sessions de l'offre en cours exposée par l'API.
7. **Le respect strict du schéma de réponse** : jamais d'objets sérialisés en texte dans un champ de liste.
8. **La durée de conservation des captures** chez H affichée dans la console. Le SDK propose `delete_screenshot_after_min`, mais la valeur par défaut n'est pas documentée.

## Les chiffres (mesure sur 10 objets, #8, 19/11)
| | Matin (3 agents) | Après (10 agents, pages de départ) |
|---|---|---|
| Sessions | 44 | 33 (Troc.com en pause, Swappie limité à Apple) |
| Sessions abouties (prix ou absence de stock vérifiée) | 44/44 | 33/33 |
| Sessions avec au moins 1 prix | 20/44 | 21/33 |
| Durée médiane d'une estimation | 196 s | **91 s** |
| Jetons par estimation (moyenne) | 784 000 | 506 000 |
| Pic de sessions simultanées | 3 | 8 |

Par boutique (après) : Easy Cash 6/10 sessions à au moins 3 prix, Certideal 2/5, Gamecash 1/5, Cash Converters 1/10, Swappie 0/3. Cause principale des sessions sans prix, lue dans les notes des agents : l'objet n'est pas en stock (PS5, Xbox Series S, jeux récents, iPad 9).
