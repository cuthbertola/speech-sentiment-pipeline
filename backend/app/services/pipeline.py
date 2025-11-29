"""
Main Pipeline Service - Orchestrates all ML services.
"""

import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.database import AudioFile, Transcript, Analysis, Entity, ProcessingStatus, SentimentLabel
from app.services.transcription import transcription_service
from app.services.sentiment import sentiment_service
from app.services.entity import entity_service
from app.services.summarization import summarization_service

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Complete pipeline processing result."""
    audio_id: int
    transcript_text: str
    language: str
    sentiment: str
    sentiment_confidence: float
    entities_count: int
    summary: str
    total_processing_time: float
    success: bool
    error: Optional[str] = None


class PipelineService:
    """Orchestrates the full audio processing pipeline."""
    
    async def process_audio(
        self,
        db: AsyncSession,
        audio_id: int
    ) -> PipelineResult:
        """
        Process an audio file through the complete pipeline.
        
        Steps:
        1. Transcribe audio with Whisper
        2. Analyze sentiment with RoBERTa
        3. Extract entities with spaCy
        4. Generate summary
        5. Save all results to database
        """
        start_time = time.time()
        
        # Get audio file record
        result = await db.execute(select(AudioFile).where(AudioFile.id == audio_id))
        audio_file = result.scalar_one_or_none()
        
        if not audio_file:
            return PipelineResult(
                audio_id=audio_id,
                transcript_text="",
                language="",
                sentiment="",
                sentiment_confidence=0.0,
                entities_count=0,
                summary="",
                total_processing_time=0.0,
                success=False,
                error="Audio file not found"
            )
        
        try:
            # Update status to processing
            audio_file.status = ProcessingStatus.PROCESSING
            await db.commit()
            
            # Step 1: Transcribe
            logger.info(f"Step 1: Transcribing audio {audio_id}")
            transcription_result = transcription_service.transcribe(audio_file.file_path)
            
            # Save transcript
            transcript = Transcript(
                audio_file_id=audio_id,
                full_text=transcription_result.text,
                language=transcription_result.language,
                language_probability=transcription_result.language_probability,
                word_timestamps=transcription_result.word_timestamps,
                segments=transcription_result.segments,
                processing_time_seconds=transcription_result.processing_time_seconds,
                word_count=transcription_result.word_count
            )
            db.add(transcript)
            await db.flush()
            
            # Step 2: Sentiment Analysis
            logger.info(f"Step 2: Analyzing sentiment for audio {audio_id}")
            sentiment_result = sentiment_service.analyze_full(
                transcription_result.text,
                transcription_result.segments
            )
            
            # Step 3: Entity Extraction
            logger.info(f"Step 3: Extracting entities for audio {audio_id}")
            entity_result = entity_service.extract_entities(transcription_result.text)
            
            # Step 4: Summarization
            logger.info(f"Step 4: Generating summary for audio {audio_id}")
            summary_result = summarization_service.summarize_full(transcription_result.text)
            
            # Save analysis
            analysis = Analysis(
                transcript_id=transcript.id,
                overall_sentiment=SentimentLabel(sentiment_result.overall.label.value),
                sentiment_confidence=sentiment_result.overall.confidence,
                positive_score=sentiment_result.overall.scores.get("positive", 0.0),
                negative_score=sentiment_result.overall.scores.get("negative", 0.0),
                neutral_score=sentiment_result.overall.scores.get("neutral", 0.0),
                segment_sentiments=sentiment_result.segments,
                summary=summary_result.summary,
                key_phrases=summary_result.key_phrases,
                action_items=summary_result.action_items,
                topics=summary_result.topics,
                processing_time_seconds=sentiment_result.processing_time_seconds
            )
            db.add(analysis)
            
            # Save entities
            for ent in entity_result.entities:
                entity = Entity(
                    transcript_id=transcript.id,
                    text=ent.text,
                    label=ent.label,
                    start_char=ent.start_char,
                    end_char=ent.end_char,
                    confidence=ent.confidence
                )
                db.add(entity)
            
            # Update audio file status
            audio_file.status = ProcessingStatus.COMPLETED
            audio_file.processed_at = datetime.utcnow()
            
            await db.commit()
            
            total_time = time.time() - start_time
            logger.info(f"Pipeline complete for audio {audio_id} in {total_time:.2f}s")
            
            return PipelineResult(
                audio_id=audio_id,
                transcript_text=transcription_result.text,
                language=transcription_result.language,
                sentiment=sentiment_result.overall.label.value,
                sentiment_confidence=sentiment_result.overall.confidence,
                entities_count=len(entity_result.entities),
                summary=summary_result.summary,
                total_processing_time=round(total_time, 2),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed for audio {audio_id}: {str(e)}")
            audio_file.status = ProcessingStatus.FAILED
            audio_file.error_message = str(e)
            await db.commit()
            
            return PipelineResult(
                audio_id=audio_id,
                transcript_text="",
                language="",
                sentiment="",
                sentiment_confidence=0.0,
                entities_count=0,
                summary="",
                total_processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )


pipeline_service = PipelineService()
