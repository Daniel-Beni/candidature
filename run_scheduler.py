import schedule
import time
import os
import datetime

def lancer_pipeline():
    print(f"[{datetime.datetime.now()}]  Lancement automatique...")
    os.system("python chef_orchestre.py --auto")

schedule.every().day.at("08:00").do(lancer_pipeline)
print("Conteneur démarré. Exécution prévue à 08:00.")

while True:
    schedule.run_pending()
    time.sleep(60)