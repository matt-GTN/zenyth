# tools.py
from langchain_core.tools import tool
from typing import Optional, Tuple
from src.video_tools import extract_video_id, get_video_transcript
from src.summarize import summarize_text
from src.translation import translate_text

# Le décorateur @tool transforme automatiquement tes fonctions en outils LangChain
# Il utilise les annotations de type et la docstring pour la description.

@tool
def extract_id_tool(youtube_url: str) -> Optional[str]:
    """Prend une URL YouTube complète et extrait l'identifiant unique de la vidéo."""
    return extract_video_id(youtube_url)

@tool
def get_transcript_tool(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Récupère la transcription textuelle d'une vidéo à partir de son ID. Gère les cas où la transcription est absente ou désactivée."""
    return get_video_transcript(video_id)

@tool
def summarize_text_tool(transcript: str, language: str = "english", summary_length: str = "standard") -> Tuple[Optional[str], Optional[str]]:
    """Takes a long text (like a transcript) and summarizes it concisely with the specified level of detail."""
    return summarize_text(transcript, language, summary_length)

@tool
def translate_text_tool(text: str, target_language: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Translates a given text into the specified target language.
    This is a final quality check to ensure the output is in the correct language.
    """
    return translate_text(text=text, target_language=target_language)