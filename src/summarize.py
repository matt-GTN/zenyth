# /sophia/src/summarize.py
import os
from langchain_openai import ChatOpenAI
from langchain.schema.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env", override=True)


def summarize_text(transcript: str) -> tuple[str | None, str | None]:
    """
    Génère un résumé d'un texte donné en utilisant une stratégie Map-Reduce pour les longs textes.
    """
    try:
        # Initialisation du LLM (pas de changement ici)
        llm = ChatOpenAI(
            model="deepseek/deepseek-chat-v3-0324:free",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            request_timeout=600, 
            default_headers={
                "HTTP-Referer": os.getenv("YOUR_SITE_URL", "http://localhost:8501"),
                "X-Title": os.getenv("YOUR_SITE_NAME", "Agent Resume YouTube"),
            }
        )
        print(os.getenv("OPENROUTER_API_KEY"))

        # 1. Découper le texte en morceaux
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=500)
        docs = text_splitter.create_documents([transcript])
        
        # Si le texte est court, on n'a pas besoin de Map-Reduce
        if len(docs) == 1:
            print("--- Texte court, résumé direct ---")
            # Tu peux garder ton prompt simple ici si tu veux
            prompt = f"""Rédige un résumé concis en français avec des points clés pour la transcription suivante:\n\n{transcript}\n\nRésumé :"""
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content, None

        # 2. Utiliser une chaîne Map-Reduce de LangChain
        print(f"--- Texte long, stratégie Map-Reduce sur {len(docs)} morceaux ---")
        # LangChain fournit des prompts par défaut, mais tu peux les personnaliser
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        
        summary = chain.invoke(docs) # LangChain gère les appels multiples
        
        return summary['output_text'], None

    except Exception as e:
        return None, f"Erreur lors de la génération du résumé : {e}"