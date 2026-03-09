import sys
import sqlite3
import datetime
import time


# ==========================================
# IMPORTS DE TES AGENTS (Fichiers précédents)
# ==========================================
# Décommente ces lignes quand tes autres scripts sont prêts et dans le même dossier
# from agent_scraper import scraper_offres
# from pipeline_candidature import analyser_et_rediger  # Ta fonction CrewAI
# from agent_relance import generer_relance             # Ta fonction CrewAI de relance

DB_NAME = "data/candidatures.db"

# ==========================================
# 1. INITIALISATION DE LA BASE DE DONNÉES
# ==========================================
def init_db():
    
    """Crée la table si elle n'existe pas encore."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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
            brouillon_relance TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(" Base de données initialisée avec succès.")

# ==========================================
# 2. INTÉGRATION DES NOUVELLES OFFRES (Le Scraper)
# ==========================================
def enregistrer_nouvelles_offres(offres_trouvees):
    """Enregistre les offres du scraper sans faire de doublons."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    ajouts = 0
    
    for offre in offres_trouvees:
        try:
            cursor.execute('''
                INSERT INTO candidatures (titre, entreprise, lien, description, statut, date_ajout)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (offre['titre'], offre['entreprise'], offre['lien'], offre['description'], 'TROUVEE', datetime.date.today()))
            ajouts += 1
        except sqlite3.IntegrityError:
            # Le lien existe déjà dans la BDD (contrainte UNIQUE), on ignore
            pass
            
    conn.commit()
    conn.close()
    print(f" {ajouts} nouvelles offres ajoutées à la base de données.")

# ==========================================
# 3. TRAITEMENT PAR L'IA (Analyste & Rédacteur)
# ==========================================
def traiter_offres_trouvees():
    """Trouve les offres 'TROUVEE' et génère les lettres de motivation."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, titre, entreprise, description FROM candidatures WHERE statut = 'TROUVEE'")
    offres_a_traiter = cursor.fetchall()
    
    for offre in offres_a_traiter:
        id_offre, titre, entreprise, description = offre
        print(f" Analyse et rédaction en cours pour : {titre} chez {entreprise}...")
        
        #  ICI ON APPELLE TON SCRIPT CREWAI
        # lettre = analyser_et_rediger(description) 
        lettre = "Ceci est une lettre de motivation simulée générée par l'IA." # Remplacer par l'appel réel
        
        # On met à jour le statut
        cursor.execute('''
            UPDATE candidatures 
            SET statut = 'A_POSTULER', lettre_generee = ?
            WHERE id = ?
        ''', (lettre, id_offre))
        
    conn.commit()
    conn.close()
    print(f" {len(offres_a_traiter)} offres sont prêtes à être envoyées (Statut: A_POSTULER).")

# ==========================================
# 4. GESTION DES RELANCES (Agent Relance)
# ==========================================
def verifier_et_creer_relances():
    """Vérifie si des candidatures 'POSTULEE' datent de plus de 7 jours."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    limite_jours = datetime.date.today() - datetime.timedelta(days=7)
    
    cursor.execute("SELECT id, entreprise, titre, date_action FROM candidatures WHERE statut = 'POSTULEE' AND date_action <= ?", (limite_jours,))
    a_relancer = cursor.fetchall()
    
    for offre in a_relancer:
        id_offre, entreprise, titre, date_postulat = offre
        print(f" Relance nécessaire pour {entreprise} (Postulé le {date_postulat}). Création du brouillon...")
        
        #  ICI ON APPELLE TON SCRIPT DE RELANCE CREWAI
        # infos = {"entreprise": entreprise, "poste_vise": titre, "date_envoi": date_postulat}
        # brouillon = generer_relance(infos)
        brouillon = "Objet: Relance\n\nBonjour, je vous relance pour ma candidature..." # Simulation
        
        cursor.execute('''
            UPDATE candidatures 
            SET statut = 'A_RELANCER', brouillon_relance = ?
            WHERE id = ?
        ''', (brouillon, id_offre))

    conn.commit()
    conn.close()
    print(f" {len(a_relancer)} brouillons de relance générés.")

# ==========================================
#  MENU PRINCIPAL DU CHEF D'ORCHESTRE
# ==========================================
if __name__ == "__main__":
    init_db()
    
    print("\n---  PIPELINE DE CANDIDATURE DE DANIEL ---")
    print("1. Lancer le Scraper (Chercher de nouvelles offres)")
    print("2. Lancer l'IA (Rédiger les lettres pour les nouvelles offres)")
    print("3. Vérifier les relances (Créer les brouillons après 7j)")
    print("4. Afficher le tableau de bord des candidatures")
    
    choix = input("\nQue veux-tu faire ? (1/2/3/4) : ")
    
    if choix == "1":
        # url = "https://www.wttj.com/..."
        # offres = asyncio.run(scraper_offres(url))
        offres_simulees = [
            {"titre": "Stage DevOps", "entreprise": "Thales", "lien": "http://lien1", "description": "Offre Thales..."},
            {"titre": "Dev Fullstack", "entreprise": "Naval Group", "lien": "http://lien2", "description": "Offre Naval..."}
        ]
        enregistrer_nouvelles_offres(offres_simulees)
        
    elif choix == "2":
        traiter_offres_trouvees()
        
    elif choix == "3":
        verifier_et_creer_relances()
        
    elif choix == "4":
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT statut, COUNT(*) FROM candidatures GROUP BY statut")
        stats = cursor.fetchall()
        print("\n ÉTAT DE TES CANDIDATURES :")
        for statut, count in stats:
            print(f"- {statut} : {count}")
        conn.close()
    else:
        print("Choix invalide.")
        
if __name__ == "__main__":
    init_db()
    
    # Si on lance le script avec l'argument "--auto" (ex: python chef_orchestre.py --auto)
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print(" [MODE AUTO] Lancement de la routine matinale...")
        
        # 1. On lance le scraper
        # offres = asyncio.run(scraper_offres("TON_URL_ICI"))
        # enregistrer_nouvelles_offres(offres)
        
        # 2. On lance l'IA pour rédiger
        traiter_offres_trouvees()
        
        # 3. On vérifie les relances
        verifier_et_creer_relances()
        
        print(" [MODE AUTO] Routine terminée avec succès.")
        
    else:
        # Mode Manuel (celui qu'on avait avant)
        print("\n---  PIPELINE DE CANDIDATURE DE DANIEL ---")
        print("1. Lancer le Scraper (Chercher de nouvelles offres)")
        print("2. Lancer l'IA (Rédiger les lettres pour les nouvelles offres)")
        print("3. Vérifier les relances (Créer les brouillons après 7j)")
        print("4. Afficher le tableau de bord")
        choix = input("\nQue veux-tu faire ? (1/2/3/4) : ")
        
        # ... (Garder tes conditions if choix == "1", etc. ici) ...