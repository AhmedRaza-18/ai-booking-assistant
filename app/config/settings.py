"""
Configuration Settings
Loads environment variables from .env file
Updated to support multiple AI providers (Groq, OpenRouter, OpenAI)
"""
from pydantic_settings import BaseSettings
from typing import Optional, Literal

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # ============================================
    # APP INFO
    # ============================================
    APP_NAME: str = "AI Booking Assistant"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # ============================================
    # AI PROVIDER SETTINGS
    # ============================================
    
    # Which AI provider to use
    AI_PROVIDER: Literal["groq", "openrouter", "openai"] = "groq"
    
    # Groq Settings (FREE & FAST - Recommended)
    GROQ_API_KEY: Optional[str] = None
    
    # OpenRouter Settings (BACKUP - Multiple models)
    OPENROUTER_API_KEY: Optional[str] = None
    
    # OpenAI Settings (OPTIONAL - Most expensive)
    OPENAI_API_KEY: Optional[str] = None
    
    # AI Model to use (changes based on provider)
    AI_MODEL: str = "llama-3.1-70b-versatile"
    
    # AI Response Settings
    AI_TEMPERATURE: float = 0.7  # 0.0 = deterministic, 1.0 = creative
    AI_MAX_TOKENS: int = 1000    # Maximum response length
    
    # ============================================
    # TWILIO SETTINGS (Voice & SMS)
    # ============================================
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # ============================================
    # GOOGLE CALENDAR SETTINGS
    # ============================================
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = "credentials.json"
    
    # ============================================
    # GOOGLE SHEETS SETTINGS
    # ============================================
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = "google-credentials.json"
    GOOGLE_SHEET_ID: str = ""
    
    # ============================================
    # DATABASE SETTINGS
    # ============================================
    DATABASE_URL: str = "sqlite:///./data/bookings.db"
    
    # ============================================
    # SERVER SETTINGS
    # ============================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    class Config:
        """
        Pydantic config
        Tells it to load from .env file
        """
        env_file = ".env"
        case_sensitive = True


# Create a single instance to use throughout the app
settings = Settings()


# Helper function to check if AI is configured
def is_ai_configured() -> bool:
    """
    Check if at least one AI provider is configured
    Returns True if any API key is set
    """
    if settings.AI_PROVIDER == "groq" and settings.GROQ_API_KEY:
        return True
    elif settings.AI_PROVIDER == "openrouter" and settings.OPENROUTER_API_KEY:
        return True
    elif settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return True
    return False


# Helper function to get current AI provider info
def get_ai_provider_info() -> dict:
    """
    Returns information about the configured AI provider
    Useful for debugging and logging
    """
    return {
        "provider": settings.AI_PROVIDER,
        "model": settings.AI_MODEL,
        "configured": is_ai_configured(),
        "temperature": settings.AI_TEMPERATURE,
        "max_tokens": settings.AI_MAX_TOKENS
    }