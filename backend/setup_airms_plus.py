#!/usr/bin/env python3
"""
🛡️ AIRMS+ Interactive Setup Script
AI-Powered Risk Mitigation & Misinformation Detection System

This script helps you configure AIRMS+ for development or production deployment.
"""

import os
import sys
import json
import secrets
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

def print_banner():
    """Print AIRMS+ banner"""
    banner = """
    🛡️  AIRMS+ Setup Wizard
    ═══════════════════════════════════════════════════════════════
    AI-Powered Risk Mitigation & Misinformation Detection System
    
    Features:
    • 🔍 Multi-layered Risk Detection (Bias, PII, Hallucination, Adversarial)
    • 🚨 AI-Powered Misinformation Detection with Fact-Checking
    • 🔒 Secure PII Handling with SHA-256 Hashing
    • 🤖 Intelligent AI Routing (Groq + Gemini)
    • 📊 Real-time Analytics Dashboard
    • 🎓 Educational Content Generation
    ═══════════════════════════════════════════════════════════════
    """
    print(banner)

def get_user_input(prompt: str, default: str = "", required: bool = True) -> str:
    """Get user input with default value"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        value = input(full_prompt).strip()
        if not value and default:
            return default
        elif not value and required:
            print("❌ This field is required. Please enter a value.")
            continue
        else:
            return value

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input from user"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    return response in ['y', 'yes', '1', 'true']

def generate_secret_key() -> str:
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def setup_mongodb_config() -> Dict[str, Any]:
    """Configure MongoDB settings"""
    print("\n📊 MongoDB Configuration")
    print("=" * 50)
    
    print("\nChoose MongoDB deployment:")
    print("1. Local MongoDB (recommended for development)")
    print("2. MongoDB Atlas (recommended for production)")
    print("3. Custom MongoDB URL")
    
    choice = get_user_input("Select option (1-3)", "1")
    
    if choice == "1":
        # Local MongoDB
        mongodb_url = get_user_input("MongoDB URL", "mongodb://localhost:27017")
        database_name = get_user_input("Database name", "airms_plus")
        
        return {
            "MONGODB_URL": mongodb_url,
            "MONGODB_DATABASE": database_name,
            "MONGODB_MIN_POOL_SIZE": 10,
            "MONGODB_MAX_POOL_SIZE": 100,
            "deployment_type": "local"
        }
    
    elif choice == "2":
        # MongoDB Atlas
        print("\n🌐 MongoDB Atlas Setup:")
        print("1. Go to https://cloud.mongodb.com/")
        print("2. Create a new cluster or use existing one")
        print("3. Get your connection string")
        
        mongodb_url = get_user_input("MongoDB Atlas connection string")
        database_name = get_user_input("Database name", "airms_plus")
        
        return {
            "MONGODB_URL": mongodb_url,
            "MONGODB_DATABASE": database_name,
            "MONGODB_MIN_POOL_SIZE": 5,
            "MONGODB_MAX_POOL_SIZE": 50,
            "deployment_type": "atlas"
        }
    
    else:
        # Custom URL
        mongodb_url = get_user_input("Custom MongoDB URL")
        database_name = get_user_input("Database name", "airms_plus")
        
        return {
            "MONGODB_URL": mongodb_url,
            "MONGODB_DATABASE": database_name,
            "MONGODB_MIN_POOL_SIZE": 10,
            "MONGODB_MAX_POOL_SIZE": 100,
            "deployment_type": "custom"
        }

def setup_ai_apis() -> Dict[str, Any]:
    """Configure AI API settings"""
    print("\n🤖 AI API Configuration")
    print("=" * 50)
    
    config = {}
    
    # Gemini API
    print("\n🧠 Gemini API (Deep Reasoning):")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    
    use_gemini = get_yes_no("Configure Gemini API?", True)
    if use_gemini:
        config["GEMINI_API_KEY"] = get_user_input("Gemini API Key", required=False)
        config["GEMINI_MODEL"] = get_user_input("Gemini Model", "gemini-1.5-flash")
    else:
        config["GEMINI_API_KEY"] = ""
        config["GEMINI_MODEL"] = "gemini-1.5-flash"
    
    # Groq API
    print("\n⚡ Groq API (Fast Filtering):")
    print("Get your API key from: https://console.groq.com/keys")
    
    use_groq = get_yes_no("Configure Groq API?", True)
    if use_groq:
        config["GROQ_API_KEY"] = get_user_input("Groq API Key", required=False)
        config["GROQ_MODEL"] = get_user_input("Groq Model", "llama3-8b-8192")
    else:
        config["GROQ_API_KEY"] = ""
        config["GROQ_MODEL"] = "llama3-8b-8192"
    
    # AI Routing Strategy
    print("\n🔀 AI Routing Strategy:")
    print("1. cost_optimized - 80% Groq, 20% Gemini (recommended)")
    print("2. quality_first - 20% Groq, 80% Gemini")
    print("3. speed_first - 90% Groq, 10% Gemini")
    
    strategy_choice = get_user_input("Select routing strategy (1-3)", "1")
    strategy_map = {
        "1": "cost_optimized",
        "2": "quality_first", 
        "3": "speed_first"
    }
    config["AI_ROUTING_STRATEGY"] = strategy_map.get(strategy_choice, "cost_optimized")
    
    return config

def setup_external_apis() -> Dict[str, Any]:
    """Configure external API settings"""
    print("\n🌐 External API Configuration")
    print("=" * 50)
    
    config = {}
    
    # Google Fact Check API
    print("\n🔍 Google Fact Check API:")
    print("Get your API key from: https://console.cloud.google.com/")
    
    use_fact_check = get_yes_no("Configure Google Fact Check API?", False)
    if use_fact_check:
        config["GOOGLE_FACT_CHECK_API_KEY"] = get_user_input("Google Fact Check API Key", required=False)
        config["GOOGLE_FACT_CHECK_ENABLED"] = True
    else:
        config["GOOGLE_FACT_CHECK_API_KEY"] = ""
        config["GOOGLE_FACT_CHECK_ENABLED"] = False
    
    # NewsAPI
    print("\n📰 NewsAPI:")
    print("Get your API key from: https://newsapi.org/")
    
    use_newsapi = get_yes_no("Configure NewsAPI?", False)
    if use_newsapi:
        config["NEWSAPI_KEY"] = get_user_input("NewsAPI Key", required=False)
        config["NEWSAPI_ENABLED"] = True
    else:
        config["NEWSAPI_KEY"] = ""
        config["NEWSAPI_ENABLED"] = False
    
    # Wikipedia (always enabled, no API key needed)
    config["WIKIPEDIA_ENABLED"] = True
    config["WIKIPEDIA_LANGUAGE"] = get_user_input("Wikipedia language", "en")
    
    return config

def setup_security_settings() -> Dict[str, Any]:
    """Configure security settings"""
    print("\n🔒 Security Configuration")
    print("=" * 50)
    
    config = {}
    
    # JWT Settings
    config["JWT_SECRET_KEY"] = generate_secret_key()
    config["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = int(get_user_input("JWT token expiration (minutes)", "480"))
    
    # PII Security
    config["PII_HASH_ALGORITHM"] = "sha256"
    config["PII_SALT_LENGTH"] = 32
    config["PII_ENABLE_REVERSE_LOOKUP"] = get_yes_no("Enable PII reverse lookup?", True)
    
    # Risk Thresholds
    config["LOW_RISK_THRESHOLD"] = float(get_user_input("Low risk threshold", "30.0"))
    config["MEDIUM_RISK_THRESHOLD"] = float(get_user_input("Medium risk threshold", "60.0"))
    config["HIGH_RISK_THRESHOLD"] = float(get_user_input("High risk threshold", "80.0"))
    
    return config

def setup_application_settings() -> Dict[str, Any]:
    """Configure application settings"""
    print("\n⚙️ Application Configuration")
    print("=" * 50)
    
    config = {}
    
    # Basic settings
    config["APP_NAME"] = "AIRMS+ AI Risk Mitigation System"
    config["APP_VERSION"] = "2.0.0"
    config["ENVIRONMENT"] = get_user_input("Environment", "development")
    config["DEBUG"] = get_yes_no("Enable debug mode?", config["ENVIRONMENT"] == "development")
    
    # Server settings
    config["HOST"] = get_user_input("Server host", "0.0.0.0")
    config["PORT"] = int(get_user_input("Server port", "8000"))
    config["RELOAD"] = get_yes_no("Enable auto-reload?", config["DEBUG"])
    
    # CORS settings
    config["CORS_ORIGINS"] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        
    ]
    
    # Feature toggles
    config["ENABLE_BIAS_DETECTION"] = get_yes_no("Enable bias detection?", True)
    config["ENABLE_PII_DETECTION"] = get_yes_no("Enable PII detection?", True)
    config["ENABLE_HALLUCINATION_DETECTION"] = get_yes_no("Enable hallucination detection?", True)
    config["ENABLE_ADVERSARIAL_DETECTION"] = get_yes_no("Enable adversarial detection?", True)
    config["ENABLE_MISINFORMATION_DETECTION"] = get_yes_no("Enable misinformation detection?", True)
    
    # Analytics
    config["ENABLE_ANALYTICS"] = get_yes_no("Enable analytics?", True)
    config["ENABLE_REAL_TIME_STATS"] = get_yes_no("Enable real-time stats?", True)
    config["ANALYTICS_RETENTION_DAYS"] = int(get_user_input("Analytics retention (days)", "90"))
    
    return config

def create_env_file(config: Dict[str, Any]) -> None:
    """Create .env file with configuration"""
    env_content = f"""# 🛡️ AIRMS+ Configuration
