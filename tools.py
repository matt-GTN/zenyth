# tools.py
from langchain_core.tools import tool
from src.video_tools import extract_video_id, get_video_transcript
from src.summarize import summarize_text

# Le décorateur @tool transforme automatiquement tes fonctions en outils LangChain
# Il utilise les annotations de type et la docstring pour la description.

@tool
def extract_id_tool(youtube_url: str) -> str | None:
    """Prend une URL YouTube complète et extrait l'identifiant unique de la vidéo."""
    return extract_video_id(youtube_url)

@tool
def get_transcript_tool(video_id: str) -> tuple[str | None, str | None]:
    """Récupère la transcription textuelle d'une vidéo à partir de son ID. Gère les cas où la transcription est absente ou désactivée."""
    return get_video_transcript(video_id)

@tool
def summarize_text_tool(transcript: str) -> tuple[str | None, str | None]:
    """Prend un long texte (comme une transcription) et le résume de manière concise."""
    return summarize_text(transcript)