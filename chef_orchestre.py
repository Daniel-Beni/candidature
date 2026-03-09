import sys
import os
import sqlite3
import datetime
import asyncio

# === IMPORT DES AGENTS ===
from agent_scraper import scraper_offres
from pipeline_candidature import analyser_et_rediger
from agent_relance import generer_relance

DB_NAME = "data/candidatures.db"

def init_db():
    os.makedirs("data", exist_ok=True) # Crée le dossier data/ s'il n'existe pas
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

def enregistrer_nouvelles_offres(offres_trouvees):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    ajouts = 0
    for offre in offres_trouvees:
        try:
            # CORRECTION DU DEPRECATION WARNING : On convertit la date en texte avec str()
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
    
    for offre in offres_a_traiter:
        id_offre, titre, entreprise, description = offre
        print(f"\n🤖 Lancement IA : {titre} chez {entreprise}...")
        
        lettre = analyser_et_rediger(description) 
        
        cursor.execute('''
            UPDATE candidatures SET statut = 'A_POSTULER', lettre_generee = ? WHERE id = ?
        ''', (lettre, id_offre))
        
    conn.commit()
    conn.close()
    print(f"✅ {len(offres_a_traiter)} lettres générées (Statut: A_POSTULER).")

def verifier_et_creer_relances():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    limite_jours = datetime.date.today() - datetime.timedelta(days=7)
    
    # Correction de la date ici aussi
    cursor.execute("SELECT id, entreprise, titre, date_action FROM candidatures WHERE statut = 'POSTULEE' AND date_action <= ?", (str(limite_jours),))
    a_relancer = cursor.fetchall()
    
    for offre in a_relancer:
        id_offre, entreprise, titre, date_postulat = offre
        print(f"⏰ Relance IA pour {entreprise}...")
        
        infos = {"entreprise": entreprise, "poste_vise": titre, "date_envoi": date_postulat}
        brouillon = generer_relance(infos)
        
        cursor.execute('''
            UPDATE candidatures SET statut = 'A_RELANCER', brouillon_relance = ? WHERE id = ?
        ''', (brouillon, id_offre))

    conn.commit()
    conn.close()
    print(f"📧 {len(a_relancer)} brouillons de relance générés.")

def lire_resultats():
    """Affiche les lettres générées dans le terminal"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT entreprise, lettre_generee FROM candidatures WHERE statut = 'A_POSTULER'")
    resultats = cursor.fetchall()
    
    for row in resultats:
        entreprise, lettre = row
        print(f"\n{'='*50}\n📄 LETTRE POUR : {entreprise}\n{'='*50}\n{lettre}")
    conn.close()

if __name__ == "__main__":
    init_db()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("🤖 [MODE AUTO] Lancement de la routine...")
        traiter_offres_trouvees()
        verifier_et_creer_relances()
        print("✅ [MODE AUTO] Terminé.")
    else:
        while True:
            print("\n--- 🛠️ PIPELINE DE CANDIDATURE ---")
            print("1. Injecter l'offre de test ETINARS (Pour tester l'IA)")
            print("2. Lancer le Scraper (Chercher sur le web)")
            print("3. Lancer l'IA (Rédiger les lettres)")
            print("4. Vérifier les relances (Après 7j)")
            print("5. Afficher les statistiques")
            print("6. 📖 LIRE LES LETTRES GÉNÉRÉES")
            print("0. Quitter")
            
            choix = input("\nChoix : ")
            
            if choix == "1":
                # TON OFFRE ETINARS EST INJECTÉE ICI
                offre_mock = [{
                    "titre": "Stage Cloud Developer - Kubernetes / DevOps (Toulouse | Space)", 
                    "entreprise": "Etinars", 
                    "lien": "https://www.etinars.com", 
                    "description": """WHO WE ARE
Etinars est une entreprise guidée par des fermes valeurs, forte de plusieurs années d’expérience, spécialisée dans le recrutement de professionnels sur des marchés de niche, en gérant l’ensemble du cycle de recrutement de profils spécialisés et exécutifs.
Chez Etinars, nous nous intéressons réellement à qui vous êtes et à ce dont vous avez besoin.
Nous accordons une grande importance à la création de relations solides et durables, basées sur la confiance et la transparence.
Notre approche vous accompagne à chaque étape, avec un parcours rapide et structuré vers votre prochaine évolution de carrière.

WHAT WE ARE LOOKING FOR
Stage Cloud Developer - Kubernetes / DevOps (Toulouse | Space)
Rejoignez un environnement international qui contribue à des programmes nationaux et européens dans des domaines où la fiabilité, la précision et la sécurité sont essentielles (notamment Space, défense et transport). Vous évoluerez au sein d’équipes mêlant ingénierie, opérations et services digitaux, avec un fort focus sur des technologies modernes et utiles “dans la vraie vie”.
Nous recherchons un(e) Cloud Developer Intern pour rejoindre l'équipe de notre client basée à Toulouse. Ce stage est une opportunité concrète et “hands-on” pour apprendre à concevoir et maintenir une infrastructure cloud-native basée sur Kubernetes, dans un contexte DevOps/SRE.
Durée : stage de 6 mois (convention universitaire, stage de fin d’études, 5e année / Master). Début idéal février / mars. Si l’évaluation du stage est positive, une poursuite en CDI pourra être envisagée.

YOUR TASKS
Dans ce rôle, vous serez amené(e) à :
Participer à la conception et au déploiement d’un cluster Kubernetes sur un cloud public.
Automatiser des environnements avec Terraform, Helm et Ansible.
Mettre en place des solutions de monitoring et logging : Prometheus, Grafana, ELK, Loki.
Contribuer au déploiement d’applications conteneurisées via GitLab CI ou ArgoCD.
Participer à la documentation (best practices, procédures) pour capitaliser la connaissance.
Suivre l’évolution des outils cloud-native et partager vos recommandations avec l’équipe.

YOUR SKILLS AND EXPERIENCE
Étudiant(e) en Ingénierie, Informatique, Computer Science ou Cloud Systems.
Première familiarité avec Docker, Kubernetes (ou Rancher) via cours/projets/stage est un plus.
À l’aise sur environnement Linux.
Scripting : Bash et/ou Python.
Curieux(se), rigoureux(se), fiable, avec une vraie motivation à apprendre et à progresser.
Esprit d’équipe et capacité à travailler dans un environnement structuré."""
                }]
                enregistrer_nouvelles_offres(offre_mock)
            elif choix == "2":
                url = input("URL à scraper (ex: site-emploi.com) : ")
                offres = asyncio.run(scraper_offres(url))
                enregistrer_nouvelles_offres(offres)
            elif choix == "3":
                traiter_offres_trouvees()
            elif choix == "4":
                verifier_et_creer_relances()
            elif choix == "5":
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT statut, COUNT(*) FROM candidatures GROUP BY statut")
                for statut, count in cursor.fetchall():
                    print(f"- {statut} : {count}")
                conn.close()
            elif choix == "6":
                lire_resultats()
            elif choix == "0":
                break