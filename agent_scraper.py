import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scraper_offres(url_recherche):
    print(f" Lancement de l'Agent Scraper sur : {url_recherche}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"})

        print("⏳ Recherche des liens d'offres sur la page principale...")
        await page.goto(url_recherche)
        await page.wait_for_timeout(5000) # On laisse charger la liste

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. On récupère UNIQUEMENT les vrais liens d'offres d'emploi
        tous_les_liens = soup.find_all('a', href=True)
        liens_offres = []
        for a in tous_les_liens:
            href = a['href']
            # Sur WTTJ, les vraies offres ont ce format d'URL
            if '/companies/' in href and '/jobs/' in href:
                url_complete = href if href.startswith('http') else "https://www.welcometothejungle.com" + href
                if url_complete not in liens_offres:
                    liens_offres.append(url_complete)

        print(f" {len(liens_offres)} offres trouvées. Visite des 3 premières pour le Deep Scraping...")
        
        offres_trouvees = []

        # 2. DEEP SCRAPING : Le robot va visiter chaque page d'offre une par une
        for lien in liens_offres[:3]: # On limite à 3 pour tester rapidement
            print(f"\n Scraping en profondeur de : {lien}")
            try:
                await page.goto(lien)
                await page.wait_for_timeout(3000) # On attend que le texte de l'offre charge
                
                page_html = await page.content()
                page_soup = BeautifulSoup(page_html, 'html.parser')
                
                # A. Extraction du VRAI Titre (souvent dans la balise <h1>)
                h1_tag = page_soup.find('h1')
                titre = h1_tag.text.strip() if h1_tag else "Ingénieur / Développeur"
                
                # B. Extraction de la VRAIE Entreprise (cachée dans l'URL de WTTJ)
                # Ex: .../companies/idex/jobs/... -> on extrait "idex" et on met une majuscule
                entreprise = lien.split('/companies/')[1].split('/')[0].capitalize()
                entreprise = entreprise.replace('-', ' ') # Nettoie les tirets éventuels
                
                # C. Extraction de la VRAIE Description
                # On aspire tout le texte contenu dans la balise principale de la page
                main_content = page_soup.find('main')
                if main_content:
                    description = main_content.text.strip()
                else:
                    description = page_soup.text.strip()
                    
                # On nettoie le texte pour l'IA (enlever les sauts de ligne inutiles) et on garde les 2500 premiers caractères
                description = " ".join(description.split())[:2500] 
                
                offres_trouvees.append({
                    "titre": titre,
                    "entreprise": entreprise,
                    "lien": lien,
                    "description": description
                })
                print(f" Succès : {titre} chez {entreprise}")
                
            except Exception as e:
                print(f" Erreur sur {lien} : {e}")

        await browser.close()
        return offres_trouvees