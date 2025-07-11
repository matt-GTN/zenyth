"""
Custom exceptions for Sophia
"""

class SophiaError(Exception):
    """Base exception for Sophia"""
    pass

class TranscriptError(SophiaError):
    """Error while retrieving transcript"""
    pass

class SummarizationError(SophiaError):
    """Error during summary generation"""
    pass

class ConfigurationError(SophiaError):
    """Configuration error"""
    pass

class APIError(SophiaError):
    """External API error"""
    pass 