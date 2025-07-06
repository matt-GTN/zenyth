# src/video_tools.py
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def extract_video_id(youtube_url: str) -> str | None:
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split('&')[0]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1].split('?')[0]
    return None

def get_video_transcript(video_id: str) -> tuple[str | None, str | None]:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr', 'en'])
        transcript_text = " ".join([d['text'] for d in transcript_list])
        return transcript_text, None
    except TranscriptsDisabled:
        return None, "Les transcriptions sont désactivées pour cette vidéo."
    except NoTranscriptFound:
        return None, "Aucune transcription trouvée pour cette vidéo (français ou anglais)."
    except Exception as e:
        return None, f"Erreur inattendue lors de la récupération de la transcription : {e}"