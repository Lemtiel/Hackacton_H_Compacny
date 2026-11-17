# Simulation : de la photo à l'annonce publiée

Supports de démo pour le pitch. Ce sont des **imitations** de Leboncoin et de Vinted, marquées d'un bandeau « Simulation ». Rien n'a été publié sur les vrais sites.

| Fichier | Contenu |
|---|---|
| `snap-n-cash-vers-leboncoin.mp4` | Vidéo de 40 s en 1920×1080 : on prend la photo, l'objet est reconnu, on précise l'état, les agents comparent les boutiques, on obtient le verdict, puis l'annonce est rédigée. On bascule ensuite sur une page Leboncoin déjà remplie, on clique sur « Publier », et l'annonce est en ligne. |
| `leboncoin.html`, `leboncoin-*.png` | La fiche Leboncoin de l'annonce, version ordinateur et version mobile. |
| `vinted.html`, `vinted-*.png` | La fiche Vinted de la même annonce. |

## Ce qui est réel et ce qui est simulé
- **L'interface** est la vraie (branche `photo-et-recherche`), compilée et lancée en local.
- **Le serveur** est remplacé par des réponses enregistrées, car aucune clé H ni Hugging Face n'était disponible. Les mêmes routes et le même format sont utilisés, et le calcul des prix passe par le vrai `backend/pricing.py`.
- **Les prix des boutiques et le prix de 170 €** sont des exemples. La recherche est accélérée. eBay n'apparaît pas, car ses clés ne sont pas configurées.
- **Le texte de l'annonce** est écrit à la main en suivant les règles du prompt de `backend/listing.py`. Il ne vient pas du modèle.
- **Les photos** sont des illustrations dessinées.
- **La page Leboncoin pré-remplie, avec un seul clic sur « Publier »**, est une fonction envisagée, absente du code. Aujourd'hui, l'utilisateur copie l'annonce et la publie lui-même. Un remplissage automatique sur Leboncoin entre en tension avec la règle 1 de `CLAUDE.md` (aucun agent sur Leboncoin) et avec les conditions d'utilisation de Leboncoin. C'est à trancher par l'équipe avant de la présenter comme une fonction du produit.
