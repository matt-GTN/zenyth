# /zenyth/backend/src/summarize.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Optional, Tuple
from config import Config, create_llm_instance
from src.exceptions import SummarizationError, ConfigurationError

def summarize_text(transcript: str, language: str = "english") -> Tuple[Optional[str], Optional[str]]:
    """
    Génère un résumé d'un texte donné en utilisant une stratégie Map-Reduce pour les longs textes.
    """
    try:
        if not transcript or not transcript.strip():
            return None, "The text to summarize is empty or contains only spaces."
        
        # Plus besoin de créer le LLM manuellement. On appelle notre usine.
        # On utilise les paramètres par défaut (température 0.7, etc.)
        llm = create_llm_instance()

        # Le reste du code ne change presque pas
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE, 
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        docs = text_splitter.create_documents([transcript])
        
        # --- PROMPT POUR LE TEXTE COURT ---
        if len(docs) == 1:
            print("--- Texte court, résumé direct ---")
            prompt_template = ChatPromptTemplate.from_template(
                """Your task is to act as an expert educational summarizer.
Create a detailed, well-structured summary of the following transcript.
**CRITICAL INSTRUCTION: The final summary MUST be written in the following language: {language}**
Identify the main ideas and present them as clear, concise key points.
Ensure you include all important information and do not omit significant details: tips, resources, data, ideas, or any other valuable detail. The goal is to learn from this summary.
Transcript:
---
{transcript}
---
Structured summary in {language}:"""
            )
            chain = prompt_template | llm | StrOutputParser()
            summary = chain.invoke({"transcript": transcript, "language": language})
            return summary, None

        # --- PROMPTS POUR MAP-REDUCE ---
        print(f"--- Texte long, stratégie Map-Reduce sur {len(docs)} morceaux ---")
        map_prompt_template = """You are an expert assistant for summarizing parts of a longer document. Your goal is to summarize the following chunk of a transcript.
**CRITICAL INSTRUCTION: Your summary output for this chunk MUST be in the following language: {language}**
Extract the key points and essential information. Include significant details like tips, resources, or data. Remain strictly faithful to the provided text. DO NOT INVENT INFORMATION.
Transcript chunk:
---
"{text}"
---
Concise summary of the chunk in {language}:"""
        map_prompt = PromptTemplate.from_template(map_prompt_template)

        combine_prompt_template = """You are an expert content synthesizer. You are provided with several partial summaries from a long transcript. Your task is to combine them into a single, detailed, fluid, and coherent final summary.
**CRITICAL INSTRUCTION: The final combined summary MUST be written in the following language: {language}**
The final summary should be well-structured, easy to read, and cover all important topics. Use bullet points for key takeaways. Ensure you include all important information and significant details like tips, resources, or data. If the content is narrative, focus on storytelling and style while maintaining a clear structure.
Partial summaries:
---
"{text}"
---
Detailed and structured final summary in {language}:"""
        combine_prompt = PromptTemplate.from_template(combine_prompt_template)
        
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
            token_max=4096
        )
        
        result = chain.invoke({"input_documents": docs, "language": language})
        return str(result['output_text']), None

    except ValueError as e: # Catch specific config errors
        print(f"Configuration error: {e}")
        return None, str(e)
    except Exception as e:
        print(f"Error during summary generation: {e}")
        # On peut utiliser nos exceptions custom ici
        return None, str(SummarizationError(f"An unexpected error occurred: {e}"))