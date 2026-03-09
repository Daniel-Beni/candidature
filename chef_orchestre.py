import sys
import os
import sqlite3
import datetime
import asyncio
import time

from agent_scraper import scraper_offres
from pipeline_candidature import analyser_et_rediger
from agent_relance import generer_relance

DB_NAME = "data/candidatures.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 🆕 Ajout de la colonne cv_genere
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            entreprise TEXT,
            lien TEXT UNIQUE,
            description TEXT,
            statut TEXT,
            date_ajout DATE,
            date_action DATE,
            lettre_generee TEXT,
            cv_genere TEXT, 
            brouillon_relance TEXT
        )
    ''')
    conn.commit()
    conn.close()

def enregistrer_nouvelles_offres(offres_trouvees):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    ajouts = 0
    for offre in offres_trouvees:
        try:
            cursor.execute('''
                INSERT INTO candidatures (titre, entreprise, lien, description, statut, date_ajout)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (offre['titre'], offre['entreprise'], offre['lien'], offre['description'], 'TROUVEE', str(datetime.date.today())))
            ajouts += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    print(f"📥 {ajouts} nouvelles offres ajoutées à la BDD.")

def traiter_offres_trouvees():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, titre, entreprise, description FROM candidatures WHERE statut = 'TROUVEE'")
    offres_a_traiter = cursor.fetchall()
    
    if len(offres_a_traiter) == 0:
        print("✅ Aucune nouvelle offre à traiter pour le moment.")
        return

    for offre in offres_a_traiter:
        id_offre, titre, entreprise, description = offre
        print(f"\n🤖 Lancement IA (CV + Lettre) : {titre} chez {entreprise}...")
        
        # 🆕 Récupération du CV et de la Lettre
        lettre, cv = analyser_et_rediger(titre, entreprise, description) 
        
        cursor.execute('''
            UPDATE candidatures SET statut = 'A_POSTULER', lettre_generee = ?, cv_genere = ? WHERE id = ?
        ''', (lettre, cv, id_offre))
        
        conn.commit()
        print(f"✅ CV et Lettre générés pour {entreprise}.")

        if offre != offres_a_traiter[-1]:
            print("⏳ Pause de 20 secondes (Groq est très rapide, une petite pause suffit)...")
            time.sleep(20)
        
    conn.close()
    print(f"\n🎉 Terminé ! {len(offres_a_traiter)} candidatures (CV + Lettre) préparées.")

def verifier_et_creer_relances():
    # ... code inchangé ...
    pass

def lire_resultats():
    """Affiche les CV et lettres générés dans le terminal"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    #  On récupère aussi le CV
    cursor.execute("SELECT entreprise, cv_genere, lettre_generee FROM candidatures WHERE statut = 'A_POSTULER'")
    resultats = cursor.fetchall()
    
    if not resultats:
        print("Dossier vide. Aucune candidature au statut 'A_POSTULER'.")
        
    for row in resultats:
        entreprise, cv, lettre = row
        print(f"\n\n{'='*70}")
        print(f"DOSSIER DE CANDIDATURE : {entreprise}")
        print(f"{'='*70}")
        print("\n\n---  CV OPTIMISÉ ---")
        print(cv)
        print("\n\n---  LETTRE DE MOTIVATION ---")
        print(lettre)
        print(f"{'='*70}\n")
    conn.close()

if __name__ == "__main__":
    init_db()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        traiter_offres_trouvees()
        verifier_et_creer_relances()
    else:
        while True:
            print("\n--- PIPELINE DE CANDIDATURE ---")
            print("1. Injecter l'offre de test ETINARS (Pour tester l'IA)")
            print("2. Lancer le Scraper (Chercher sur le web)")
            print("3. Lancer l'IA (Rédiger CV + Lettres)")
            print("4. Vérifier les relances (Après 7j)")
            print("5. Afficher les statistiques")
            print("6. LIRE LES DOSSIERS GÉNÉRÉS (CV + LETTRES)")
            print("0. Quitter")
            
            choix = input("\nChoix : ")
            
            if choix == "1":
                pass # Tu peux laisser ton offre factice ici ou l'enlever
            elif choix == "2":
                url = input("URL à scraper (ex: site-emploi.com) : ")
                offres = asyncio.run(scraper_offres(url))
                enregistrer_nouvelles_offres(offres)
            elif choix == "3":
                traiter_offres_trouvees()
            elif choix == "4":
                verifier_et_creer_relances()
            elif choix == "5":
                pass # Statistique standard
            elif choix == "6":
                lire_resultats()
            elif choix == "0":
                break