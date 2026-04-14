"""
Ask ZodiaQ configuration.
Reads settings from .env file at the project root.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Load .env from the project root (parent of app/)
ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # Path to the AI-predigest project that contains the evaluators & API clients
    ai_predigest_path: str = "/Users/sankit/Downloads/AI-predigest"

    host: str = "0.0.0.0"
    port: int = 8001

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
