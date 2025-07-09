# src/video_tools.py
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, RequestBlocked
from youtube_transcript_api.proxies import WebshareProxyConfig
from typing import Optional, Tuple

# Configuration du proxy Webshare
WEBSHARE_PROXY_USERNAME = os.getenv("WEBSHARE_PROXY_USERNAME")
WEBSHARE_PROXY_PASSWORD = os.getenv("WEBSHARE_PROXY_PASSWORD")
# Pour l'offre Rotating Residential, le port HTTP 80 est recommandé
WEBSHARE_PROXY_PORT = int(os.getenv("WEBSHARE_PROXY_PORT", "80"))

# Nombre maximal de tentatives quand YouTube bloque une IP
RETRIES_WHEN_BLOCKED = 25


def _new_transcript_api() -> YouTubeTranscriptApi:
    """Crée une instance YouTubeTranscriptApi configurée avec un proxy rotatif.

    On crée une nouvelle instance à chaque appel pour forcer la rotation d'IP.
    """
    if WEBSHARE_PROXY_USERNAME and WEBSHARE_PROXY_PASSWORD:
        proxy_cfg = WebshareProxyConfig(
            proxy_username=WEBSHARE_PROXY_USERNAME,
            proxy_password=WEBSHARE_PROXY_PASSWORD,
            proxy_port=WEBSHARE_PROXY_PORT,
            retries_when_blocked=RETRIES_WHEN_BLOCKED,
        )
        return YouTubeTranscriptApi(proxy_config=proxy_cfg)
    # Fallback : pas de proxy
    return YouTubeTranscriptApi()

def extract_video_id(youtube_url: str) -> Optional[str]:
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split('&')[0]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1].split('?')[0]
    return None

def get_video_transcript(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    last_error: Optional[str] = None
    for _ in range(RETRIES_WHEN_BLOCKED):
        try:
            api = _new_transcript_api()
            transcript_list = api.get_transcript(video_id, languages=["fr", "en"])
            transcript_text = " ".join(d["text"] for d in transcript_list)
            return transcript_text, None
        except RequestBlocked as rb:
            last_error = str(rb)
            # On réessaie avec une nouvelle IP
            continue
        except TranscriptsDisabled:
            return None, "Les transcriptions sont désactivées pour cette vidéo."
        except NoTranscriptFound:
            return None, "Aucune transcription trouvée pour cette vidéo (français ou anglais)."
        except Exception as e:
            return None, f"Erreur inattendue lors de la récupération de la transcription : {e}"

    # Si on sort de la boucle, toutes les IP ont été bloquées
    return None, last_error or "Toutes les tentatives ont été bloquées par YouTube."