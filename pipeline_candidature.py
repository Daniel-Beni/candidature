import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

# ==========================================
# 1. CONFIGURATION DU LLM (Sécurisée)
# ==========================================
# Cette ligne va chercher automatiquement le fichier .env caché et charger la clé
load_dotenv() 

# Tant que ta variable dans le fichier .env s'appelle bien "GOOGLE_API_KEY", 
# Langchain la trouvera tout seul, sans que tu aies à la déclarer !
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

# ==========================================
# 2. CHARGEMENT DE TA "SOURCE DE VÉRITÉ"
# ==========================================
def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

profil_json = load_file('profil.json')
template_lettre = load_file('lettre_motivation.md')

# OFFRE D'EMPLOI TEST (À remplacer plus tard par la sortie de l'Agent Scraper)
offre_emploi_test = """
Recherche Ingénieur DevOps (Stage/Alternance). 
Missions : Mettre en place des pipelines CI/CD, conteneurisation des applications.
Stack technique : Docker, Kubernetes, GitLab CI, Python, GCP.
Profil : Vous êtes curieux, aimez le travail en équipe et avez une première expérience avec le Cloud.
"""

# ==========================================
# 3. CRÉATION DES AGENTS IA
# ==========================================

agent_analyste = Agent(
    role="Analyste Technique en Recrutement IT",
    goal="Analyser les offres d'emploi et déterminer le niveau de compatibilité avec le profil du candidat.",
    backstory="Tu es un expert en recrutement tech. Tu sais lire entre les lignes d'une offre d'emploi pour identifier les compétences clés (hard skills et soft skills) réellement attendues.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

agent_redacteur = Agent(
    role="Rédacteur de Lettre de Motivation Expert",
    goal="Rédiger une lettre de motivation ultra-personnalisée et percutante en adaptant un modèle existant.",
    backstory="Tu es un as de la communication professionnelle. Tu sais mettre en valeur les expériences d'un candidat pour qu'elles matchent parfaitement avec le besoin de l'entreprise, sans jamais mentir ni inventer d'expériences.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# ==========================================
# 4. DÉFINITION DES TÂCHES
# ==========================================

tache_analyse = Task(
    description=f"""
    1. Lis l'offre d'emploi suivante : {offre_emploi_test}
    2. Analyse le profil du candidat : {profil_json}
    3. Identifie les points forts du candidat pour ce poste précis.
    4. Sors une liste claire des projets et compétences du candidat à mettre en avant pour cette offre.
    """,
    expected_output="Un rapport court résumant les atouts du candidat pour l'offre, avec un score de compatibilité sur 100.",
    agent=agent_analyste
)

tache_redaction = Task(
    description=f"""
    1. Utilise l'analyse fournie par l'Analyste Technique.
    2. Prends ce modèle de lettre de motivation : {template_lettre}
    3. Remplace les variables entre accolades {{ }} par les informations pertinentes tirées de l'offre d'emploi et du profil du candidat.
    4. Assure-toi que la lettre soit fluide, professionnelle et ne contienne aucune hallucination (n'invente pas de compétences).
    """,
    expected_output="Une lettre de motivation finale, formatée en Markdown, prête à être envoyée.",
    agent=agent_redacteur
)

# ==========================================
# 5. ASSEMBLAGE DE L'ÉQUIPAGE (CREW)
# ==========================================

crew = Crew(
    agents=[agent_analyste, agent_redacteur],
    tasks=[tache_analyse, tache_redaction],
    process=Process.sequential # L'analyste travaille d'abord, puis passe le relais au rédacteur
)

# ==========================================
# 6. LANCEMENT DU PIPELINE
# ==========================================
print("Lancement des agents pour analyser l'offre et rédiger la candidature...")
resultat_final = crew.kickoff()

print("==========================================\n")
print(" RÉSULTAT FINAL (LETTRE GÉNÉRÉE) :\n")
print(resultat_final)