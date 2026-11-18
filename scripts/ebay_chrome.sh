#!/usr/bin/env bash
# Ouvre un Chrome DÉDIÉ à eBay, que l'agent H peut piloter pour préparer un brouillon (démo sur cet ordinateur).
# 1. Lance ce script. 2. Dans la fenêtre qui s'ouvre, connecte-toi à eBay toi-même. 3. Laisse la fenêtre ouverte.
# Le profil est séparé de ton Chrome habituel (dossier ~/.snapncash/chrome-ebay) : l'agent ne voit que cette fenêtre.
# Ton mot de passe et tes cookies restent sur cet ordinateur.
set -euo pipefail
PROFILE="$HOME/.snapncash/chrome-ebay"
mkdir -p "$PROFILE"
open -na "Google Chrome" --args --remote-debugging-port=9222 --remote-allow-origins='*' \
  --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check "https://www.ebay.fr/"
echo "Chrome eBay ouvert. Connecte-toi à eBay dans cette fenêtre, puis laisse-la ouverte."
echo "Pour le serveur : EBAY_DRAFT_LOCAL=1 (voir README, « Brouillon eBay par un agent »)."
