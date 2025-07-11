# /zenyth/backend/src/summarize.py
import os
from langchain_openai import ChatOpenAI
from langchain.schema.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from pydantic import SecretStr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import Optional, Tuple
from config import Config

# Récupération de la configuration LLM
llm_config = Config.get_llm_config()
llm = ChatOpenAI(**llm_config)

def summarize_text(transcript: str, language: str = "english") -> Tuple[Optional[str], Optional[str]]:
    """
    Génère un résumé d'un texte donné en utilisant une stratégie Map-Reduce pour les longs textes.
    """
    try:
        if not transcript or not transcript.strip():
            return None, "The text to summarize is empty or contains only spaces."
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return None, "Missing OpenRouter API key"
            
        llm = ChatOpenAI(
            model="deepseek/deepseek-chat-v3-0324:free",
            api_key=SecretStr(api_key),
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            timeout=1800, 
            default_headers={
                "HTTP-Referer": os.getenv("YOUR_SITE_URL", "http://localhost:3000"), # Note: le port par défaut de Next.js est 3000
                "X-Title": os.getenv("YOUR_SITE_NAME", "Zenyth"),
            }
        )

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=750)
        docs = text_splitter.create_documents([transcript])
        
        # --- PROMPT POUR LE TEXTE COURT (Amélioré) ---
        if len(docs) == 1:
            print("--- Texte court, résumé direct ---")
            prompt_template = ChatPromptTemplate.from_template(
                """Your task is to act as an expert educational summarizer.
Create a detailed, well-structured summary of the following transcript.

**CRITICAL INSTRUCTION: The final summary MUST be written in the following language: {language}**

Identify the main ideas and present them as clear, concise key points.
Ensure you include all important information and do not omit significant details: tips, resources, data, ideas, or any other valuable detail.
The goal is to learn from this summary.

Transcript:
---
{transcript}
---

Structured summary in {language}:"""
            )
            chain = prompt_template | llm | StrOutputParser()
            summary = chain.invoke({"transcript": transcript, "language": language})
            return summary, None

        # --- PROMPTS POUR MAP-REDUCE (Améliorés) ---
        print(f"--- Texte long, stratégie Map-Reduce sur {len(docs)} morceaux ---")

        # Étape MAP : Résumer chaque morceau individuellement
        map_prompt_template = """You are an expert assistant for summarizing parts of a longer document.
Your goal is to summarize the following chunk of a transcript.

**CRITICAL INSTRUCTION: Your summary output for this chunk MUST be in the following language: {language}**

Extract the key points and essential information. Include significant details like tips, resources, or data.
Remain strictly faithful to the provided text. DO NOT INVENT INFORMATION.

Transcript chunk:
---
"{text}"
---

Concise summary of the chunk in {language}:"""
        map_prompt = PromptTemplate.from_template(map_prompt_template)

        # Étape COMBINE : Assembler les résumés en un seul
        combine_prompt_template = """You are an expert content synthesizer. You are provided with several partial summaries from a long transcript.
Your task is to combine them into a single, detailed, fluid, and coherent final summary.

**CRITICAL INSTRUCTION: The final combined summary MUST be written in the following language: {language}**

The final summary should be well-structured, easy to read, and cover all important topics.
Use bullet points for key takeaways. Ensure you include all important information and significant details like tips, resources, or data.
If the content is narrative, focus on storytelling and style while maintaining a clear structure.

Partial summaries:
---
"{text}"
---

Detailed and structured final summary in {language}:"""
        combine_prompt = PromptTemplate.from_template(combine_prompt_template)
        
        # Le prompt "collapse" n'a pas besoin d'être aussi complexe.
        collapse_prompt_template = """Combine the following summaries into a single, coherent intermediate summary.
        
**CRITICAL INSTRUCTION: The output MUST be in the following language: {language}**

Summaries to combine:
---
"{text}"
---

Combined summary in {language}:"""
        collapse_prompt = PromptTemplate.from_template(collapse_prompt_template)

        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            collapse_prompt=collapse_prompt,
            verbose=True,
            # On s'assure que la langue est passée à chaque étape
            token_max=4096 # Pour le modèle `combine`, Deepseek free a une limite
        )
        
        result = chain.invoke({"input_documents": docs, "language": language})
        
        return str(result['output_text']), None

    except Exception as e:
        return None, f"Error during summary generation: {e}"