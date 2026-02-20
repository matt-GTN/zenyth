# /backend/config.py
"""
Configuration centralisée pour Zenyth
"""
import os
import itertools
import threading
from typing import Optional, List, Dict
from pydantic import SecretStr
from langchain_openai import ChatOpenAI

class Config:
    """Classe de configuration pour l'application Zenyth."""
    
    # --- Clés API ---
    # Lit les clés depuis la variable d'environnement, les sépare par une virgule
    OPENROUTER_API_KEYS_STR: str = os.getenv("OPENROUTER_API_KEYS", "")
    OPENROUTER_API_KEYS: List[str] = [key.strip() for key in OPENROUTER_API_KEYS_STR.split(',') if key.strip()]
    
    # --- Configuration du proxy YouTube ---
    WEBSHARE_PROXY_USERNAME: Optional[str] = os.getenv("WEBSHARE_PROXY_USERNAME")
    WEBSHARE_PROXY_PASSWORD: Optional[str] = os.getenv("WEBSHARE_PROXY_PASSWORD")
    # Setting domain back to 'p.webshare.io' as Webshare handles country targeting via the username (e.g. username-rotate)
    WEBSHARE_PROXY_DOMAIN_NAME: str = "p.webshare.io"
    WEBSHARE_RETRIES: int = 10

    # --- Configuration du Site ---
    SITE_URL: str = os.getenv("YOUR_SITE_URL", "https://tryzenyth.app")
    SITE_NAME: str = os.getenv("YOUR_SITE_NAME", "Zenyth")
    
    # --- Configuration du Modèle LLM par défaut ---
    DEFAULT_MODEL_NAME: str = "google/gemini-2.5-flash-lite"  # Modèle OpenRouter par défaut
    DEFAULT_TEMPERATURE: float = 0.1
    DEFAULT_TIMEOUT: int = 1800 # Augmenté pour les longs résumés
    DEFAULT_BASE_URL: str = "https://openrouter.ai/api/v1"

    # --- Configuration du Traitement de Texte ---
    CHUNK_SIZE: int = 15000
    CHUNK_OVERLAP: int = 750
    
    @classmethod
    def get_default_headers(cls) -> Dict[str, str]:
        """Retourne les en-têtes HTTP par défaut pour les appels LLM."""
        return {
            "HTTP-Referer": cls.SITE_URL,
            "X-Title": cls.SITE_NAME,
        }

# --- Logique de Rotation des Clés API (Thread-Safe) ---

if not Config.OPENROUTER_API_KEYS:
    print("⚠️ WARNING: OPENROUTER_API_KEYS environment variable not set or empty. API calls will fail.")
    # Crée un cycle avec une chaîne vide pour que l'appli ne crash pas, mais les appels échoueront avec une erreur d'auth.
    key_cycle = itertools.cycle([""]) 
else:
    print(f"✅ Found {len(Config.OPENROUTER_API_KEYS)} API keys. Rotation is enabled.")
    key_cycle = itertools.cycle(Config.OPENROUTER_API_KEYS)

key_lock = threading.Lock()

def get_rotating_api_key() -> str:
    """Récupère de manière sûre la prochaine clé API du cycle (thread-safe)."""
    with key_lock:
        key = next(key_cycle)
        if key:
            print(f"🔄 Using API key ending in: ...{key[-4:]}")
        return key

# --- Usine de création de LLM (Nouveau & Centralisé) ---

def create_llm_instance(**kwargs) -> ChatOpenAI:
    """
    Crée et configure une instance de ChatOpenAI pour OpenRouter.
    C'est le point d'entrée unique pour obtenir un client LLM.
    Les `kwargs` peuvent surcharger les paramètres par défaut (ex: temperature, timeout).
    """
    api_key = get_rotating_api_key()
    if not api_key:
        # Cette erreur est plus claire et arrêtera le processus tôt.
        raise ValueError("No OpenRouter API key available. Check your .env file and OPENROUTER_API_KEYS variable.")

    # Paramètres par défaut tirés de la classe Config
    config = {
        "model": Config.DEFAULT_MODEL_NAME,
        "temperature": Config.DEFAULT_TEMPERATURE,
        "timeout": Config.DEFAULT_TIMEOUT,
        "api_key": SecretStr(api_key),
        "base_url": Config.DEFAULT_BASE_URL,
        "default_headers": Config.get_default_headers(),
    }

    # Met à jour la configuration avec les arguments fournis (kwargs)
    # Permet de surcharger la température pour la traduction, par exemple.
    config.update(kwargs)
    
    print(f"🤖  Creating LLM instance for model '{config['model']}' with temp {config['temperature']}.")
    return ChatOpenAI(**config)
