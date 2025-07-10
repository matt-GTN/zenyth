# src/video_tools.py
import os
import time
import random
# On importe la classe principale et la classe de config pour Webshare
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, RequestBlocked
from youtube_transcript_api.proxies import WebshareProxyConfig
from typing import Optional, Tuple

# La configuration reste la même
WEBSHARE_PROXY_USERNAME = os.getenv("WEBSHARE_PROXY_USERNAME")
WEBSHARE_PROXY_PASSWORD = os.getenv("WEBSHARE_PROXY_PASSWORD")
RETRIES_WHEN_BLOCKED = 10 # WebshareProxyConfig gère ça nativement

# BROWSER_HEADERS ne sont plus nécessaires, la bibliothèque a des headers par défaut
# et la config du proxy gère le plus important ("Connection: close")

# === DÉBUT DE LA CORRECTION MAJEURE ===

def _get_api_client() -> YouTubeTranscriptApi:
    """Crée une instance cliente de l'API avec la configuration du proxy."""
    proxy_config = None
    if WEBSHARE_PROXY_USERNAME and WEBSHARE_PROXY_PASSWORD:
        proxy_config = WebshareProxyConfig(
            proxy_username=WEBSHARE_PROXY_USERNAME,
            proxy_password=WEBSHARE_PROXY_PASSWORD,
            retries_when_blocked=RETRIES_WHEN_BLOCKED
        )
    
    # On crée une instance de la classe avec notre configuration.
    # C'est la méthode officielle et la plus propre.
    return YouTubeTranscriptApi(proxy_config=proxy_config)

def get_video_transcript(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Récupère la transcription en utilisant une instance configurée de l'API."""
    try:
        # 1. Obtenir une instance configurée du client API.
        # On pourrait le créer une seule fois et le réutiliser, mais en créer un nouveau 
        # à chaque appel garantit qu'il n'y a pas d'état partagé (plus sûr).
        api_client = _get_api_client()

        # 2. Utiliser la méthode .fetch() sur l'instance.
        # C'est la méthode moderne et recommandée par la doc.
        transcript = api_client.fetch(video_id, languages=["fr", "en"])
        
        # Le format de retour de .fetch() est une liste de segments.
        # On doit les joindre.
        transcript_text = " ".join(segment.text for segment in transcript)
        
        print("Transcription récupérée avec succès !")
        return transcript_text, None

    except RequestBlocked as rb:
        # La logique de retry est maintenant gérée en interne par la bibliothèque 
        # grâce à `retries_when_blocked` dans WebshareProxyConfig.
        # Si on arrive ici, c'est que toutes les tentatives ont échoué.
        print(f"Échec de la récupération après {RETRIES_WHEN_BLOCKED} tentatives de proxy. Erreur : {rb}")
        return None, str(rb)
        
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        # Gérer les cas où il n'y a tout simplement pas de transcription
        error_message = "Les transcriptions sont désactivées." if isinstance(e, TranscriptsDisabled) else "Aucune transcription trouvée (fr/en)."
        print(error_message)
        return None, error_message
        
    except Exception as e:
        # Capturer toutes les autres erreurs potentielles
        print(f"Erreur inattendue : {e}")
        return None, f"Erreur inattendue lors de la récupération de la transcription : {e}"

# La fonction extract_video_id ne change pas
def extract_video_id(youtube_url: str) -> Optional[str]:
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split('&')[0]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1].split('?')[0]
    return None
