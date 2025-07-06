# /sophia/src/summarize.py
import os
from langchain_openai import ChatOpenAI
from langchain.schema.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from pydantic import SecretStr


def summarize_text(transcript: str, language: str = "français") -> tuple[str | None, str | None]:
    """
    Génère un résumé d'un texte donné en utilisant une stratégie Map-Reduce pour les longs textes.
    """
    try:
        # Vérification du texte d'entrée
        if not transcript or not transcript.strip():
            return None, "Le texte à résumer est vide ou ne contient que des espaces."
        
        # Initialisation du LLM (pas de changement ici)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return None, "Clé API OpenRouter manquante"
            
        llm = ChatOpenAI(
            model="deepseek/deepseek-chat-v3-0324:free",
            api_key=SecretStr(api_key),
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            timeout=1800, 
            default_headers={
                "HTTP-Referer": os.getenv("YOUR_SITE_URL", "http://localhost:8501"),
                "X-Title": os.getenv("YOUR_SITE_NAME", "Agent Resume YouTube"),
            }
        )


        # 1. Découper le texte en morceaux
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=750)
        docs = text_splitter.create_documents([transcript])
        
        # Si le texte est court, on n'a pas besoin de Map-Reduce
        if len(docs) == 1:
            print("--- Texte court, résumé direct ---")
            # Tu peux garder ton prompt simple ici si tu veux
            prompt = f"""En tant qu'expert pédagogique, rédige un résumé détaillé et bien structuré en {language} pour la transcription suivante. 
            Identifie les idées principales et présente-les sous forme de points clés clairs et concis.
            Assure-toi d'inclure les informations importantes et de ne pas omettre de détails significatifs : tips, ressources, bonnées idées, ou tout autre détail de valeur. 
            Le but est d'apprendre en utilisant ce résumé.

            Transcription :
            {transcript}

            Résumé structuré :"""
            response = llm.invoke([HumanMessage(content=prompt)])
            return str(response.content), None

        # 2. Utiliser une chaîne Map-Reduce de LangChain
        print(f"--- Texte long, stratégie Map-Reduce sur {len(docs)} morceaux ---")

        map_prompt_template = """En tant qu'expert pédagogique et assitant de rédaction, tu es chargé de résumer des parties d'une transcription.
        Voici un morceau de la transcription. Résume-le en {language} en extrayant les points essentiels.

        
        Assure-toi d'inclure les informations importantes et de ne pas omettre de détails significatifs : tips, ressources, bonnées idées, ou tout autre détail de valeur. 
        Le but est d'apprendre en utilisant ce résumé.
        Structure le résumé de manière claire et concise, en utilisant des phrases complètes et en évitant les répétitions inutiles.

        Si le sujet de la vidéo est narratif, fais plus de place à la narration et au style, tout en gardant une structure claire et fluide, en étant le plus captivant possible.
        
        N'INVENTE JAMAIS D'INFORMATIONS, RESTE STRICTEMENT FIDÈLE AU TEXTE FOURNI.
        Morceau de transcription :
        "{text}"
        
        Résumé concis du morceau en {language} :
        """
        map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text", "language"])

        combine_prompt_template = """
        Tu es un assistant expert en synthèse de contenu. Plusieurs résumés partiels d'une longue transcription te sont fournis ci-dessous.
        Ta tâche est de les combiner en un résumé final unique, détaillé, fluide et cohérent en {language}.
        
        Si le sujet de la vidéo est pédagogique, le résumé final doit être bien structuré, facile à lire mais en faisant des phrases complètes, et couvrir tous les sujets importants abordés dans la vidéo.
        N'hésite pas à utiliser des listes à puces pour les points clés.
        Assure-toi d'inclure les informations importantes et de ne pas omettre de détails significatifs : tips, ressources, bonnées idées, ou tout autre détail de valeur. 

        Si le sujet de la vidéo est narratif, fais plus de place à la narration et au style, tout en gardant une structure claire et fluide, en étant le plus captivant possible.

        Résumés partiels :
        "{text}"
        
        Résumé final détaillé et structuré en {language} :
        """
        combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text", "language"])

        # Le "collapse_prompt" est utilisé pour combiner les résumés intermédiaires
        # si les résultats de l'étape "map" sont trop volumineux pour le "combine_prompt" final.
        collapse_prompt_template = """Tu es un assistant expert en synthèse de contenu.
        Plusieurs résumés partiels te sont fournis. Combine-les en un unique résumé intermédiaire cohérent en {language}.

        Résumés partiels :
        "{text}"
        
        Résumé combiné :
        """
        collapse_prompt = PromptTemplate(template=collapse_prompt_template, input_variables=["text", "language"])

        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            collapse_prompt=collapse_prompt, # Ajout du prompt pour l'étape de "collapse"
            verbose=True 
        )
        
        summary = chain.invoke({"input_documents": docs, "language": language})
        
        return str(summary['output_text']), None

    except Exception as e:
        return None, f"Erreur lors de la génération du résumé : {e}"