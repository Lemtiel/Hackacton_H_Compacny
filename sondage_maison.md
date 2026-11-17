# Sondage maison : temps pour fixer un prix et publier une annonce

Action n°5 de Specs.md (Tristan, lundi 16/11 au soir) : sonder 5 à 10 personnes sur le temps passé à fixer un prix et à publier une annonce.

**But :** obtenir un chiffre à nous, même petit, sur le temps que prend une revente aujourd'hui. Il complète les sondages OpinionWay et Ecologic cités dans Specs.md, qui viennent d'acteurs de la revente.

**Cible :** 18-35 ans, idéalement des gens qui ont déjà revendu du high-tech ou un jeu vidéo.

**Durée pour le sondé :** moins d'une minute, 8 questions à choix.

**Données :** anonyme. On ne demande ni nom, ni contact, ni l'objet vendu. Dans le tableau, chaque sondé devient R1, R2, etc.

---

## 1. Message à copier dans WhatsApp

> Salut ! Petit service pour mon hackathon 🙏 8 questions, 1 minute, anonyme.
> Réponds juste avec les lettres, par exemple : **1B 2A 3C 4B 5B 6A 7C 8A**
>
> **1. Ton âge ?**
> A. Moins de 18 ans  B. 18-24 ans  C. 25-35 ans  D. Plus de 35 ans
>
> **2. As-tu déjà revendu un objet high-tech ou un jeu vidéo d'occasion (téléphone, console, jeu, casque…) ?**
> A. Oui, dans les 12 derniers mois  B. Oui, il y a plus d'un an  C. Jamais (passe directement à la question 7)
>
> **3. Pour ta dernière vente, combien de temps as-tu passé à trouver le bon prix (chercher, comparer) ?**
> A. Moins de 5 min  B. 5 à 15 min  C. 15 à 30 min  D. 30 min à 1 h  E. Plus d'1 h
>
> **4. Et combien de temps pour rédiger et publier l'annonce (photos, texte, mise en ligne) ?**
> A. Moins de 5 min  B. 5 à 15 min  C. 15 à 30 min  D. 30 min à 1 h  E. Plus d'1 h
>
> **5. Combien de sites ou de sources as-tu consultés pour fixer ton prix ?**
> A. Aucun, au feeling  B. 1  C. 2 ou 3  D. 4 ou plus
>
> **6. Avec le recul, ton prix était…**
> A. Trop bas  B. À peu près juste  C. Trop haut  D. Je ne sais pas
>
> **7. Qu'est-ce qui te freine le plus pour revendre tes objets ?**
> A. Le temps que ça prend  B. Les démarches (annonce, envoi, échanges)  C. La peur de mal fixer le prix  D. Rien, je vends sans souci  E. Autre (dis-moi quoi)
>
> **8. Utiliserais-tu une appli gratuite qui, à partir d'une photo, te donne un prix indicatif en moins de 2 minutes et une annonce prête à copier ?**
> A. Oui, sûrement  B. Peut-être  C. Non
>
> Merci 🙌

**Conseils d'envoi :**
- L'envoyer en message individuel plutôt que dans un groupe : on obtient plus de réponses, et les sondés ne copient pas les réponses des autres.
- Viser 10 envois pour obtenir au moins 5 réponses. Relancer une fois le lendemain matin.
- Pour les personnes qui n'ont jamais revendu (réponse 2C), les questions 3 à 6 restent vides. C'est normal.

---

## 2. Version Google Forms (si tu préfères un lien)

Créer un formulaire sur forms.google.com, intitulé « Snap N Cash : revendre un objet, combien de temps ? ».

Description : « 8 questions, 1 minute. Sondage anonyme pour un projet étudiant (hackathon Eugenia). Aucune donnée personnelle n'est demandée. »

Paramètres :
- Désactiver la collecte des adresses e-mail (Paramètres > Réponses).
- Ne pas exiger de connexion Google.

Questions (toutes de type **Choix multiples**, une seule réponse) : reprendre les 8 questions et leurs options ci-dessus, sans les lettres.
- Question 2 : activer « Accéder à la section en fonction de la réponse ». Placer les questions 3 à 6 dans une section 2, et les questions 7 et 8 dans une section 3. La réponse « Jamais » mène directement à la section 3.
- Question 7 : activer l'option « Autre » pour le texte libre.
- Rendre obligatoires les questions 1, 2, 7 et 8.

Les réponses s'exportent en Google Sheets (onglet Réponses > icône Sheets). Il suffit ensuite de recopier les lettres dans le tableau `sondage_reponses.xlsx`.

---

## 3. Saisie des réponses

Fichier : `sondage_reponses.xlsx`
- Onglet **Saisie** : une ligne par sondé, une lettre par question (A, B, C…). Laisser vide si la question ne s'applique pas.
- Onglet **Synthèse** : se remplit tout seul. Il donne la répartition de chaque question, le temps médian pour fixer un prix, le temps médian pour publier, le temps total médian et les pourcentages clés.

**Calcul des temps :** chaque tranche est remplacée par son milieu (A = 2,5 min, B = 10 min, C = 22,5 min, D = 45 min, E = 75 min, choix arbitraire pour « plus d'1 h »). Le temps total d'un sondé est la somme des questions 3 et 4. On donne la médiane, moins sensible qu'une moyenne aux réponses extrêmes sur un si petit échantillon.

---

## 4. Ce qu'on pourra présenter (une fois les réponses reçues)

Formulations prêtes, à compléter avec les vrais chiffres :
- « Sur N personnes de notre entourage qui ont déjà revendu du high-tech, il a fallu en médiane X min pour fixer le prix et Y min pour publier l'annonce. »
- « Z % ont consulté au moins 2 sources avant de fixer leur prix. »
- « W % pensent avoir vendu trop bas. »
- « Frein le plus cité : … » (à comparer aux 29 % « manque de temps » d'OpinionWay.)
- « V sur N utiliseraient sûrement une appli qui donne un prix en moins de 2 minutes. »

**Limites à dire nous-mêmes avant qu'un juré le fasse :**
- Échantillon très petit (5 à 10 personnes) et tiré de notre entourage : c'est un signal, pas une statistique.
- Les temps sont déclarés de mémoire, pas chronométrés. La vraie mesure du temps gagné reste l'action n°9 (3 testeurs chronométrés jeudi, à la main puis avec l'app).
- La question 8 décrit notre produit de façon positive. Elle mesure un intérêt, pas un usage réel.

**Lien avec la suite :** le temps total médian sert de point de départ à l'action n°9. Si les sondés déclarent 30 minutes et que l'app répond en moins de 2 minutes, c'est l'écart que les testeurs de jeudi devront confirmer ou démentir.
