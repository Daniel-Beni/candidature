# pyright: reportMissingImports=false
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv() 

# CONFIGURATION NATIVE CREWAI POUR GROQ
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.5
)

# ... le reste du code (agents et tâches) reste EXACTEMENT pareil ...

def generer_relance(infos_suivi):
    agent_relance = Agent(
        role="Expert en Communication Professionnelle",
        goal="Rédiger des e-mails de relance percutants et polis.",
        backstory="Tu es un expert RH. Tu relances sans paraître insistant. Ton poli et direct.",
        verbose=True, allow_delegation=False, llm=llm
    )

    tache_redaction_relance = Task(
        description=f"""
        Rédige un e-mail de relance court pour :
        - Entreprise : {infos_suivi['entreprise']}
        - Poste : {infos_suivi['poste_vise']}
        - Date d'envoi : {infos_suivi['date_envoi']}
        Consignes : Objet clair, max 4 phrases, propose un échange téléphonique.
        """,
        expected_output="Un brouillon d'e-mail de relance.",
        agent=agent_relance
    )

    crew_relance = Crew(agents=[agent_relance], tasks=[tache_redaction_relance], process=Process.sequential)
    return str(crew_relance.kickoff())