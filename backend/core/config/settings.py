from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "AIRMS"
    VERSION: str = "2.0.0"
    
    # Database
    MONGODB_URI: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # LLM Providers
    GROQ_API_KEY: str
    OPENAI_API_KEY: str | None = None
    
    # Risk Detection
    MIN_RISK_SCORE: float = 0.0
    MAX_RISK_SCORE: float = 10.0
    HIGH_RISK_THRESHOLD: float = 7.0
    MEDIUM_RISK_THRESHOLD: float = 4.0
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()