# AI-Powered Risk Mitigation & Misinformation Detection System
# Generated by setup script on {os.popen('date').read().strip()}

# === APPLICATION SETTINGS ===
APP_NAME="{config['APP_NAME']}"
APP_VERSION={config['APP_VERSION']}
ENVIRONMENT={config['ENVIRONMENT']}
DEBUG={str(config['DEBUG']).lower()}

# === SERVER SETTINGS ===
HOST={config['HOST']}
PORT={config['PORT']}
RELOAD={str(config['RELOAD']).lower()}

# === MONGODB SETTINGS ===
MONGODB_URL={config['MONGODB_URL']}
MONGODB_DATABASE={config['MONGODB_DATABASE']}
MONGODB_MIN_POOL_SIZE={config['MONGODB_MIN_POOL_SIZE']}
MONGODB_MAX_POOL_SIZE={config['MONGODB_MAX_POOL_SIZE']}

# === AI API SETTINGS ===
GEMINI_API_KEY={config['GEMINI_API_KEY']}
GEMINI_MODEL={config['GEMINI_MODEL']}
GROQ_API_KEY={config['GROQ_API_KEY']}
GROQ_MODEL={config['GROQ_MODEL']}
AI_ROUTING_STRATEGY={config['AI_ROUTING_STRATEGY']}

