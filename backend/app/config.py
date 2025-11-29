"""
Configuration Settings for Speech-Sentiment Pipeline.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Speech-Sentiment Pipeline"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./speech_sentiment.db"
    
    # Whisper
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cpu"
    
    # Sentiment Model
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    # File Storage
    UPLOAD_DIR: str = "data/audio_samples"
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: List[str] = ["mp3", "wav", "m4a", "flac", "ogg"]
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "sqlite:///mlflow/mlflow.db"
    MLFLOW_EXPERIMENT_NAME: str = "speech-sentiment-pipeline"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
