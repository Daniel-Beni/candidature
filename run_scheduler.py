import schedule
import time
import os
import datetime

def lancer_pipeline():
    print(f"[{datetime.datetime.now()}]  Lancement automatique du pipeline...")
    # Appelle ton script avec l'argument --auto que nous avons configuré
    os.system("python chef_orchestre.py --auto")

# Planification tous les jours à 08:00
schedule.every().day.at("08:00").do(lancer_pipeline)

print("Conteneur démarré. Le planificateur est actif (Exécution prévue tous les jours à 08:00).")

# Boucle infinie pour garder le conteneur actif et vérifier l'heure
while True:
    schedule.run_pending()
    time.sleep(60) # Vérifie toutes les minutes pour ne pas surcharger le CPU