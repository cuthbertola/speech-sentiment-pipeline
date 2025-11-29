"""
Main FastAPI Application - Speech-to-Text + Sentiment Analysis Pipeline.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.database import create_tables
from app.api.routes import audio, analysis, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🎤 Whisper model: {settings.WHISPER_MODEL_SIZE}")
    logger.info(f"😊 Sentiment model: {settings.SENTIMENT_MODEL}")
    
    # Create database tables
    await create_tables()
    logger.info("📊 Database tables created")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 🎙️ Speech-to-Text + Sentiment Analysis Pipeline

This API provides:
- **Audio Upload**: Upload mp3, wav, m4a, flac, ogg files
- **Transcription**: Real-time speech-to-text using OpenAI Whisper
- **Sentiment Analysis**: Positive/negative/neutral classification using RoBERTa
- **Entity Extraction**: Named entity recognition (names, dates, organizations)
- **Summarization**: Automatic call summary with key phrases and action items
- **Search**: Full-text search across transcripts

### Target Metrics
- WER (Word Error Rate): <10%
- Sentiment Accuracy: 85%+
- Processing Time: <2x audio length
- Entity Extraction F1: 0.82+
    """,
    lifespan=lifespan
)

# Add CORS middleware - Allow all localhost origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002", "http://127.0.0.1:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }
