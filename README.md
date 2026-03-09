# Automated Job Hunter AI

> Un pipeline automatisé et conteneurisé de recherche d'emploi, propulsé par une architecture multi-agents IA.

Ce projet personnel a été conçu pour optimiser et automatiser ma recherche de stage. Il s'occupe de sourcer les offres, d'analyser ma compatibilité avec celles-ci, et de rédiger des lettres de motivation sur mesure, le tout orchestré de manière autonome dans le cloud.

## Fonctionnalités Principales

* **Web Scraping Asynchrone :** Extraction des offres d'emploi ciblées via Playwright.
* **Architecture Multi-Agents (CrewAI) :**
  *  *Agent Analyste :* Évalue la pertinence de l'offre par rapport à mon profil structuré (JSON).
  *  *Agent Rédacteur :* Génère une lettre de motivation sans hallucination, basée sur un template et les données réelles de l'offre.
  * *Agent Relance :* Rédige des brouillons d'e-mails ciblés pour les candidatures sans réponse après 7 jours.
* **Persistance des Données :** Suivi de l'état des candidatures (Trouvée, À Postuler, Postulée, À Relancer) via une base de données locale **SQLite**.
* **Automatisation DevOps :** Planification quotidienne des tâches en tâche de fond (Schedule).
* **Déploiement Cloud-Native :** Conteneurisation complète (Docker) et déploiement sur une VM **Google Cloud Platform (GCP)**.

## Stack Technique

* **Langage :** Python 3.12
* **IA & LLMs :** CrewAI, LangChain, Google Gemini API (1.5 Flash)
* **Scraping :** Playwright, BeautifulSoup4
* **Base de données :** SQLite
* **Infra & DevOps :** Docker, Docker Compose, GCP (Compute Engine)

## Architecture du Projet

1. Le script `run_scheduler.py` tourne en boucle dans le conteneur Docker.
2. Tous les jours à 8h00, il déclenche `chef_orchestre.py`.
3. Le chef d'orchestre interroge le Scraper pour les nouvelles offres, met à jour la base SQLite, et déclenche les agents IA pour la rédaction et les relances.
4. L'utilisateur (moi) accède à la base de données pour récupérer les lettres prêtes à l'envoi et met à jour les statuts.

## Installation & Déploiement

### Prérequis
* Docker et Docker Compose installés sur votre machine ou serveur.
* Une clé API valide (ex: Google Gemini).

### Lancement en Local ou sur Serveur

1. Clonez ce dépôt :
   ```bash
   git clone [https://github.com/votre-pseudo/automated-job-hunter.git](https://github.com/votre-pseudo/automated-job-hunter.git)
   cd automated-job-hunter