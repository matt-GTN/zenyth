# /backend/src/video_tools.py
import time
import random
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, RequestBlocked, TranscriptList
from youtube_transcript_api.proxies import WebshareProxyConfig
from typing import Optional, Tuple
from config import Config

def _get_api_client() -> YouTubeTranscriptApi:
    """Crée une instance cliente de l'API avec la configuration du proxy."""
    proxy_config = None
    if Config.WEBSHARE_PROXY_USERNAME and Config.WEBSHARE_PROXY_PASSWORD:
        proxy_config = WebshareProxyConfig(
            proxy_username=Config.WEBSHARE_PROXY_USERNAME,
            proxy_password=Config.WEBSHARE_PROXY_PASSWORD,
            retries_when_blocked=Config.WEBSHARE_RETRIES
        )
    return YouTubeTranscriptApi(proxy_config=proxy_config)

def get_video_transcript(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Récupère la transcription d'une vidéo.
    Tente d'abord de trouver une transcription en français ou anglais.
    Si non disponible, se rabat sur la première transcription trouvée.
    
    Retourne:
        Tuple[Optional[str], Optional[str]]: (texte de la transcription, message d'erreur)
    """
    try:
        api_client = _get_api_client()
        
        transcript_list = api_client.list(video_id)
        transcript_to_fetch = None
        
        try:
            transcript_to_fetch = transcript_list.find_transcript(['fr', 'en'])
        except NoTranscriptFound:
            print("No transcript in preferred languages (fr, en). Falling back to the first available.")
            try:
                transcript_to_fetch = next(iter(transcript_list))
            except StopIteration:
                raise NoTranscriptFound(video_id, ['any'], transcript_list)

        print(f"Fetching transcript in '{transcript_to_fetch.language_code}'...")
        fetched_transcript = transcript_to_fetch.fetch()
        
        # --- CORRECTION DE LA LIGNE POSANT PROBLÈME ---
        # On utilise segment.text au lieu de segment['text']
        transcript_text = " ".join(segment.text for segment in fetched_transcript)
        
        print("Transcript successfully retrieved!")
        return transcript_text, None

    except RequestBlocked as rb:
        error_message = f"Failed to retrieve after {Config.WEBSHARE_RETRIES} proxy attempts. Error: {rb}"
        print(error_message)
        return None, error_message
        
    except TranscriptsDisabled:
        error_message = "Transcripts are disabled for this video. Unfortunately, we cannot summarize that for you."
        print(error_message)
        return None, error_message
        
    except NoTranscriptFound:
        error_message = "No transcript could be found for this video in any language."
        print(error_message)
        return None, error_message
        
    except Exception as e:
        error_message = f"Unexpected error while retrieving transcript: {e}"
        print(f"Unexpected error: {e}")
        return None, error_message

def extract_video_id(youtube_url: str) -> Optional[str]:
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split('&')[0]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1].split('?')[0]
    return None