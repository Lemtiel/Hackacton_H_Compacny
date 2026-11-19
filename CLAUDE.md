# CLAUDE.md : Snap N Cash

## Sources de vérité
- **[Specs.md](Specs.md)** : ce qu'on construit, le périmètre, les critères de succès. En cas de doute ou de contradiction, s'arrêter et demander.
- **[CONTEXT.md](CONTEXT.md)** : le hackathon, les échéances, l'équipe, le cadre légal.
- **[JOURNAL.md](JOURNAL.md)** : les décisions prises et pourquoi. Ajouter une entrée datée après chaque décision importante.

## Façon de travailler avec Jude
- Répondre en français, de façon concise et directe.
- Annoncer chaque phase d'implémentation et attendre le feu vert avant de coder.
- Proposer chaque modèle Hugging Face avec sa justification (précision, coût, temps), puis attendre la validation de Jude avant de l'utiliser.
- Signaler clairement ce qui a été testé et ce qui ne l'a pas été.

## Règles non négociables
1. **Sources de prix :** seulement eBay (API Browse) et les agents H sur Easy Cash, Gamecash, Cash Converters, Certideal et Swappie (Troc.com autorisé mais en pause depuis le 19/11 : 0 prix sur 10 objets). Aucun agent ni scraping sur Vinted, Leboncoin, Cdiscount, TikTok Shop, Back Market, Label Emmaüs, Largo, Recommerce, Smaaart, Refurbed (CGU qui l'interdisent).
2. **Aucun contournement d'anti-robot.** Un site qui bloque l'agent sort de la liste. Les CGU de H Company (§5.2, §5.3) l'exigent aussi.
3. **Easy Cash :** navigation par les pages de catégorie, jamais par le moteur de recherche (bloqué par le robots.txt).
4. **eBay :** résultats dans un bloc séparé, jamais mélangés aux autres sites. Les données eBay ne passent pas dans un modèle de texte génératif.
5. **Données :** aucune photo, annonce relevée ou pseudonyme de vendeur conservé côté serveur. L'historique reste dans le navigateur.
6. **Photos :** refuser toute photo où un visage est détecté.
7. **Secrets :** clés API dans `.env` uniquement. Ne jamais les committer : le dépôt est public.
8. **Affichage :** les prix sont indicatifs, la mention « généré par IA » est visible, et la page « Comment ça marche » liste les sites consultés. Ne jamais écrire « tous les sites ».
9. **Captures des agents** : montrées en direct pendant la recherche (mode démo, actif par défaut depuis le 19/11, interrupteur dans Réglages). Aucune capture conservée, ni sur le serveur ni dans le navigateur. Les résultats affichent seulement le prix et le lien.

## Architecture
- Interface : Next.js générée avec v0, hébergée sur Vercel.
- Serveur : Python (FastAPI) dans un Space Hugging Face, résultats envoyés site par site.
- Agents : Agent API de H Company, une session par site, en parallèle, 90 s maximum par site.

## Mesures à tenir
Chaque test d'agent alimente le journal de l'Agent API : site, résultat, durée, tokens consommés, ce qui a marché ou cassé. Ces chiffres servent au pitch et aux retours à H Company.

## Fin de projet
Avant la livraison de vendredi : garde-fou de conformité en mode complet, puis revue hostile.
