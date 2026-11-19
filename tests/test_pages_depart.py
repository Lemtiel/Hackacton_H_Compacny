"""Page de départ des agents (mesure du 19/11), sans réseau. Lancer : .venv/bin/python tests/test_pages_depart.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.sites import start_url  # noqa: E402

total = failed = 0


def check(label: str, ok: bool) -> None:
    global total, failed
    total += 1
    failed += not ok
    print(("OK   " if ok else "ÉCHEC ") + label)


def ends(site, cat, product, suffix):
    url = start_url(site, cat, product)
    check(f"{site} « {product} » → …{suffix} (obtenu : {url})", url.endswith(suffix))


ends("easycash", "smartphone", "Apple iPhone 13 128 Go", "apple/iphone-13-reconditionne")
ends("easycash", "smartphone", "Apple iPhone 13 Pro 256 Go", "apple/iphone-13-pro-reconditionne")
ends("easycash", "smartphone", "Samsung Galaxy S21 128 Go", "samsung/galaxy-s21-5g-s21-5g-plus-s21-5g-ultra")
ends("easycash", "smartphone", "Samsung Galaxy S21 Ultra", "samsung/galaxy-s21-ultra")
ends("easycash", "console", "Nintendo Switch", "nintendo/switch")
ends("easycash", "console", "Nintendo Switch OLED", "nintendo/switch-oled")
ends("easycash", "console", "Sony PlayStation 5", "sony/ps5")
ends("easycash", "console", "Microsoft Xbox Series S", "microsoft/xbox-series-s")
ends("easycash", "jeu_video", "EA Sports FC 25 PS5", "jeux-video/sony/ps5")
ends("easycash", "jeu_video", "Zelda Tears of the Kingdom", "bons-plans.easycash.fr/jeux-video")  # pas de plateforme : catégorie
ends("easycash", "informatique", "Apple MacBook Air M1 256 Go", "macbook/macbook-air-occasion-reconditionne")
ends("certideal", "smartphone", "Apple iPhone 12 64 Go", "iphone-12-reconditionne-261")
ends("certideal", "tablette", "Apple iPad 9 64 Go", "ipad-349")
ends("certideal", "informatique", "Apple MacBook Pro M1", "macbook-pro-149")
ends("easycash", "smartphone", "Google Pixel 7", "telephonie/smartphones/google")
ends("easycash", "smartphone", "Fairphone 5", "bons-plans.easycash.fr/telephonie/smartphones")  # inconnu : catégorie
ends("cashconverters", "smartphone", "Apple iPhone 13 128 Go", "/p/search?q=Apple+iPhone+13")
ends("gamecash", "console", "Nintendo Switch", "recherche.html?h=1&searchTxt=Nintendo+Switch")
from agents.sites import PAUSED_SITES, sites_for  # noqa: E402

check("Troc.com en pause : aucun agent lancé", "troc" not in sites_for("console", "Sony PlayStation 5") and "troc" in PAUSED_SITES)
check("Swappie lancé pour un iPhone", "swappie" in sites_for("smartphone", "Apple iPhone 13 128 Go"))
check("Swappie pas lancé pour un Galaxy", "swappie" not in sites_for("smartphone", "Samsung Galaxy S21 128 Go"))
check("sans nom d'objet : liste par catégorie inchangée", "swappie" in sites_for("smartphone"))
ends("swappie", "smartphone", "Apple iPhone 13", "swappie.com/fr/")

print(f"{total - failed}/{total} vérifications correctes")
sys.exit(1 if failed else 0)
