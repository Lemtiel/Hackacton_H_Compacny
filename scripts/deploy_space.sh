#!/usr/bin/env bash
# Envoie le serveur sur un Space Hugging Face (SDK Docker) déjà créé.
# Usage : scripts/deploy_space.sh <compte>/<nom-du-space>      ex. Judebkn95/snapncash
# Git demande un identifiant (ton compte Hugging Face) puis un mot de passe : colle un JETON AVEC DROIT D'ÉCRITURE
# (huggingface.co/settings/tokens). Aucun secret n'est envoyé par ce script : les clés se règlent dans les paramètres du Space.
set -euo pipefail
SPACE="${1:?Usage : scripts/deploy_space.sh <compte>/<nom-du-space>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cp -R "$ROOT/backend" "$ROOT/agents" "$ROOT/requirements.txt" "$TMP/"
cp "$ROOT/deploy/space/Dockerfile" "$ROOT/deploy/space/README.md" "$TMP/"
rm -rf "$TMP/backend/models"
find "$TMP" -name "__pycache__" -type d -prune -exec rm -rf {} +

cd "$TMP"
git init -q -b main
git add -A
git -c user.name="deploy" -c user.email="deploy@snapncash.local" commit -q -m "Déploiement du serveur Snap N Cash"
echo "Envoi vers https://huggingface.co/spaces/$SPACE ..."
git push --force "https://huggingface.co/spaces/$SPACE" main
echo "Envoyé. Le Space construit l'image (3 à 6 minutes). Adresse de l'API : https://${SPACE%%/*}-${SPACE##*/}.hf.space"
