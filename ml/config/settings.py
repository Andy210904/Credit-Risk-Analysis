import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
    
    # Model Settings
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Service Settings
    ML_SERVICE_PORT = int(os.getenv("ML_SERVICE_PORT", "8001"))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Model Storage
    MODEL_PATH = os.getenv("MODEL_PATH", "./models/")
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"

config = Config()