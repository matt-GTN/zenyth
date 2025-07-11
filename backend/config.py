"""
Configuration centralisée pour Zenyth
"""
import os
from typing import Optional

class Config:
    """Configuration de l'application Zenyth"""
    
    # API Keys
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
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
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY est requis dans le fichier .env")
        return True
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """Retourne la configuration pour le LLM"""
        return {
            "model": cls.MODEL_NAME,
            "api_key": cls.OPENROUTER_API_KEY,
            "base_url": "https://openrouter.ai/api/v1",
            "temperature": cls.TEMPERATURE,
            "request_timeout": cls.REQUEST_TIMEOUT,
            "default_headers": {
                "HTTP-Referer": cls.SITE_URL,
                "X-Title": cls.SITE_NAME,
            }
        } 