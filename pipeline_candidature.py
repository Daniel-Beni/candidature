import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv() 

# Configuration de Llama 3 via Groq
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.5
)

def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

profil_json = load_file('profil.json')
template_lettre = load_file('lettre_motivation.md')

def analyser_et_rediger(titre, entreprise, description_offre):
    # 1. L'Analyste (Il lit et comprend)
    agent_analyste = Agent(
        role="Analyste Technique en Recrutement IT",
        goal="Analyser l'offre d'emploi et extraire les mots-clés et compétences exigés.",
        backstory="Tu es un expert en recrutement tech. Tu sais identifier exactement ce qu'un recruteur veut lire (outils, soft skills, missions).",
        verbose=True, allow_delegation=False, llm=llm
    )

   
   # 2. LE NOUVEAU : L'Optimiseur de CV (Il forge l'arme principale)
    agent_cv = Agent(
        role="Expert en Optimisation de CV (ATS-Friendly)",
        goal="Créer un CV sur mesure, ultra-concis (format 1 page), basé sur le profil du candidat et les besoins stricts de l'offre.",
        backstory="Tu es un ancien recruteur impitoyable devenu expert en algorithmes ATS. Tu sais mettre en gras les mots-clés exacts, mais surtout, tu SUPPRIMES sans hésiter toutes les compétences et projets qui ne sont pas directement liés à l'offre. Tu détestes le superflu.",
        verbose=True, allow_delegation=False, llm=llm
    )

    # 3. Le Rédacteur de Lettre
    agent_redacteur = Agent(
        role="Rédacteur de Lettre de Motivation Expert",
        goal="Rédiger une lettre de motivation percutante et alignée avec le CV optimisé.",
        backstory="Tu es un as de la communication. Tu n'inventes JAMAIS d'informations.",
        verbose=True, allow_delegation=False, llm=llm
    )

    tache_analyse = Task(
        description=f"Analyse l'offre pour le poste de '{titre}' chez '{entreprise}'.\nDescription de l'offre : {description_offre}\nSors les 5 compétences techniques et les 3 soft skills clés de cette offre.",
        expected_output="Une liste à puces des mots-clés et compétences recherchées par l'entreprise.",
        agent=agent_analyste
    )

    tache_cv = Task(
        description=f"""
        Utilise le rapport de l'analyste et le profil brut du candidat : {profil_json}.
        Crée un CV ultra-ciblé et concis en Markdown pour le poste de '{titre}' chez '{entreprise}'.
        L'objectif est que ce CV tienne sur UNE SEULE PAGE. Il faut donc élaguer tout ce qui est hors sujet.
        
        CONSIGNES STRICTES POUR LE CV :
        1. Titre du CV : Mets le titre EXACT de l'offre.
        2. Compétences (Filtrage extrême) : NE GARDE QUE les compétences et catégories de compétences qui ont un lien direct avec l'offre. MASQUE totalement les compétences hors sujet. Mets en gras les mots-clés exacts de l'offre.
        3. Projets (Top 2 uniquement) : Sélectionne STRICTEMENT les 2 projets les plus pertinents pour cette offre, pas un de plus. Reformule leur description pour y intégrer les mots-clés de l'offre.
        4. Expériences : Ne garde que les missions de l'expérience les plus pertinentes pour le poste (3 puces maximum).
        5. Format : Uniquement du code Markdown propre (titres #, listes, gras). AUCUNE phrase d'introduction ou de conclusion générée par toi.
        """,
        expected_output="Un CV au format Markdown, ultra-ciblé, épuré des compétences inutiles et strictement limité à 2 projets maximum.",
        agent=agent_cv
    )

    tache_redaction = Task(
        description=f"""
        Tu dois rédiger la lettre pour le poste de '{titre}' chez '{entreprise}'.
        Utilise le rapport de l'analyste et assure-toi d'être cohérent avec le CV qui vient d'être généré. 
        Prends ce modèle de lettre : {template_lettre}
        
        CONSIGNES STRICTES :
        1. Remplace {{nom_entreprise}} EXACTEMENT par "{entreprise}".
        2. Remplace {{titre_du_poste}} EXACTEMENT par "{titre}".
        3. Remplis les autres variables intelligemment en fonction de l'offre.
        4. Sors UNIQUEMENT le texte final de la lettre en Markdown, rien d'autre.
        """,
        expected_output="La lettre de motivation finale en Markdown.",
        agent=agent_redacteur
    )

    crew = Crew(
        agents=[agent_analyste, agent_cv, agent_redacteur], 
        tasks=[tache_analyse, tache_cv, tache_redaction], 
        process=Process.sequential
    )
    
    # Lancement de l'équipe
    resultat_final = crew.kickoff()
    
    # On récupère le résultat de la lettre (le kickoff) ET le résultat de la tâche CV !
    return str(resultat_final), str(tache_cv.output)