# === EXTERNAL API SETTINGS ===
GOOGLE_FACT_CHECK_API_KEY={config['GOOGLE_FACT_CHECK_API_KEY']}
GOOGLE_FACT_CHECK_ENABLED={str(config['GOOGLE_FACT_CHECK_ENABLED']).lower()}
NEWSAPI_KEY={config['NEWSAPI_KEY']}
NEWSAPI_ENABLED={str(config['NEWSAPI_ENABLED']).lower()}
WIKIPEDIA_ENABLED={str(config['WIKIPEDIA_ENABLED']).lower()}
WIKIPEDIA_LANGUAGE={config['WIKIPEDIA_LANGUAGE']}

# === SECURITY SETTINGS ===
JWT_SECRET_KEY={config['JWT_SECRET_KEY']}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES={config['JWT_ACCESS_TOKEN_EXPIRE_MINUTES']}
PII_HASH_ALGORITHM={config['PII_HASH_ALGORITHM']}
PII_SALT_LENGTH={config['PII_SALT_LENGTH']}
PII_ENABLE_REVERSE_LOOKUP={str(config['PII_ENABLE_REVERSE_LOOKUP']).lower()}

# === RISK DETECTION SETTINGS ===
LOW_RISK_THRESHOLD={config['LOW_RISK_THRESHOLD']}
MEDIUM_RISK_THRESHOLD={config['MEDIUM_RISK_THRESHOLD']}
HIGH_RISK_THRESHOLD={config['HIGH_RISK_THRESHOLD']}

