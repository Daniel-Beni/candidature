# Automated Job Hunter AI

> Un pipeline automatisé et conteneurisé de recherche d'emploi, propulsé par une architecture multi-agents IA.

Ce projet personnel a été conçu pour optimiser et automatiser ma recherche de stage. Il s'occupe de sourcer les offres, d'analyser ma compatibilité avec celles-ci, et de rédiger des lettres de motivation sur mesure, le tout orchestré de manière autonome dans le cloud.

##  Fonctionnalités Principales
* **Web Scraping Asynchrone :** Extraction via Playwright.
* **Architecture Multi-Agents (CrewAI) :**
  * *Agent Analyste :* Évalue la pertinence de l'offre (JSON Profile).
  *  *Agent Rédacteur :* Génère une lettre de motivation sans hallucination.
  * *Agent Relance :* Rédige des brouillons de relance après 7 jours.
* **Persistance (SQLite) :** Suivi de l'état des candidatures.
* **DevOps :** Docker, GCP (Compute Engine), Schedule.

##  Installation & Déploiement
1. Clonez ce dépôt :
   `git clone https://github.com/Daniel-Beni/candidature.git`
2. Créez un fichier `.env` avec `GOOGLE_API_KEY=votre_cle`
3. Lancez en arrière-plan : `docker-compose up -d --build`