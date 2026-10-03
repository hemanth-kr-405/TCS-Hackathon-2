import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "TCS Retail Customer Sentiment Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database — SQLite default, swap DATABASE_URL env var for PostgreSQL
    DATABASE_URL: str = "sqlite:///./retail_sentiment.db"

    # ML
    MODEL_SEED: int = 42
    MIN_TRAINING_SAMPLES: int = 100
    MODELS_DIR: str = "models"

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # LLM API Keys & Provider Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    XAI_API_KEY: str = ""
    XAI_MODEL: str = "grok-2-latest"
    XAI_BASE_URL: str = "https://api.x.ai"

    GROK_API_KEY: str = ""
    GROK_MODEL: str = "grok-2-latest"
    DEFAULT_LLM_PROVIDER: str = "auto"


    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
