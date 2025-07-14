# /zenyth/backend/src/summarize.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time
from typing import Optional, Tuple
from config import Config, create_llm_instance
from src.exceptions import SummarizationError

def get_direct_summary_prompt(summary_length: str) -> str:
    """Returns the appropriate prompt template for direct summarization based on the summary length."""
    return """Your task is to act as an expert educational summarizer.
Create a {summary_length}, well-structured summary of the following transcript. The goal is to create a summary that is easy to learn from.

**CRITICAL INSTRUCTIONS:**
1.  **Structure the summary logically:** Use headings, subheadings, and bullet points to organize the information clearly.
2.  **Highlight key information:** Use 'strong' markdown (e.g., **key concept**) to emphasize the most important concepts, actionable tips, key data, and critical terms.

Summary length guidelines:
- brief: A very concise summary in 2-3 sentences capturing only the main point.
- short: A paragraph covering the key points.
- standard: A balanced summary with main points and some supporting details, organized with headings.
- detailed: A comprehensive summary with main points, important details, and clear structure.
- comprehensive: A thorough summary with extensive details, nuances, and a well-defined structure.

Transcript:
---
{transcript}
---
A {summary_length}, well-structured summary in {language}:"""

def get_map_prompt_template(summary_length: str) -> str:
    """Returns the appropriate map prompt template based on the summary length."""
    return """You are an expert assistant acting as an educational summarizer for a long document. Your goal is to create a structured {summary_length} summary of the following chunk of a transcript.

**CRITICAL INSTRUCTIONS:**
1.  **Extract and structure:** Identify and extract all key points, data, and tips. Present them clearly using bullet points or short paragraphs.
2.  **Highlight key information:** Use 'strong' markdown (e.g., **key insight**) to emphasize the most important concepts, data, or actionable advice within this chunk.

Summary length guidelines:
- brief: Extract only the single most essential point from this chunk.
- short: Extract the key points from this chunk as concise bullet points.
- standard: Extract the main points and supporting details, organized logically.
- detailed: Extract the main points and all important details with clear structure.
- comprehensive: Extract all significant information and nuances in a structured format.

Transcript chunk:
---
"{text}"
---
A {summary_length}, structured summary of the chunk in {language}:"""

def get_combine_prompt_template(summary_length: str) -> str:
    """Returns the appropriate combine prompt template based on the summary length."""
    return """You are an expert content synthesizer and educational summarizer. You are provided with several partial summaries from a long transcript. Your task is to synthesize them into a single, coherent, and well-structured {summary_length} final summary. The ultimate goal is to produce a summary that someone can learn from.

**CRITICAL INSTRUCTIONS:**
1.  **Synthesize and structure:** Combine the information from the partial summaries into a unified document. Do not just list them. Create a logical flow with headings, subheadings, and bullet points.
2.  **Remove redundancy:** Eliminate overlapping information to create a concise and clean final text.
3.  **Highlight key information:** Review all points and use 'strong' markdown (e.g., **critical finding**) to emphasize the most important overall concepts, actionable advice, and key data from across all summaries.

Summary length guidelines:
- brief: A very concise summary in 2-3 sentences capturing only the main point.
- short: A short paragraph covering the key points.
- standard: A balanced summary with main points and supporting details, organized with headings.
- detailed: A comprehensive summary with main points, important details, and a clear, logical structure.
- comprehensive: A thorough summary with extensive details, nuances, and a well-defined structure.

Partial summaries:
---
"{text}"
---
A single, {summary_length}, well-structured final summary in {language}:"""

def get_collapse_prompt_template(summary_length: str) -> str:
    """Returns the appropriate collapse prompt template based on the summary length."""
    return """You are an expert summarizer tasked with consolidating intermediate summaries into a more refined, single summary. Combine the following summaries into a single, coherent, and well-structured {summary_length} intermediate summary.

**CRITICAL INSTRUCTIONS:**
1.  **Merge and structure:** Combine the key information from the provided summaries. Organize the result logically, perhaps using bullet points for clarity.
2.  **Refine and condense:** Remove redundant points and rephrase for better flow and conciseness.
3.  **Highlight key information:** Use 'strong' markdown (e.g., **key term**) to highlight the most important concepts and terms that should be preserved in the next stage of summarization.

Summary length guidelines:
- brief: A very concise summary in 2-3 sentences capturing the main point.
- short: A short paragraph covering the key points.
- standard: A balanced summary with main points and some supporting details.
- detailed: A comprehensive summary with main points and important details.
- comprehensive: A thorough summary with extensive details and nuances.

Summaries to combine:
---
"{text}"
---
A single, {summary_length}, combined summary in {language}:"""

def summarize_text(transcript: str, language: str = "english", summary_length: str = "standard") -> Tuple[Optional[str], Optional[str]]:
    """
    Generates a summary of a given text using a Map-Reduce strategy for long texts.
    The summary_length parameter controls the level of detail in the summary.
    """
    start_time = time.time()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting summarization for a {summary_length} summary.")
    try:
        if not transcript or not transcript.strip():
            return None, "The text to summarize is empty or contains only spaces."
        
        llm = create_llm_instance()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        docs = text_splitter.create_documents([transcript])
        
        # --- PROMPT FOR SHORT TEXT ---
        if len(docs) == 1:
            print(f"--- Short text, direct {summary_length} summary ---")
            prompt_template = ChatPromptTemplate.from_template(
                get_direct_summary_prompt(summary_length)
            )
            chain = prompt_template | llm | StrOutputParser()
            summary = chain.invoke({"transcript": transcript, "language": language, "summary_length": summary_length})
            end_time = time.time()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Direct summarization finished in {end_time - start_time:.2f} seconds.")
            return summary, None

        # --- PROMPTS FOR MAP-REDUCE ---
        print(f"--- Long text, Map-Reduce strategy on {len(docs)} chunks with {summary_length} detail level ---")
        
        map_prompt = PromptTemplate.from_template(
            get_map_prompt_template(summary_length)
        )
        
        combine_prompt = PromptTemplate.from_template(
            get_combine_prompt_template(summary_length)
        )
        
        collapse_prompt = PromptTemplate.from_template(
            get_collapse_prompt_template(summary_length)
        )

        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            collapse_prompt=collapse_prompt,
            verbose=True,
            token_max=4096
        )
        
        result = chain.invoke({"input_documents": docs, "language": language, "summary_length": summary_length})
        end_time = time.time()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Map-Reduce summarization finished in {end_time - start_time:.2f} seconds.")
        return str(result['output_text']), None

    except ValueError as e: # Catch specific config errors
        print(f"Configuration error: {e}")
        return None, str(e)
    except Exception as e:
        end_time = time.time()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error during summary generation after {end_time - start_time:.2f} seconds: {e}")
        # On peut utiliser nos exceptions custom ici
        return None, str(SummarizationError(f"An unexpected error occurred: {e}"))