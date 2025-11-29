"""
Health Check API Route.
"""

from fastapi import APIRouter

from app.config import settings
from app.models.schemas import HealthCheck

router = APIRouter()


@router.get("/", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Used by:
    - Docker health checks
    - Kubernetes probes
    - Load balancers
    """
    return HealthCheck(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        whisper_model=settings.WHISPER_MODEL_SIZE,
        sentiment_model=settings.SENTIMENT_MODEL,
        database="connected"
    )
