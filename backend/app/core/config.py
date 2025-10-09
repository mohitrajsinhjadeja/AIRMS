"""
Configuration settings for AIRMS+ MongoDB backend
"""

import os
import secrets
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
class Settings(BaseSettings):
    """
    🛡️ AIRMS+ Configuration System
    Comprehensive settings for AI-powered risk detection and misinformation analysis
    """
    
    # === APPLICATION SETTINGS ===
    APP_NAME: str = "AIRMS+ AI Risk Mitigation System"
    VERSION: str = "2.0.0"  # Added VERSION attribute
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # === SERVER SETTINGS ===
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # === CORS SETTINGS ===
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # === MONGODB SETTINGS ===
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://airms:airms@cluster0.it4r7ez.mongodb.net/airms?retryWrites=true&w=majority&appName=Cluster0")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "airms")
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    MONGODB_MAX_IDLE_TIME_MS: int = 30000
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 5000
    
    # === AI API SETTINGS ===
    # Gemini API (Deep Reasoning)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_MAX_TOKENS: int = 2048
    GEMINI_TEMPERATURE: float = 0.1
    
    # Groq API (Fast Filtering)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-8b-8192"
    GROQ_MAX_TOKENS: int = 1024
    GROQ_TEMPERATURE: float = 0.0
    
    # AI Routing Strategy
    AI_ROUTING_STRATEGY: str = "cost_optimized"  # cost_optimized, quality_first, speed_first
    GROQ_TRAFFIC_PERCENTAGE: int = 80  # 80% Groq for cost optimization
    
    # === EXTERNAL API SETTINGS ===
    # Google Fact Check API
    GOOGLE_FACT_CHECK_API_KEY: Optional[str] = None
    GOOGLE_FACT_CHECK_ENABLED: bool = True
    
    # NewsAPI
    NEWSAPI_KEY: Optional[str] = None
    NEWSAPI_ENABLED: bool = True
    
    # Wikipedia API
    WIKIPEDIA_ENABLED: bool = True
    WIKIPEDIA_LANGUAGE: str = "en"
    
    # === SECURITY SETTINGS ===
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days for refresh token
    API_KEY_PREFIX: str = "airms_"
    
    # PII Security Settings
    PII_SALT_LENGTH: int = 32
    PII_ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    PII_TOKEN_EXPIRY_DAYS: int = 90  # 90-day retention policy
    PII_HASH_ALGORITHM: str = "sha256"  # Hash algorithm for PII tokenization
    PII_ENABLE_REVERSE_LOOKUP: bool = True  # Enable reverse lookup for detokenization
    
    # === RISK DETECTION SETTINGS ===
    # Risk Scoring Weights
    BIAS_WEIGHT: float = 0.25
    HALLUCINATION_WEIGHT: float = 0.30
    PII_WEIGHT: float = 0.30
    ADVERSARIAL_WEIGHT: float = 0.15
    
    # Risk Thresholds
    LOW_RISK_THRESHOLD: float = 0.3
    MEDIUM_RISK_THRESHOLD: float = 0.6
    HIGH_RISK_THRESHOLD: float = 0.8
    
    # Feature Flags
    ENABLE_BIAS_DETECTION: bool = True
    ENABLE_HALLUCINATION_DETECTION: bool = True
    ENABLE_PII_DETECTION: bool = True
    ENABLE_ADVERSARIAL_DETECTION: bool = True
    ENABLE_MISINFORMATION_DETECTION: bool = True
    
    # === PII PATTERNS ===
    PII_PATTERNS: Dict[str, str] = {
        # Indian Aadhaar (12 digits)
        "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        
        # Indian PAN (5 letters, 4 digits, 1 letter)
        "pan": r"\b[A-Z]{5}\d{4}[A-Z]\b",
        
        # Phone numbers (Indian format)
        "phone": r"\b(?:\+91[-.\s]?)?[6-9]\d{9}\b",
        
        # Email addresses
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        
        # Credit card numbers (basic pattern)
        "credit_card": r"\b(?:\d{4}[-.\s]?){3}\d{4}\b",
        
        # Bank account numbers (basic pattern)
        "bank_account": r"\b\d{9,18}\b",
        
        # IFSC codes (Indian banking)
        "ifsc": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
        
        # Names (basic pattern - 2+ words starting with capital)
        "name": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",
        
        # Addresses (basic pattern)
        "address": r"\b\d+[A-Za-z\s,.-]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Place|Pl)\b"
    }
    
    # Indian Context Bias Keywords
    INDIAN_BIAS_KEYWORDS: Dict[str, List[str]] = {
        "political": ["BJP", "Congress", "AAP", "Modi", "Gandhi", "left-wing", "right-wing"],
        "religious": ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "secular"],
        "caste": ["Brahmin", "Kshatriya", "Vaishya", "Shudra", "Dalit", "OBC", "reservation"],
        "regional": ["North Indian", "South Indian", "Punjabi", "Bengali", "Marathi", "Tamil"],
        "linguistic": ["Hindi", "English", "regional language", "mother tongue"],
        "economic": ["rich", "poor", "middle class", "elite", "underprivileged"]
    }
    
    # === MISINFORMATION DETECTION SETTINGS ===
    MISINFORMATION_CONFIDENCE_THRESHOLD: float = 0.7
    FACT_CHECK_TIMEOUT_SECONDS: int = 10
    ENABLE_EDUCATIONAL_CONTENT: bool = True
    
    # === CORS SETTINGS ===
    CORS_ORIGINS: List[str] = ["https://airms-frontend-1013218741719.us-central1.run.app", "http://localhost:3000", "http://localhost:5173"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]  # Allow all methods
    CORS_HEADERS: List[str] = ["*"]  # Allow all headers
    CORS_MAX_AGE: int = 600  # 10 minutes
    
    # === LOGGING SETTINGS ===
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "logs/airms_plus.log"
    
    # === RATE LIMITING ===
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # === BACKGROUND TASKS ===
    ENABLE_BACKGROUND_TASKS: bool = True
    TASK_QUEUE_SIZE: int = 1000
    MAX_CONCURRENT_TASKS: int = 10
    
    # === ANALYTICS SETTINGS ===
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_RETENTION_DAYS: int = 90
    ENABLE_REAL_TIME_STATS: bool = True
    STATS_UPDATE_INTERVAL_SECONDS: int = 30
    
    # === CACHE SETTINGS ===
    ENABLE_REDIS_CACHE: bool = False
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 3600
    
    # Model Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_assignment=True,
        # You can add other config options here
        extra="allow",  # Allow extra fields
        validate_default=True
    )

    @validator('CORS_ORIGINS', pre=True)
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    def validate_ai_apis(self) -> Dict[str, bool]:
        """Validate AI API configurations"""
        return {
            "gemini_configured": bool(self.GEMINI_API_KEY),
            "groq_configured": bool(self.GROQ_API_KEY),
            "fact_check_configured": bool(self.GOOGLE_FACT_CHECK_API_KEY)
        }
    
    def get_ai_routing_config(self) -> Dict[str, Any]:
        """Get AI routing configuration"""
        if self.AI_ROUTING_STRATEGY == "cost_optimized":
            return {"groq_percentage": self.GROQ_TRAFFIC_PERCENTAGE, "gemini_percentage": 100 - self.GROQ_TRAFFIC_PERCENTAGE}
        elif self.AI_ROUTING_STRATEGY == "quality_first":
            return {"groq_percentage": 20, "gemini_percentage": 80}
        else:  # speed_first
            return {"groq_percentage": 90, "gemini_percentage": 10}
    
    def get_risk_weights(self) -> Dict[str, float]:
        """Get risk detection weights"""
        return {
            "bias": self.BIAS_WEIGHT,
            "hallucination": self.HALLUCINATION_WEIGHT,
            "pii": self.PII_WEIGHT,
            "adversarial": self.ADVERSARIAL_WEIGHT
        }
    
    def get_risk_thresholds(self) -> Dict[str, float]:
        """Get risk assessment thresholds"""
        return {
            "low": self.LOW_RISK_THRESHOLD,
            "medium": self.MEDIUM_RISK_THRESHOLD,
            "high": self.HIGH_RISK_THRESHOLD
        }
    
    def get_pii_config(self) -> Dict[str, Any]:
        """Get PII safety configuration"""
        return {
            "salt_length": self.PII_SALT_LENGTH,
            "token_expiry_days": self.PII_TOKEN_EXPIRY_DAYS,
            "patterns": self.PII_PATTERNS,
            "encryption_enabled": True,
            "permission_required": True,
            "hash_algorithm": self.PII_HASH_ALGORITHM,
            "enable_reverse_lookup": self.PII_ENABLE_REVERSE_LOOKUP
        }


