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
# 2. DONNÉES DE LA CANDIDATURE (Simulées pour le test)
# ==========================================
# Dans la version finale, ces données viendront de ton fichier de suivi (CSV ou base de données)
infos_suivi = {
    "entreprise": "Alliance Marine",
    "poste_vise": "Stage Ingénieur Data / BI",
    "date_envoi": "il y a 10 jours",
    "nom_recruteur": "Inconnu", # Si tu as le nom, l'agent l'utilisera
    "ton": "Professionnel, poli, mais déterminé"
}

# ==========================================
# 3. CRÉATION DE L'AGENT DE RELANCE
# ==========================================
agent_relance = Agent(
    role="Expert en Communication Professionnelle",
    goal="Rédiger des e-mails de relance de candidature percutants, polis et concis.",
    backstory="""Tu es un expert en ressources humaines. Tu sais exactement comment 
    relancer un recruteur sans paraître insistant ou désespéré. Tu utilises un ton 
    courtois, direct, et tu rappelles subtilement la valeur du candidat.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# ==========================================
# 4. DÉFINITION DE LA TÂCHE
# ==========================================
tache_redaction_relance = Task(
    description=f"""
    Rédige un e-mail de relance court pour la candidature suivante :
    - Entreprise : {infos_suivi['entreprise']}
    - Poste : {infos_suivi['poste_vise']}
    - Date de candidature : {infos_suivi['date_envoi']}
    - Contact : {infos_suivi['nom_recruteur']}
    
    Consignes strictes :
    1. Propose un objet d'e-mail clair et professionnel.
    2. Le corps de l'e-mail doit comporter maximum 4 phrases.
    3. Rappelle l'intérêt pour le poste et l'entreprise.
    4. Propose un échange téléphonique.
    5. N'invente aucune information (pas d'hallucination).
    """,
    expected_output="Un brouillon d'e-mail prêt à être copié, contenant l'Objet et le Message.",
    agent=agent_relance
)

# ==========================================
# 5. EXÉCUTION
# ==========================================
crew_relance = Crew(
    agents=[agent_relance],
    tasks=[tache_redaction_relance],
    process=Process.sequential
)

print(f" Rédaction de la relance pour {infos_suivi['entreprise']}...")
brouillon_final = crew_relance.kickoff()

print("\n==========================================")
print("BROUILLON D'E-MAIL DE RELANCE GÉNÉRÉ :")
print("==========================================\n")
print(brouillon_final)