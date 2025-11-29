"""
SQLAlchemy Database Models.
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    ForeignKey, JSON, Enum
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ProcessingStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SentimentLabel(str, PyEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class AudioFile(Base):
    """Uploaded audio file metadata."""
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    format = Column(String(50), nullable=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    transcript = relationship("Transcript", back_populates="audio_file", uselist=False, cascade="all, delete-orphan")


class Transcript(Base):
    """Transcription results."""
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    audio_file_id = Column(Integer, ForeignKey("audio_files.id", ondelete="CASCADE"), unique=True)
    full_text = Column(Text, nullable=False)
    language = Column(String(10), nullable=True)
    language_probability = Column(Float, nullable=True)
    word_timestamps = Column(JSON, nullable=True)
    segments = Column(JSON, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    word_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    audio_file = relationship("AudioFile", back_populates="transcript")
    analysis = relationship("Analysis", back_populates="transcript", uselist=False, cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="transcript", cascade="all, delete-orphan")


class Analysis(Base):
    """Sentiment analysis results."""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id", ondelete="CASCADE"), unique=True)
    overall_sentiment = Column(Enum(SentimentLabel), nullable=False)
    sentiment_confidence = Column(Float, nullable=False)
    positive_score = Column(Float, nullable=False)
    negative_score = Column(Float, nullable=False)
    neutral_score = Column(Float, nullable=False)
    segment_sentiments = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    key_phrases = Column(JSON, nullable=True)
    action_items = Column(JSON, nullable=True)
    topics = Column(JSON, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transcript = relationship("Transcript", back_populates="analysis")


class Entity(Base):
    """Extracted named entities."""
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id", ondelete="CASCADE"))
    text = Column(String(500), nullable=False)
    label = Column(String(50), nullable=False)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transcript = relationship("Transcript", back_populates="entities")