# Global settings instance
settings = Settings()

# Convenience functions
def validate_ai_apis() -> Dict[str, bool]:
    """Validate AI API configurations"""
    return settings.validate_ai_apis()

def get_ai_routing_config() -> Dict[str, Any]:
    """Get AI routing configuration"""
    return settings.get_ai_routing_config()

def get_risk_weights() -> Dict[str, float]:
    """Get risk detection weights"""
    return settings.get_risk_weights()

def get_risk_thresholds() -> Dict[str, float]:
    """Get risk assessment thresholds"""
    return settings.get_risk_thresholds()

def get_pii_config() -> Dict[str, Any]:
    """Get PII safety configuration"""
    return settings.get_pii_config()

# Environment-specific configurations
def is_development() -> bool:
    return settings.ENVIRONMENT == "development"

def is_production() -> bool:
    return settings.ENVIRONMENT == "production"

def get_mongodb_url() -> str:
    """Get MongoDB URL with proper formatting"""
    return settings.MONGODB_URL

def get_log_config() -> Dict[str, Any]:
    """Get logging configuration"""
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.LOG_FORMAT,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
        },
    }
    
    # Add file handler if log file is specified
    if settings.LOG_FILE:
        # Create logs directory if it doesn't exist
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(exist_ok=True)
        
        config["handlers"]["file"] = {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": settings.LOG_FILE,
        }
        config["root"]["handlers"].append("file")
    
    return config
