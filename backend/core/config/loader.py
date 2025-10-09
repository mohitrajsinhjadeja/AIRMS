from pathlib import Path
from typing import Dict, Any
import yaml
import os
from pydantic import BaseSettings

class AirmsConfig(BaseSettings):
    # Application
    APP_NAME: str = "AIRMS+"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    MONGODB_URI: str
    MONGODB_DB: str = "airms"
    DB_POOL_SIZE: int = 5

    # AI Services
    GROQ_API_KEY: str
    GEMINI_API_KEY: str | None = None
    AI_ROUTING_STRATEGY: str = "cost_optimized"
    GROQ_TRAFFIC_PERCENTAGE: int = 80
    GEMINI_TRAFFIC_PERCENTAGE: int = 20

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True

def load_config() -> AirmsConfig:
    """Load configuration based on environment"""
    env = os.getenv('APP_ENV', 'dev')
    config_path = Path(__file__).parent / 'environments' / f'{env}.yaml'
    
    # Load YAML config
    with open(config_path) as f:
        yaml_config = yaml.safe_load(f)
    
    # Update environment variables with YAML config
    for key, value in yaml_config.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                env_key = f"AIRMS_{key.upper()}_{subkey.upper()}"
                if env_key not in os.environ:
                    os.environ[env_key] = str(subvalue)
        else:
            env_key = f"AIRMS_{key.upper()}"
            if env_key not in os.environ:
                os.environ[env_key] = str(value)
                
    return AirmsConfig()