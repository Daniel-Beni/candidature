import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scraper_offres(url_recherche):
    print(f"Lancement de l'Agent Scraper sur : {url_recherche}")
    
    async with async_playwright() as p:
        # headless=True pour tourner en fond. Mets False si tu veux voir le robot cliquer !
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

        print("Chargement de la page en cours...")
        await page.goto(url_recherche)
        await page.wait_for_timeout(3000)

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        offres_trouvees = []

        # ==========================================
        #  BALISES À ADAPTER SELON LE SITE CIBLE
        # ==========================================
        blocs_offres = soup.find_all('article') 

        print(f" {len(blocs_offres)} offres potentielles détectées. Extraction...")

        for bloc in blocs_offres[:5]:
            try:
                titre = bloc.find('h2').text.strip() if bloc.find('h2') else "Titre inconnu"
                entreprise = bloc.find('span').text.strip() if bloc.find('span') else "Entreprise inconnue"
                lien_balise = bloc.find('a')
                lien_offre = lien_balise['href'] if lien_balise else ""
                
                if lien_offre and not lien_offre.startswith('http'):
                    lien_offre = "https://www.site-cible.com" + lien_offre

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