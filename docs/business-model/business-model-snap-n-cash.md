# Snap N Cash : business model

Version 2 du 17/11/2026 (formule du partenariat choisie par l'équipe), préparée pour Tristan (CPO) et Stephen (CEO). Elle remplace le premier jet du matin.
Tous les calculs sont dans le tableur [snap-n-cash-projections.xlsx](snap-n-cash-projections.xlsx) : on change une hypothèse en bleu, tout se recalcule.

**Légende des chiffres :** ✅ mesuré par l'équipe (dépôt GitHub) · 📄 source publique citée · 🟡 hypothèse à valider · ❓ à sourcer avant le pitch

---

## 1. En bref

- **Le problème :** 86 % des Français gardent des objets inutilisés (320 € par foyer), mais 17 % seulement en ont déjà revendu. Ils citent le manque de temps, des démarches complexes et la peur de se tromper de prix 📄 (OpinionWay pour Leboncoin, 2025, dans Specs.md).
- **La solution :** une photo, un prix indicatif relevé sur plusieurs sites en moins de 2 minutes, et une annonce prête à publier.
- **Qui paie :** les 3 premières photos sont gratuites. Ensuite, trois abonnements : **Bronze** (4,99 €), **Silver** (14,99 €) et **Entreprise** (149 € HT). À partir de l'an 2, un **partenariat avec Vinted et Leboncoin** : d'abord payé par annonce publiée, puis par une licence. Et plus tard, des commissions des boutiques de rachat.
- **Pourquoi c'est rentable :** une estimation nous coûte **0,17 € dans le pire cas** et **0,02 € dans un forfait H**. Chaque abonnement reste rentable même dans le pire cas.
- **Projection, scénario central :** 22 000 € de chiffre d'affaires la première année, 150 000 € la deuxième, 375 000 € la troisième. Le résultat est positif en an 1 et en an 3, et négatif en an 2, l'année des embauches. Il faut lever environ 37 000 € 🟡.

---

## 2. Le marché

| Chiffre | Valeur | Source |
|---|---|---|
| Marché français de l'occasion | 14 milliards d'euros en 2024, doublé depuis 2019 | 📄 Xerfi, *Les marchés de l'occasion* |
| Volume vendu sur Vinted (Europe) | 10,8 milliards d'euros en 2025, +47 % | 📄 FashionUnited, avril 2026 |
| Objets qui dorment chez les Français | 19 objets et 320 € par foyer en moyenne | 📄 OpinionWay pour Leboncoin, 2025 |
| Téléphones dans les tiroirs | 46 millions | 📄 Harris Interactive et Crédoc pour Ecologic, 2023 |
| Part des Français qui ont déjà revendu | 17 % | 📄 OpinionWay pour Leboncoin, 2025 |

**Ce que ça veut dire :** il y a beaucoup d'objets qui ne sont pas encore en vente. Notre utilisateur n'est pas le vendeur Vinted aguerri, c'est la personne qui n'a jamais osé vendre. Pour Vinted et Leboncoin, c'est du stock en plus : c'est la base du partenariat (partie 6).

**Part de marché visée :** il manque la part du high-tech et des jeux vidéo dans l'occasion ❓. À sourcer pour la slide marché.

---

## 3. À qui ça sert, et ce que chacun y gagne

| Client | Son problème | Ce qu'on lui apporte | Il paie ? |
|---|---|---|---|
| **Particulier occasionnel** | Ne sait pas quel prix mettre, n'a pas le temps | Un prix en 2 min, une annonce prête | 3 photos gratuites, puis Bronze |
| **Vendeur régulier** (Vinted, Leboncoin, eBay) | Passe du temps à comparer les prix de chaque objet | 50 estimations par mois, publication rapide | Silver |
| **Pro** (dépôt-vente, brocanteur, ressourcerie, petite enseigne) | Fixe des dizaines de prix par jour, à la main | Estimation en volume, plusieurs comptes, export | Entreprise |
| **Plateformes** (Vinted, Leboncoin) | Veulent plus d'annonces, bien rédigées, au bon prix (elles se vendent plus vite) | Des annonces de qualité, d'objets qui dormaient | Par annonce publiée, puis licence |
| **Boutiques de rachat** (Easy Cash, Cash Converters...) | Veulent des clients qui viennent vendre | Des clients qui connaissent déjà l'estimation | Commission (plus tard) |

---

## 4. L'offre et les prix

| | **Gratuit** | **Bronze** | **Silver** | **Entreprise** |
|---|---|---|---|---|
| Prix | 0 € | **4,99 € TTC / mois** | **14,99 € TTC / mois** | **149 € HT / mois** |
| Estimations | **3 au total** (à vie) | 10 par mois | 50 par mois | 500 par mois, puis sur devis |
| Prix « vendre seul » (eBay) et « revendre en magasin » | ✓ | ✓ | ✓ | ✓ |
| Annonce générée (Vinted, Leboncoin, eBay, texte) | ✓ | ✓ | ✓ | ✓ |
| Historique (dans le navigateur) | ✓ | ✓ | ✓ | ✓ |
| Publication en un clic sur Vinted et Leboncoin | | | ✓ (avec le partenariat) | ✓ (avec le partenariat) |
| Alerte quand le prix d'un objet change | | | ✓ | ✓ |
| Plusieurs comptes, export du stock, facture | | | | ✓ |
| Accès par API | | | | ✓ |
| Engagement | | Sans | Sans | Annuel possible |

Les prix ont été **validés par l'équipe** le 17/11. La partie 5 bis explique comment les défendre devant le jury.

**Pourquoi 3 photos gratuites et pas plus :** chaque estimation lance de vrais agents H et coûte de vrais tokens. Le calcul de la partie 5 montre que les 3 photos offertes sont remboursées 2,5 fois par les abonnés Bronze qu'elles font venir, même dans le pire cas de coût.

**Pourquoi Bronze est mensuel sans engagement :** un particulier vend par vagues (un déménagement, un tri de printemps). Il s'abonne un ou deux mois puis arrête. Le modèle prévoit 15 % de résiliations par mois 🟡.

**Point de départ de l'offre Entreprise :** l'espace revendeurs en cours de construction (branche `revendeurs`, cahier des charges `docs/revendeurs.md`) classe déjà les annonces par marge possible. Les fonctions Entreprise (plusieurs comptes, export, API) s'ajouteront dessus.

**À prévoir côté produit :** compter les 3 photos gratuites impose un compte (une adresse e-mail). Ce n'est pas contraire à la règle 5 de CLAUDE.md (photos, annonces relevées et pseudonymes de vendeurs non conservés), mais il faudra une politique de confidentialité conforme au RGPD.

---

## 5. Combien coûte une estimation, et ce que rapporte chaque abonnement

### Le coût de revient ✅
Les 14 sessions d'agent du 16/11 (`mesures/agent_runs.csv`) consomment en moyenne **162 000 tokens par site**, soit **650 000 à 870 000 tokens par estimation** sur 4 boutiques.

| Poste | Pire cas (payé à l'usage) | Dans un forfait H Builder |
|---|---|---|
| Agents H | 0,19 $ | 0,015 $ |
| Hugging Face (identification + annonce) | 0,002 $ | 0,002 $ |
| Hébergement variable | 0,001 € | 0,001 € |
| **Total par estimation** | **0,17 €** | **0,02 €** |

Sources : forfaits et prix des modèles sur la documentation H 📄. Le pire cas suppose le modèle Holo le plus cher, car on ne sait pas encore lequel fait tourner l'agent `web-surfer-flash` ❓.

**Les forfaits H 📄 :** Free (0 $, 60 millions de tokens, 3 agents en même temps), Builder (20 $ par mois, 1 milliard, 10 agents), Startup (200 $ par mois, 10 milliards, 100 agents). La limite de 3 agents en parallèle relevée le 16/11 est celle du forfait gratuit : on passe à l'échelle en changeant de forfait, sans recoder.

### Ce que rapporte un abonné par mois

| | Bronze | Silver | Entreprise |
|---|---|---|---|
| Prix HT encaissé | 4,16 € | 12,49 € | 149,00 € |
| Frais de paiement (Stripe, 1,5 % + 0,25 €) | 0,33 € | 0,48 € | 2,93 € |
| Estimations utilisées en moyenne | 4 | 20 | 250 |
| **Marge brute, pire cas** | **3,17 € (76 %)** | **8,69 € (70 %)** | **104,54 € (70 %)** |
| Marge brute, pire cas, quota entièrement utilisé | 2,17 € | 3,71 € | 63,01 € |
| **Marge brute, dans un forfait H** | **3,77 € (91 %)** | **11,70 € (94 %)** | **142,12 € (95 %)** |

Les pourcentages sont calculés sur le prix HT encaissé.

Aucun abonnement ne perd d'argent, même si l'abonné utilise tout son quota au tarif le plus cher.

### Le retour sur les photos gratuites
- Un inscrit gratuit utilise en moyenne 2 photos 🟡. Pire cas : il nous coûte **0,33 €**.
- Si 4 % des inscrits passent en Bronze 🟡, il faut 25 inscrits gratuits pour 1 abonné : **8,31 €** de photos offertes.
- Un abonné Bronze reste en moyenne 6,7 mois et rapporte **21,13 €** de marge sur cette durée.
- **Résultat : 1 € de photos offertes rapporte 2,5 € de marge en Bronze, et 3,3 € en Silver.** Dans un forfait H, le coût des photos gratuites devient négligeable.

Le taux de passage de 4 % est prudent : sur 200 produits freemium, 29 % convertissent entre 2,5 et 7,5 % 📄 (Growth Unhinged, *Free-to-paid conversion report*).

---

## 5 bis. Comment défendre nos prix

### D'abord, de quelle marge on parle
La **marge brute** est ce qui reste du prix une fois payé ce que coûte **chaque estimation** : les tokens des agents H, les modèles Hugging Face, l'hébergement et les frais de carte bancaire. Elle ne compte **ni les salaires, ni le marketing, ni les frais fixes**.

| Scénario central | Année 1 | Année 3 |
|---|---|---|
| Chiffre d'affaires | 22 100 € | 375 200 € |
| Marge brute | 18 000 € (81 %) | 331 500 € (88 %) |
| **Résultat après salaires, marketing et frais fixes** | **1 200 € (5 %)** | **14 700 € (4 %)** |

**La phrase à dire au jury :** « Notre marge brute est élevée parce que le coût d'une estimation est faible et mesuré. Notre résultat, lui, reste modeste : 5 % la première année, 4 % la troisième. »

### Sur quoi repose le coût, et ce qui est solide
- **Solide ✅ :** les tokens par site viennent de nos 14 sessions réelles du 16/11 (`mesures/agent_runs.csv`), et les prix par token et les forfaits viennent de la documentation publique de H 📄.
- **Prudent :** on retient le modèle Holo le plus cher, plus 20 % de dépassement, sans aucune réutilisation des prix. C'est le pire cas.
- **Fragile 🟡 :** 14 sessions, 3 objets, un seul jour de test. Le nombre moyen d'estimations par abonné est une hypothèse. Le modèle exact de l'agent H est inconnu ❓.

### Le vrai argument : la marge de sécurité
Plutôt que de défendre un pourcentage, on peut montrer **jusqu'où le coût peut monter avant qu'un abonnement perde de l'argent** :

| | Bronze | Silver | Entreprise |
|---|---|---|---|
| Coût maximal par estimation (usage moyen) | 0,96 € | 0,60 € | 0,58 € |
| Coût mesuré dans le pire cas | 0,17 € | 0,17 € | 0,17 € |
| **Marge de sécurité** | **coût × 5,8** | **coût × 3,6** | **coût × 3,5** |
| Marge de sécurité si tout le quota est utilisé | × 2,3 | × 1,4 | × 1,8 |

**La phrase à dire :** « Même si nos agents consommaient 3,5 fois plus de tokens que mesuré, aucun abonnement ne perdrait d'argent. » Le point faible est Silver quand tout le quota est utilisé (marge × 1,4) : si les tests montrent un coût plus élevé, on baisse son quota de 50 à 40 estimations.

### Pourquoi ces prix sont justes pour le client
On ne fixe pas le prix à partir de notre coût, mais à partir de **ce que le client y gagne** :
- **Bronze (4,99 €) :** le jour du test, la Nintendo Switch se vendait entre 145 et 200 € en boutique, avec une médiane de 166 € ✅ (JOURNAL.md). Vendre 15 % trop bas fait perdre environ 25 €, soit **5 mois d'abonnement**. Et 16 % des Français citent la peur de se tromper de prix comme frein 📄.
- **Silver (14,99 €) :** un vendeur régulier fait 20 estimations par mois. S'il gagne 10 minutes à chaque fois 🟡, c'est **plus de 3 heures par mois** pour 15 €. Le sondage maison (temps passé à fixer un prix) donnera le vrai chiffre.
- **Entreprise (149 € HT) :** 250 estimations par mois. À 5 minutes gagnées par objet 🟡, c'est **21 heures de travail**, soit environ 250 € au SMIC ❓ (montant 2026 à vérifier). Le prix est donc inférieur au temps économisé, avant même de compter les ventes au bon prix.
- **Points de comparaison :** il existe déjà des outils payants pour les revendeurs Vinted (VintedCRM, Margeo) ❓. Relever leurs prix permettrait de montrer que nous sommes dans la même gamme.

---

## 6. Les partenariats Vinted et Leboncoin

### Pourquoi c'est l'axe clé
1. **Ça règle notre problème de CGU.** Aujourd'hui, les conditions d'utilisation de Vinted et Leboncoin interdisent les robots : nos agents n'y vont pas (règle 1 de CLAUDE.md), et l'application se contente d'ouvrir une recherche chez l'utilisateur. Un partenariat officiel nous donnerait un **accès autorisé** à leurs prix (par API, pas par des agents) et la **publication directe** de l'annonce. C'est la principale amélioration de produit possible : ce sont les deux plus gros sites d'occasion en France.
2. **Ça devient une source de revenus.** D'abord une rémunération par annonce publiée, puis une licence (partie 6 bis).

### Ce qu'on leur apporte
- **Des annonces en plus :** des objets qui dormaient dans les tiroirs, mis en vente par des gens qui n'avaient jamais vendu.
- **Des annonces de meilleure qualité :** bonne photo, bon titre, bon prix. Elles se vendent plus vite, donc la plateforme encaisse ses frais plus vite. Leboncoin dit lui-même que ses annonces rédigées avec l'IA sont « 20 % plus efficaces » 📄 (Journal de l'Automobile, mai 2025).
- **Un prix neutre :** on compare plusieurs sources (eBay, boutiques de rachat), ce qu'aucune plateforme ne peut faire pour elle-même.

### Comment on est payés
Formule choisie par l'équipe le 17/11 : **par annonce publiée pendant un an, puis une licence**. Le détail, les chiffres et les risques sont dans la partie 6 bis.

### Le calendrier réaliste
- **Maintenant (prototype) :** aucun accès à Vinted ni à Leboncoin, l'utilisateur publie lui-même. C'est conforme aux CGU.
- **Mois 1 à 12 :** on accumule des preuves (nombre d'estimations, taux de publication, précision du prix) pour pouvoir se présenter.
- **Mois 13 (scénario central) :** première plateforme signée, payée par annonce publiée. Prudent : mois 25. Ambitieux : mois 10.
- **Mois 25 :** la première plateforme passe en licence, la seconde est signée par annonce publiée.
- **Mois 37 (après l'horizon du tableur) :** la seconde plateforme passe en licence.

### Les risques à dire honnêtement
- **Ils peuvent le faire eux-mêmes.** Leboncoin génère déjà des annonces par IA pour les voitures et les biens de consommation 📄. Notre réponse : la comparaison neutre entre plusieurs sites et les boutiques de rachat, qu'une plateforme ne fera jamais pour ses concurrents.
- **Aucun programme partenaire public n'existe** pour notre usage ❓. Leboncoin propose des solutions de diffusion aux pros de l'immobilier 📄 (MySweetImmo, sept. 2024) : c'est un précédent à citer, pas une garantie.
- **Transparence obligatoire.** Dès qu'un site nous paie, la page « Comment ça marche » doit le dire, et l'ordre des résultats ne doit pas en dépendre (Code de la consommation, art. L111-7 ❓ à faire vérifier). Aujourd'hui, la page affirme qu'« aucun site ne nous paie » : il faudra la modifier le jour où un partenariat est signé.

### Les boutiques de rachat (même logique, plus tard)
Le bloc « Revendre en magasin » envoie déjà des vendeurs vers Easy Cash, Cash Converters, etc. Une commission d'apport d'affaires de 2 € par rachat est prévue à partir du mois 19 🟡. Aucune boutique n'a de programme connu ❓ : il faut les démarcher.

---

## 6 bis. La formule du partenariat : par annonce publiée, puis licence

Choix de l'équipe le 17/11. C'est la formule retenue dans les projections (cellule jaune « Formule de rémunération » = 4 dans le tableur).

### Phase 1 : par annonce publiée, pendant 12 mois
- **Le principe :** la plateforme nous paie **0,30 € HT** pour chaque annonce publiée chez elle depuis Snap N Cash 🟡.
- **Pourquoi 0,30 € :** c'est le milieu de la fourchette 0,20 à 0,50 €. Si 60 % des annonces se vendent, la plateforme paie environ 0,50 € par vente, soit à peu près 11 % des 4,70 € de frais que Vinted encaisse sur un objet de 80 € 📄. Elle reste largement gagnante.
- **Pourquoi c'est facile à signer :** la plateforme ne paie que pour des annonces réelles, sans engagement de départ. Pendant un an, elle mesure elle-même la valeur de l'outil : nombre d'annonces, part vendue, vitesse de vente, prix obtenu.
- **Le risque à traiter :** payer à l'annonce pousse à publier n'importe quoi. Pour rassurer la plateforme, on ne compte que les annonces restées en ligne au moins 7 jours et non signalées 🟡.

### Phase 2 : licence, au bout de 12 mois
- **La date :** 12 mois après la signature de chaque plateforme, soit **le mois 25** pour la première dans le scénario central. Un an couvre toutes les saisons de la revente (rentrée, Noël, tri de printemps) et donne assez de mesures pour fixer le prix de la licence. C'est aussi la durée habituelle d'un contrat pilote 🟡.
- **Le principe :** la plateforme intègre notre moteur d'estimation chez elle, pour ses propres utilisateurs, contre un forfait. Le tableur retient **4 000 € HT par mois et par plateforme**, 15 000 estimations incluses. Ces estimations nous coûtent environ 750 € par mois 🟡.
- **Pourquoi c'est mieux que la phase 1 :** au mois 24 du scénario central, la phase 1 rapporte environ 3 100 € par mois. La licence rapporte 4 000 €, garantis.

### Le risque de la licence : perdre la comparaison neutre, et comment l'éviter
Intégré chez Vinted, notre moteur ne montrera jamais les prix de Leboncoin. Or la comparaison neutre est notre principal argument (partie 6). La réponse est de séparer deux produits :

| | **Application Snap N Cash** | **Moteur sous licence, chez la plateforme** |
|---|---|---|
| Pour qui | Tout le monde | Les utilisateurs de la plateforme |
| Sources de prix | Toutes : eBay, boutiques de rachat, plateformes partenaires | Les prix de la plateforme et des boutiques de rachat 🟡 |
| Classement | Neutre, ne dépend d'aucun paiement | Défini avec la plateforme |
| Marque | Snap N Cash | Celle de la plateforme |

Trois clauses à mettre dans chaque contrat de licence :
1. **Non exclusive :** on peut signer avec Vinted et avec Leboncoin.
2. **L'application reste indépendante :** la licence ne donne aucun droit sur ce que Snap N Cash affiche ni sur l'ordre des résultats.
3. **Transparence :** la page « Comment ça marche » dit quelles plateformes nous rémunèrent, dès la phase 1 (Code de la consommation, art. L111-7 ❓ à faire vérifier).

Les prix eBay restent hors du moteur sous licence : les conditions de l'API eBay pour un usage chez un concurrent sont à vérifier ❓, et la règle 4 de CLAUDE.md les garde déjà à part.

### L'impact chiffré
Revenu net du partenariat sur 3 ans (coût des estimations pour la plateforme déduit) :

| Scénario | **Formule choisie** | Pour comparaison : par annonce vendue |
|---|---|---|
| Prudent (signature au mois 25) | **29 600 €** | 29 600 € |
| Central (signature au mois 13) | **94 900 €** | 170 100 € |
| Ambitieux (signature au mois 10) | **156 700 €** | 587 200 € |

**À dire honnêtement :** la formule choisie rapporte moins que la commission par vente quand Snap N Cash grandit vite, parce que la licence est un forfait. En échange, le revenu est garanti et le contrat est plus simple à signer.

**Le levier :** le prix de la licence. Les mesures de la phase 1 serviront à le négocier. Chaque tranche de 1 000 € par mois ajoute 12 000 € au résultat de l'an 3 du scénario central. Une licence à 8 000 € par mois ramènerait ce résultat au niveau de la commission par vente (environ 63 000 €).

---

## 7. Projections sur 3 ans

Hypothèses principales (toutes modifiables dans le tableur) : 500 inscrits organiques le premier mois, puis une croissance mensuelle de 12 % en an 1, 5 % en an 2 et 3 % en an 3 ; publicité à 3 € par inscrit ❓ ; fondateurs non payés en an 1, puis 2 salaires en an 2 et 4 en an 3 ; réutilisation des prix déjà relevés dans les 24 h pour 20 à 50 % des estimations 🟡.

### Scénario central

| | Année 1 | Année 2 | Année 3 |
|---|---|---|---|
| Nouveaux inscrits | 16 100 | 45 100 | 77 700 |
| Abonnés Bronze en fin d'année | 354 | 959 | 1 664 |
| Abonnés Silver en fin d'année | 115 | 348 | 648 |
| Clients Entreprise en fin d'année | 7 | 37 | 94 |
| Abonnements | 22 100 € | 115 300 € | 271 400 € |
| Partenariat Vinted / Leboncoin | 0 € | 26 800 € | 77 100 € |
| Commissions des boutiques de rachat | 0 € | 7 400 € | 26 600 € |
| **Chiffre d'affaires** | **22 100 €** | **149 500 €** | **375 200 €** |
| Coût technique (H, Hugging Face, hébergement, estimations sous licence) | 3 000 € | 6 900 € | 32 800 € |
| Marge brute | 18 000 € (81 %) | 137 500 € (92 %) | 331 500 € (88 %) |
| Marketing, frais fixes, salaires | 16 800 € | 160 800 € | 316 800 € |
| **Résultat d'exploitation** | **+1 200 €** | **−23 300 €** | **+14 700 €** |

Le besoin de trésorerie le plus fort est d'environ **37 000 €**, au mois 29 : les salaires démarrent en an 2, alors que le partenariat ne rapporte encore que la phase 1.

### Les trois scénarios

| | Prudent | Central | Ambitieux |
|---|---|---|---|
| Croissance organique an 1 | 8 % par mois | 12 % | 18 % |
| Passage en Bronze / Silver | 2 % / 0,5 % | 4 % / 1 % | 6 % / 2 % |
| Signature de la 1re plateforme | mois 25 | mois 13 | mois 10 |
| Passage en licence | après l'horizon | mois 25 | mois 22 |
| Chiffre d'affaires an 3 | 158 000 € | 375 000 € | 844 000 € |
| Résultat d'exploitation an 3 | −167 000 € | +15 000 € | +401 000 € |
| Besoin de financement sur 3 ans | 290 000 € | 37 000 € | 3 000 € |

**À retenir :** le modèle tient si le partenariat arrive. Sans lui (scénario prudent), il ne faut pas embaucher en an 2 : les abonnements seuls couvrent les coûts techniques et le marketing, pas une équipe. Dans le scénario central, la levée de fonds à prévoir est d'environ 40 000 €.

---

## 8. Les risques et nos réponses

| Risque | Notre réponse |
|---|---|
| H Company n'autorise pas l'usage commercial de son API | Question posée aux mentors (Specs §9.4) ❓. Sans accord, pas de lancement commercial |
| Le prix des tokens H change | Le pire cas (0,17 € par estimation) laisse déjà au moins 70 % de marge brute sur chaque abonnement |
| Un site bloque nos agents | Il sort de la liste (règle 2). Il reste eBay et les autres boutiques, puis les partenariats |
| Les estimations sont fausses | Objectif mesuré sur 30 objets : écart médian ≤ 15 % avec le prix réellement vendu (Specs). À publier dans le pitch |
| Les particuliers ne paient pas | Les pros (Entreprise), le partenariat et les boutiques pèsent 61 % du chiffre d'affaires en an 3 (scénario central) |
| Vinted ou Leboncoin copient l'idée | Notre force : la comparaison neutre entre plusieurs sites et les boutiques de rachat |
| La licence nous enferme chez une plateforme | Licence non exclusive, application Snap N Cash indépendante (partie 6 bis) |

---

## 9. Questions pour Tristan et Stephen

1. ~~Les prix des paliers~~ : validés par l'équipe le 17/11 (4,99 €, 14,99 € TTC, 149 € HT).
2. ~~La cible Entreprise~~ : validée le 17/11, dépôts-vente et brocanteurs d'abord.
3. ~~L'horizon~~ : validé le 17/11, 3 ans.
4. ~~Les salaires~~ : validé le 17/11, fondateurs non payés en an 1.
5. ~~La formule du partenariat~~ : validée le 17/11, par annonce publiée pendant 12 mois, puis licence (partie 6 bis).

## 10. Chiffres à sourcer avant vendredi
- Le modèle qui fait tourner `web-surfer-flash` et son prix (question à H).
- L'usage commercial de l'API H (Specs §9.4).
- La part du high-tech et des jeux vidéo dans le marché de l'occasion.
- Le coût d'un inscrit obtenu par publicité (3 € retenus).
- Le taux de vente des annonces sur Vinted et Leboncoin.
- Un ordre de grandeur pour le prix d'une licence logicielle auprès d'une grande plateforme (question aux mentors).
- Les conditions de l'API eBay pour un usage chez une autre plateforme.
- L'article L111-7 du Code de la consommation appliqué à notre cas.
- Les conditions de Vercel Hobby pour un usage commercial.
- Un ou deux appels à des brocanteurs pour tester le prix Entreprise.

## Sources
- Mesures de l'équipe : `mesures/agent_runs.csv`, `JOURNAL.md`, `Specs.md` du dépôt [Lemtiel/Hackacton_H_Compacny](https://github.com/Lemtiel/Hackacton_H_Compacny) (branches `main` et `photo-et-recherche`).
- Forfaits Agent API H : [hub.hcompany.ai/computer-use-agents/billing](https://hub.hcompany.ai/computer-use-agents/billing)
- Prix des modèles Holo : [hub.hcompany.ai/models.md](https://hub.hcompany.ai/models.md)
- Marché de l'occasion : [Xerfi, Les marchés de l'occasion](https://www.xerfi.com/presentationetude/Les-marches-de-l-occasion_7DIS72)
- Résultats Vinted 2025 : [FashionUnited, avril 2026](https://fashionunited.fr/actualite/business/vinted-atteint-1-1-milliard-deuros-de-chiffre-daffaires-en-2025-et-assume-une-baisse-strategique-de-ses-benefices/2026040941303)
- Frais de protection acheteurs Vinted : [Fripio, 2026](https://fripio.app/blog/frais-protection-acheteur-vinted-2026)
- IA de Leboncoin pour les annonces : [Journal de l'Automobile, mai 2025](https://journalauto.com/services/leboncoin-adresse-lia-generative-aux-revendeurs-particuliers/)
- Solutions de diffusion Leboncoin pour l'immobilier : [MySweetImmo, sept. 2024](https://www.mysweetimmo.com/2024/09/23/pros-de-limmo-leboncoin-propose-4-nouvelles-solutions-de-diffusion-dannonces/)
- Conversion freemium : [Growth Unhinged, Free-to-paid conversion report](https://www.growthunhinged.com/p/free-to-paid-conversion-report)
