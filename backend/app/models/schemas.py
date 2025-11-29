"""
Pydantic Schemas for API validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# ===== Audio Schemas =====

class AudioUploadResponse(BaseModel):
    id: int
    filename: str
    status: ProcessingStatus
    message: str
    model_config = ConfigDict(from_attributes=True)


class AudioFileInfo(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    status: ProcessingStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class AudioFileList(BaseModel):
    files: List[AudioFileInfo]
    total: int


# ===== Transcript Schemas =====

class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float
    confidence: Optional[float] = None


class TranscriptSegment(BaseModel):
    id: int
    text: str
    start: float
    end: float
    words: Optional[List[WordTimestamp]] = None


class TranscriptResponse(BaseModel):
    id: int
    audio_file_id: int
    full_text: str
    language: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = None
    word_count: Optional[int] = None
    processing_time_seconds: Optional[float] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ===== Sentiment Schemas =====

class SentimentScores(BaseModel):
    positive: float = Field(..., ge=0, le=1)
    negative: float = Field(..., ge=0, le=1)
    neutral: float = Field(..., ge=0, le=1)


class SegmentSentiment(BaseModel):
    text: str
    sentiment: SentimentLabel
    confidence: float
    start: Optional[float] = None
    end: Optional[float] = None


class SentimentResponse(BaseModel):
    overall_sentiment: SentimentLabel
    confidence: float
    scores: SentimentScores
    segment_sentiments: Optional[List[SegmentSentiment]] = None


# ===== Entity Schemas =====

class EntityResponse(BaseModel):
    text: str
    label: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    confidence: Optional[float] = None


class EntitiesResponse(BaseModel):
    entities: List[EntityResponse]
    entity_counts: Dict[str, int]


# ===== Summary Schemas =====

class SummaryResponse(BaseModel):
    summary: str
    key_phrases: List[str]
    action_items: Optional[List[str]] = None
    topics: Optional[List[str]] = None


# ===== Full Analysis Schema =====

class FullAnalysisResponse(BaseModel):
    audio: AudioFileInfo
    transcript: Optional[TranscriptResponse] = None
    sentiment: Optional[SentimentResponse] = None
    entities: Optional[EntitiesResponse] = None
    summary: Optional[SummaryResponse] = None
    processing_complete: bool


# ===== Health Check =====

class HealthCheck(BaseModel):
    status: str
    app_name: str
    version: str
    whisper_model: str
    sentiment_model: str
    database: str
