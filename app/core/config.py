from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    APP_NAME: str = "NEXUS REST API"
    API_V1_STR: str = "/api/v1"
    PROJECT_VERSION: str = "0.1.0"

    # Database placeholder (example, replace with your actual connection string via .env)
    DATABASE_URL: str = "postgresql://nexus_user:nexus_password@localhost:5432/nexus_db" # Default to a local SQLite for simplicity

    # LLM Service Placeholders (load from environment variables)
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    GEMINI_API_KEY: str = "your_gemini_api_key_here"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

settings = Settings()