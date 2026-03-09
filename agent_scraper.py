import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scraper_offres(url_recherche):
    print(f" Lancement de l'Agent Scraper sur : {url_recherche}")
    
    # On utilise "async with" pour s'assurer que le navigateur se ferme bien à la fin
    async with async_playwright() as p:
        # headless=True : le navigateur tourne en fond sans ouvrir de fenêtre. 
        # Mets-le sur False pour voir le robot cliquer en direct quand tu fais tes tests !
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # On simule un comportement humain classique (user-agent) pour éviter les blocages basiques
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})

        print(" Chargement de la page en cours...")
        await page.goto(url_recherche)

        # On attend un peu que le JavaScript charge les offres (3 secondes)
        await page.wait_for_timeout(3000)

        # On récupère tout le code HTML de la page une fois chargée
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')

        offres_trouvees = []

        # ==========================================
        #  ZONE À ADAPTER SELON LE SITE (F12 / Inspecter)
        # ==========================================
        # Exemple générique : on cherche les blocs qui contiennent les offres.
        # Sur WTTJ, ça pourrait être des balises <article> ou des <div class="sc-XXXXX">
        
        blocs_offres = soup.find_all('article') # À modifier selon le site

        print(f" {len(blocs_offres)} offres potentielles détectées. Extraction en cours...")

        for bloc in blocs_offres[:5]: # On se limite aux 5 premières pour ne pas saturer ton IA au début
            try:
                # Il faut inspecter le site pour trouver les bonnes balises
                titre = bloc.find('h2').text.strip() if bloc.find('h2') else "Titre inconnu"
                entreprise = bloc.find('span').text.strip() if bloc.find('span') else "Entreprise inconnue"
                
                # Récupération du lien
                lien_balise = bloc.find('a')
                lien_offre = lien_balise['href'] if lien_balise else ""
                
                # Si le lien est relatif (ex: /jobs/devops), on ajoute la racine du site
                if lien_offre and not lien_offre.startswith('http'):
                    lien_offre = "https://www.site-cible.com" + lien_offre

                # Pour être complet, l'idéal serait d'ouvrir 'lien_offre' avec Playwright 
                # pour récupérer la description complète. Ici on met un texte temporaire.
                description = "Description complète à scraper sur la page de l'offre..."

                offres_trouvees.append({
                    "titre": titre,
                    "entreprise": entreprise,
                    "lien": lien_offre,
                    "description": description
                })
            except Exception as e:
                print(f"Erreur sur une offre : {e}")

        await browser.close()
        return offres_trouvees

# ==========================================
# TEST DU SCRAPER
# ==========================================
if __name__ == "__main__":
    # Remplace par une vraie URL de recherche (ex: Welcome to the Jungle, Indeed...)
    url_test = "https://www.example-job-board.com/recherche?q=devops&l=toulon"
    
    # On exécute la fonction asynchrone
    resultats = asyncio.run(scraper_offres(url_test))
    
    # On affiche le résultat de façon jolie (JSON formaté)
    print("\n RÉSULTAT DU SCRAPING :")
    print(json.dumps(resultats, indent=2, ensure_ascii=False))