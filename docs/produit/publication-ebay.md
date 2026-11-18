# Publier sur eBay : où on en est, et le 1 clic

*Mis à jour le 18/11/2026. Source : retours de Jude sur le prototype, travail de Kevin (PR #25), documentation eBay Developers.*

## Aujourd'hui : publication assistée
L'utilisateur publie lui-même. L'app prépare ce qu'il faut et la page de mise en vente d'eBay s'ouvre vide.

| Étape | Ce que fait l'app |
|---|---|
| Titre et description | Rédigés par IA, modifiables, copiables en un geste |
| Prix | Prix conseillé, tiré des annonces eBay en cours (hors reconditionné) |
| Catégorie | Suggérée par l'API Taxonomy d'eBay, corrigée par nos règles (17 produits vérifiés) |
| Photos | Versions studio (objet détouré sur fond clair, objet non modifié) |
| Envoi vers eBay | Bouton « Partager photos et annonce » : une feuille de partage du téléphone avec les photos, le titre, la description et le prix |

**Ce qui n'est pas fait :** la page eBay ne se remplit pas toute seule. L'utilisateur colle le titre, choisit la catégorie, ajoute les photos et valide.

**Ce qui n'est pas testé :** la feuille de partage sur un vrai téléphone, et ce que l'app eBay en fait. Le bouton n'apparaît qu'en HTTPS (Vercel, Space) ou sur `localhost` : il est absent sur une adresse locale du type `http://192.168.x.x`.

## Pourquoi pas la publication automatique pour vendredi
- **Les Specs l'excluent** : « publication automatique des annonces » est hors périmètre, et l'usage doit rester sans compte.
- **Elle demande le compte eBay de l'utilisateur** : il se connecte à eBay et autorise l'app.
- **Elle remet en cause l'exemption eBay** obtenue le 18/11 (« je ne conserve aucune donnée eBay ») : avec un jeton utilisateur, il faudrait répondre aux notifications de suppression de compte.
- **Elle demande l'hébergement des photos** chez eBay, alors que la règle 5 interdit de conserver les photos côté serveur.
- **Elle demande un serveur public** pour recevoir le retour de connexion eBay.

## Le 1 clic : plan technique (suite du produit)
D'après la documentation de l'API Inventory d'eBay :
1. **Connexion eBay** de l'utilisateur, avec son accord (jeton utilisateur).
2. **Prérequis chez le vendeur** : les « business policies » activées (une politique d'expédition, de retour et de paiement, les trois sont obligatoires) et une adresse d'expédition.
3. **Photos** envoyées à eBay (au moins une), puis **création de l'objet** : titre, description, état, caractéristiques, quantité.
4. **Création de l'offre** : catégorie, prix, politiques du vendeur, adresse.
5. **Publication de l'offre** : eBay crée l'annonce.

**Estimation :** une à deux journées, avec un premier essai sur le **Sandbox** d'eBay (environnement de test, sans vraie annonce). Il faut modifier les Specs, déployer le serveur, et décider quoi faire des notifications de suppression de compte.

**Comment le présenter :** « Aujourd'hui, l'app prépare l'annonce et l'envoie vers eBay en un partage. Le 1 clic est la prochaine étape : le plan est prêt, les prérequis sont connus. » Ne pas montrer un faux « annonce créée » : un essai Sandbox se présente comme un Sandbox.
