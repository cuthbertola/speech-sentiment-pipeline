"""
Audio Upload and Management API Routes.
"""

import os
import uuid
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import settings
from app.core.database import get_db
from app.models.database import AudioFile, ProcessingStatus
from app.models.schemas import AudioUploadResponse, AudioFileInfo, AudioFileList
from app.services.pipeline import pipeline_service

router = APIRouter()


def get_audio_duration(file_path: str) -> float:
    """Get audio duration using pydub."""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0
    except Exception:
        return 0.0


@router.post("/upload", response_model=AudioUploadResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an audio file for processing.
    
    Supported formats: mp3, wav, m4a, flac, ogg
    """
    # Validate file extension
    file_ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Create upload directory if not exists
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get file info
    file_size = os.path.getsize(file_path)
    duration = get_audio_duration(str(file_path))
    
    # Create database record
    audio_file = AudioFile(
        filename=unique_filename,
        original_filename=file.filename or "unknown",
        file_path=str(file_path),
        file_size_bytes=file_size,
        duration_seconds=duration,
        format=file_ext,
        status=ProcessingStatus.PENDING
    )
    
    db.add(audio_file)
    await db.commit()
    await db.refresh(audio_file)
    
    return AudioUploadResponse(
        id=audio_file.id,
        filename=audio_file.filename,
        status=audio_file.status,
        message="File uploaded successfully. Processing will begin shortly."
    )


@router.post("/{audio_id}/process")
async def process_audio(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Start processing an uploaded audio file."""
    result = await db.execute(select(AudioFile).where(AudioFile.id == audio_id))
    audio_file = result.scalar_one_or_none()
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    if audio_file.status == ProcessingStatus.PROCESSING:
        raise HTTPException(status_code=400, detail="File is already being processed")
    
    if audio_file.status == ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="File has already been processed")
    
    # Process through pipeline
    pipeline_result = await pipeline_service.process_audio(db, audio_id)
    
    if not pipeline_result.success:
        raise HTTPException(status_code=500, detail=pipeline_result.error)
    
    return {
        "message": "Processing complete",
        "audio_id": audio_id,
        "transcript_preview": pipeline_result.transcript_text[:200] + "..." if len(pipeline_result.transcript_text) > 200 else pipeline_result.transcript_text,
        "language": pipeline_result.language,
        "sentiment": pipeline_result.sentiment,
        "entities_found": pipeline_result.entities_count,
        "processing_time_seconds": pipeline_result.total_processing_time
    }


@router.get("/", response_model=AudioFileList)
async def list_audio_files(
    skip: int = 0,
    limit: int = 20,
    status: ProcessingStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """List all uploaded audio files."""
    query = select(AudioFile)
    
    if status:
        query = query.where(AudioFile.status == status)
    
    query = query.order_by(AudioFile.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(AudioFile.id))
    if status:
        count_query = count_query.where(AudioFile.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return AudioFileList(
        files=[AudioFileInfo.model_validate(f) for f in files],
        total=total
    )


@router.get("/{audio_id}", response_model=AudioFileInfo)
async def get_audio_file(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific audio file."""
    result = await db.execute(select(AudioFile).where(AudioFile.id == audio_id))
    audio_file = result.scalar_one_or_none()
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return AudioFileInfo.model_validate(audio_file)


@router.delete("/{audio_id}")
async def delete_audio_file(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an audio file and all associated data."""
    result = await db.execute(select(AudioFile).where(AudioFile.id == audio_id))
    audio_file = result.scalar_one_or_none()
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Delete physical file
    if os.path.exists(audio_file.file_path):
        os.remove(audio_file.file_path)
    
    # Delete database record (cascade will delete related records)
    await db.delete(audio_file)
    await db.commit()
    
    return {"message": "Audio file deleted successfully"}
