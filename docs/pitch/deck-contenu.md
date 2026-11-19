# Pitch deck : contenu des slides

*Brouillon du 19/11 pour vendredi 15h. 10 slides dans l'ordre imposé par le brief : problème, solution, démo, business model, go-to-market, architecture technique, limites et roadmap, coût de run. Pitch de 6 min, puis 4 min de questions. Chiffres mesurés le 19/11 sur 10 objets avec 10 agents simultanés, 33 sessions d'agent (#8, `mesures/mesure_*_2026-11-19_10h30.csv`).*

---

## 1. Titre
**Snap N Cash.** Ce qui dort chez vous a un prix.
Une photo, le bon prix, l'annonce prête.
Team 13 · snapncash.vercel.app

## 2. Le problème
- 86 % des Français gardent des objets inutilisés : 320 € par foyer.
- 17 % seulement les ont déjà revendus.
- Leurs freins : le temps (29 %), les démarches (20 %), la peur de se tromper de prix (16 %).
- 46 millions de téléphones dorment dans les tiroirs.

*Sources : OpinionWay pour Leboncoin, septembre 2025 ; Harris Interactive et Crédoc pour Ecologic, 2023.*

> Note orale : « Tout le monde a un vieux téléphone dans un tiroir. Personne ne sait combien il vaut, ni où le vendre. »

## 3. La solution
Une photo. Des agents H Company visitent en direct jusqu'à cinq boutiques d'occasion sans API. En moins de deux minutes, l'app répond :
- **où vendre** : soi-même (annonces eBay en cours) ou en magasin (rachat estimé à partir des prix boutique), avec le gain en euros ;
- **à quel prix** : fourchette et prix conseillé ;
- **l'annonce prête** : titre, description, caractéristiques, photos studio.

## 4. Démo
En direct sur snapncash.vercel.app : photo d'un iPhone, identification, écrans des agents côte à côte, verdict, annonce.
Puis, sur notre Mac : un agent H prépare le brouillon eBay dans le navigateur du vendeur.

Exemple mesuré le 19/11 en ligne, « iPhone 13 128 Go, bon état » :
- vendre soi-même : **261 €** (61 annonces eBay en cours) ;
- rachat estimé en magasin : **155 €** (11 prix boutique × 0,60) ;
- gain : **+106 €**, en 89 s.

> Plan B : la vidéo de 5 min si le réseau tombe.

## 5. Business model
- 3 estimations gratuites, puis **Bronze 4,99 €**, **Silver 14,99 €**, **Entreprise 149 € HT** par mois.
- À partir de l'an 2 : partenariat Vinted et Leboncoin, payé par annonce publiée puis par licence.
- Plus tard : commissions des boutiques de rachat.
- Scénario central : **22 k€** en an 1, **150 k€** en an 2, **375 k€** en an 3. Marge brute de 81 à 84 %.

## 6. Go-to-market
*Validé par Jude et Tristan le 19/11. Reprend les clients de docs/business-model (partie 3) et les hypothèses du tableur (🟡 = hypothèse).*

**Cible de départ : la personne qui n'a jamais osé vendre.** 83 % des Français n'ont jamais revendu. Nous commençons par le high-tech, là où l'écart de prix fait le plus peur : 46 millions de téléphones dorment dans les tiroirs.

| Phase | Qui | Comment | Objectif |
|---|---|---|---|
| **1. Lancement** (mois 1 à 6) | Particuliers | 3 estimations gratuites comme produit d'appel. Vidéos courtes « ce que vaut ton vieux téléphone » sur TikTok et Instagram, avec les écrans des agents. Temps forts : déménagements, rentrée, avant Noël. Écoles et campus. | 500 inscrits organiques le 1er mois 🟡, puis +12 % par mois |
| **2. Pros** (dès le mois 4) | Dépôts-ventes, ressourceries, petites enseignes | Démarchage direct avec l'espace `/pro`, qui classe les annonces par marge de revente | Offre Entreprise, 7 clients en fin d'an 1 🟡 |
| **3. Plateformes** (an 2) | Vinted, Leboncoin | Nous leur apportons des annonces bien remplies, d'objets qui dormaient. Payé par annonce publiée, puis licence | 26 800 € en an 2 🟡 |

**Chiffres clés :** 16 100 inscrits en an 1 (12 100 organiques, 4 000 par la publicité à 3 € l'inscrit 🟡) ; 4 % passent en Bronze 🟡.

> Note orale : « On ne va pas chercher les vendeurs Vinted. On va chercher les 83 % qui n'ont jamais revendu, avec trois estimations offertes. »

## 7. Architecture technique
```
Interface Next.js (Vercel) ──▶ Serveur FastAPI (Space Hugging Face)
                                   ├─▶ Hugging Face : gemma-4-31B-it (identification, annonce)
                                   ├─▶ H Company Agent API : web-surfer-flash, 1 session par boutique, en parallèle
                                   ├─▶ eBay API Browse (bloc séparé)
                                   └─▶ Bria RMBG-2.0 (photos studio)
```
- **Un agent par boutique, en parallèle** : aucune ligne de code propre à une boutique. Certideal et Swappie se sont ajoutés par une ligne de configuration.
- **Résultats envoyés site par site**, écrans des agents relayés en direct.
- **Passage à l'échelle sans recoder** : 10 agents simultanés depuis le 19/11 (limite relevée par H Company), 100 avec l'offre Startup.
- **Mesuré sur 10 objets, 33 sessions, 10 agents** : 100 % des sessions aboutissent à une réponse vérifiée (prix ou « pas en stock ») ; annonces eBay en cours pour 10 objets sur 10 ; **durée médiane 91 s** (toutes sous 100 s, objectif < 120 s).

## 8. Ce qu'on a refusé de faire
- Aucun agent sur Vinted, Leboncoin, Back Market et les autres sites dont les CGU l'interdisent.
- Aucun contournement d'anti-robot : Fnac a bloqué l'agent, Fnac est sortie de la liste.
- Aucune photo ni annonce conservée sur notre serveur.
- **Brouillon eBay par agent** : il fonctionne, mais seulement sur l'ordinateur du vendeur. Nous refusons de faire passer ses identifiants par notre serveur, et eBay interdit les agents IA sans son autorisation depuis février 2026.

## 9. Limites et roadmap
**Limites mesurées :** prix magasin complet (au moins 3 prix) pour 6 objets sur 10. Cause principale, lue dans les notes des agents : l'objet n'est pas en stock (PS5, iPad 9, jeux récents). Durée tenue : 91 s en médiane avec 10 agents (196 s à 3 agents le matin).
**Corrigé pendant la mesure :** prix eBay d'une PS5 faussé par des jeux (18 € → 580 €), Troc.com mis en pause (0 prix sur 10).
**Roadmap :**
1. Publication en un clic via le programme partenaire d'eBay (Listing API).
2. Partenariat Vinted et Leboncoin.
3. Plus de boutiques, ajoutées par configuration.

## 10. Coût de run
| Poste | Payé à l'usage (pire cas) | Forfait H Builder |
|---|---|---|
| Agents H, 6 boutiques | 0,285 $ | 0,023 $ |
| Hugging Face | 0,002 $ | 0,002 $ |
| **Par estimation** | **0,26 €** | **0,02 €** |
| Photos studio en plus | 0,018 $ par photo | 0,018 $ par photo |

Hébergement : Space Hugging Face à 0,03 $/h, Vercel Pro à 20 $/mois (le plan gratuit interdit l'usage commercial). À l'usage moyen, aucun abonnement ne perd d'argent sous 0,58 € par estimation.
Calcul prudent : 1 140 000 jetons par estimation (6 boutiques, 17/11), au taux de 1 € ≈ 1,10 $.
Mesuré le 19/11 : 506 000 jetons par estimation en moyenne (10 objets, 5 boutiques, départ sur la page de résultats ou du modèle).

---
*Prix indicatifs, comparaison non exhaustive. Estimation et annonce générées par IA.*
