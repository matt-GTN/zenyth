"""
Exceptions personnalisées pour Sophia
"""

class SophiaError(Exception):
    """Exception de base pour Sophia"""
    pass

class VideoIDExtractionError(SophiaError):
    """Erreur lors de l'extraction de l'ID vidéo"""
    pass

class TranscriptError(SophiaError):
    """Erreur lors de la récupération de la transcription"""
    pass

class SummarizationError(SophiaError):
    """Erreur lors de la génération du résumé"""
    pass

class ConfigurationError(SophiaError):
    """Erreur de configuration"""
    pass

class APIError(SophiaError):
    """Erreur d'API externe"""
    pass 