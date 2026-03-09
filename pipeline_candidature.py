import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv() 
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

profil_json = load_file('profil.json')
template_lettre = load_file('lettre_motivation.md')

def analyser_et_rediger(description_offre):
    agent_analyste = Agent(
        role="Analyste Technique en Recrutement IT",
        goal="Analyser les offres d'emploi et déterminer le niveau de compatibilité.",
        backstory="Tu es un expert en recrutement tech. Tu identifies les compétences clés.",
        verbose=True, allow_delegation=False, llm=llm
    )

    agent_redacteur = Agent(
        role="Rédacteur de Lettre de Motivation Expert",
        goal="Rédiger une lettre de motivation ultra-personnalisée.",
        backstory="Tu es un as de la communication. Tu n'inventes JAMAIS d'expériences.",
        verbose=True, allow_delegation=False, llm=llm
    )

    tache_analyse = Task(
        description=f"Lis l'offre : {description_offre}\nAnalyse le profil : {profil_json}\nSors les points forts.",
        expected_output="Un rapport des atouts du candidat pour l'offre.",
        agent=agent_analyste
    )

    tache_redaction = Task(
        description=f"Utilise l'analyse. Prends ce modèle : {template_lettre}\nRemplace les variables {{ }} par les bonnes infos.",
        expected_output="La lettre de motivation finale en Markdown.",
        agent=agent_redacteur
    )

    crew = Crew(agents=[agent_analyste, agent_redacteur], tasks=[tache_analyse, tache_redaction], process=Process.sequential)
    resultat_final = crew.kickoff()
    return str(resultat_final)