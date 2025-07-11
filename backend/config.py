"""
Configuration centralisée pour Zenyth
"""
import os
import itertools
import threading
from typing import Optional, List

class Config:
    """Configuration de l'application Zenyth"""
    
    # API Keys
    OPENROUTER_API_KEYS_STR: str = os.getenv("OPENROUTER_API_KEYS", "")
    OPENROUTER_API_KEYS: List[str] = [key.strip() for key in OPENROUTER_API_KEYS_STR.split(',') if key.strip()]
    
    # Site Configuration
    SITE_URL: str = os.getenv("YOUR_SITE_URL", "tryzenyth.app")
    SITE_NAME: str = os.getenv("YOUR_SITE_NAME", "Zenyth")
    
    # Model Configuration
    MODEL_NAME: str = "deepseek/deepseek-chat-v3-0324:free"
    TEMPERATURE: float = 0.7
    REQUEST_TIMEOUT: int = 900
    
    # Text Processing
    CHUNK_SIZE: int = 20000
    CHUNK_OVERLAP: int = 800
    
    @classmethod
    def validate(cls) -> bool:
        """Valide la configuration"""
        # Updated validation check
        if not cls.OPENROUTER_API_KEYS:
            raise ValueError("OPENROUTER_API_KEYS is required in the .env file (comma-separated).")
        return True
    
    @classmethod
    def get_llm_config(cls, api_key: str) -> dict:
        """Returns a configuration dictionary for the LLM, requiring a specific API key."""
        return {
            "model": cls.MODEL_NAME,
            "api_key": api_key, # Use the provided key
            "base_url": "https://openrouter.ai/api/v1",
            "temperature": cls.TEMPERATURE,
            "request_timeout": cls.REQUEST_TIMEOUT,
            "default_headers": {
                "HTTP-Referer": cls.SITE_URL,
                "X-Title": cls.SITE_NAME,
            }
        }

# 1. Check if keys are available
if not Config.OPENROUTER_API_KEYS:
    print("⚠️ WARNING: OPENROUTER_API_KEYS environment variable not set or empty. API calls will fail.")
    key_cycle = itertools.cycle([""]) # Fails gracefully
else:
    print(f"✅ Found {len(Config.OPENROUTER_API_KEYS)} API keys. Rotation is enabled.")
    # 2. Create an iterator that cycles through the keys endlessly
    key_cycle = itertools.cycle(Config.OPENROUTER_API_KEYS)

# 3. Create a lock to make the key rotation thread-safe
key_lock = threading.Lock()

def get_rotating_api_key() -> str:
    """
    Safely retrieves the next API key from the cycle.
    This function is thread-safe.
    """
    with key_lock:
        # Get the next key from our cycling iterator
        key = next(key_cycle)
        print(f"🔄 Using API key ending in: ...{key[-4:]}")
        return key