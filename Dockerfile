# On utilise l'image officielle Playwright qui contient déjà Python et les navigateurs
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Définition du répertoire de travail
WORKDIR /app

# Copie des dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tous tes scripts et fichiers (profil.json, lettre_motivation.md, etc.)
COPY . .

# On crée un dossier spécifiquement pour la base de données (pour la persistance)
RUN mkdir -p /app/data

# Commande de lancement du conteneur (le script qui tourne en boucle)
CMD ["python", "run_scheduler.py"]