# === FEATURE TOGGLES ===
ENABLE_BIAS_DETECTION={str(config['ENABLE_BIAS_DETECTION']).lower()}
ENABLE_PII_DETECTION={str(config['ENABLE_PII_DETECTION']).lower()}
ENABLE_HALLUCINATION_DETECTION={str(config['ENABLE_HALLUCINATION_DETECTION']).lower()}
ENABLE_ADVERSARIAL_DETECTION={str(config['ENABLE_ADVERSARIAL_DETECTION']).lower()}
ENABLE_MISINFORMATION_DETECTION={str(config['ENABLE_MISINFORMATION_DETECTION']).lower()}

# === ANALYTICS SETTINGS ===
ENABLE_ANALYTICS={str(config['ENABLE_ANALYTICS']).lower()}
ENABLE_REAL_TIME_STATS={str(config['ENABLE_REAL_TIME_STATS']).lower()}
ANALYTICS_RETENTION_DAYS={config['ANALYTICS_RETENTION_DAYS']}

# === CORS SETTINGS ===
CORS_ORIGINS={json.dumps(config['CORS_ORIGINS'])}
CORS_CREDENTIALS=true
CORS_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS=["*"]

# === LOGGING SETTINGS ===
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Environment file created: {os.path.abspath('.env')}")

def verify_setup() -> bool:
    """Verify the setup configuration"""
    print("\n🔍 Verifying Setup...")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Try to import and validate configuration
    try:
        sys.path.insert(0, os.getcwd())
        from app.core.config import settings, validate_ai_apis
        
        print(f"✅ Configuration loaded successfully")
        print(f"   App Name: {settings.APP_NAME}")
        print(f"   Version: {settings.APP_VERSION}")
        print(f"   Environment: {settings.ENVIRONMENT}")
        print(f"   Database: {settings.MONGODB_DATABASE}")
        
        # Validate AI APIs
        api_status = validate_ai_apis()
        print(f"   AI APIs: Gemini={api_status['gemini_configured']}, Groq={api_status['groq_configured']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 AIRMS+ Setup Complete!")
    print("=" * 50)
    print("\n📋 Next Steps:")
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. Start the development server:")
    print("   python -m uvicorn app.main:app --reload")
    print("\n3. Access the API documentation:")
    print("   http://localhost:8000/docs")
    print("\n4. Test the system:")
    print("   http://localhost:8000/health")
    print("\n5. Default admin credentials:")
    print("   Email: admin@airms.com")
    print("   Password: admin123")
    print("\n🔗 Useful URLs:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("   • System Info: http://localhost:8000/")
    print("\n📚 Documentation:")
    print("   • MongoDB Setup: SUPABASE_ONLY_SETUP.md")
    print("   • API Reference: /docs endpoint")
    print("   • Configuration: app/core/config.py")

def main():
    """Main setup function"""
    print_banner()
    
    # Check if running in correct directory
    if not os.path.exists('app') or not os.path.exists('requirements.txt'):
        print("❌ Please run this script from the backend_mongo directory")
        sys.exit(1)
    
    # Collect configuration
    config = {}
    
    try:
        # Setup each component
        config.update(setup_application_settings())
        config.update(setup_mongodb_config())
        config.update(setup_ai_apis())
        config.update(setup_external_apis())
        config.update(setup_security_settings())
        
        # Create .env file
        create_env_file(config)
        
        # Verify setup
        if verify_setup():
            print_next_steps()
        else:
            print("\n⚠️ Setup verification failed. Please check your configuration.")
            
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
