"""
Analysis API Routes - Transcripts, Sentiment, Entities, Summaries.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.database import AudioFile, Transcript, Analysis, Entity
from app.models.schemas import (
    TranscriptResponse, SentimentResponse, SentimentScores,
    EntitiesResponse, EntityResponse, SummaryResponse,
    FullAnalysisResponse, AudioFileInfo, SegmentSentiment, SentimentLabel
)

router = APIRouter()


@router.get("/{audio_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get transcript for an audio file."""
    result = await db.execute(
        select(Transcript).where(Transcript.audio_file_id == audio_id)
    )
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return TranscriptResponse.model_validate(transcript)


@router.get("/{audio_id}/sentiment", response_model=SentimentResponse)
async def get_sentiment(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get sentiment analysis for an audio file."""
    result = await db.execute(
        select(Analysis)
        .join(Transcript)
        .where(Transcript.audio_file_id == audio_id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Build segment sentiments
    segment_sentiments = None
    if analysis.segment_sentiments:
        segment_sentiments = [
            SegmentSentiment(
                text=seg.get("text", ""),
                sentiment=SentimentLabel(seg.get("sentiment", "neutral")),
                confidence=seg.get("confidence", 0.0),
                start=seg.get("start"),
                end=seg.get("end")
            )
            for seg in analysis.segment_sentiments
        ]
    
    return SentimentResponse(
        overall_sentiment=analysis.overall_sentiment,
        confidence=analysis.sentiment_confidence,
        scores=SentimentScores(
            positive=analysis.positive_score,
            negative=analysis.negative_score,
            neutral=analysis.neutral_score
        ),
        segment_sentiments=segment_sentiments
    )


@router.get("/{audio_id}/entities", response_model=EntitiesResponse)
async def get_entities(
    audio_id: int,
    label: Optional[str] = Query(None, description="Filter by entity label"),
    db: AsyncSession = Depends(get_db)
):
    """Get extracted entities for an audio file."""
    # Get transcript ID
    result = await db.execute(
        select(Transcript).where(Transcript.audio_file_id == audio_id)
    )
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    # Get entities
    query = select(Entity).where(Entity.transcript_id == transcript.id)
    if label:
        query = query.where(Entity.label == label.upper())
    
    result = await db.execute(query)
    entities = result.scalars().all()
    
    # Count by label
    entity_counts = {}
    for ent in entities:
        entity_counts[ent.label] = entity_counts.get(ent.label, 0) + 1
    
    return EntitiesResponse(
        entities=[
            EntityResponse(
                text=ent.text,
                label=ent.label,
                start_char=ent.start_char,
                end_char=ent.end_char,
                confidence=ent.confidence
            )
            for ent in entities
        ],
        entity_counts=entity_counts
    )


@router.get("/{audio_id}/summary", response_model=SummaryResponse)
async def get_summary(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get summary and key phrases for an audio file."""
    result = await db.execute(
        select(Analysis)
        .join(Transcript)
        .where(Transcript.audio_file_id == audio_id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return SummaryResponse(
        summary=analysis.summary or "",
        key_phrases=analysis.key_phrases or [],
        action_items=analysis.action_items or [],
        topics=analysis.topics or []
    )


@router.get("/{audio_id}/full", response_model=FullAnalysisResponse)
async def get_full_analysis(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get complete analysis for an audio file."""
    # Get audio file with relationships
    result = await db.execute(
        select(AudioFile)
        .options(selectinload(AudioFile.transcript).selectinload(Transcript.analysis))
        .options(selectinload(AudioFile.transcript).selectinload(Transcript.entities))
        .where(AudioFile.id == audio_id)
    )
    audio_file = result.scalar_one_or_none()
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Build response
    transcript_response = None
    sentiment_response = None
    entities_response = None
    summary_response = None
    
    if audio_file.transcript:
        transcript = audio_file.transcript
        transcript_response = TranscriptResponse.model_validate(transcript)
        
        if transcript.analysis:
            analysis = transcript.analysis
            
            segment_sentiments = None
            if analysis.segment_sentiments:
                segment_sentiments = [
                    SegmentSentiment(
                        text=seg.get("text", ""),
                        sentiment=SentimentLabel(seg.get("sentiment", "neutral")),
                        confidence=seg.get("confidence", 0.0),
                        start=seg.get("start"),
                        end=seg.get("end")
                    )
                    for seg in analysis.segment_sentiments
                ]
            
            sentiment_response = SentimentResponse(
                overall_sentiment=analysis.overall_sentiment,
                confidence=analysis.sentiment_confidence,
                scores=SentimentScores(
                    positive=analysis.positive_score,
                    negative=analysis.negative_score,
                    neutral=analysis.neutral_score
                ),
                segment_sentiments=segment_sentiments
            )
            
            summary_response = SummaryResponse(
                summary=analysis.summary or "",
                key_phrases=analysis.key_phrases or [],
                action_items=analysis.action_items or [],
                topics=analysis.topics or []
            )
        
        if transcript.entities:
            entity_counts = {}
            for ent in transcript.entities:
                entity_counts[ent.label] = entity_counts.get(ent.label, 0) + 1
            
            entities_response = EntitiesResponse(
                entities=[
                    EntityResponse(
                        text=ent.text,
                        label=ent.label,
                        start_char=ent.start_char,
                        end_char=ent.end_char,
                        confidence=ent.confidence
                    )
                    for ent in transcript.entities
                ],
                entity_counts=entity_counts
            )
    
    return FullAnalysisResponse(
        audio=AudioFileInfo.model_validate(audio_file),
        transcript=transcript_response,
        sentiment=sentiment_response,
        entities=entities_response,
        summary=summary_response,
        processing_complete=audio_file.status.value == "completed"
    )
