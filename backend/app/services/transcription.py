"""
Whisper Speech-to-Text Service.
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

import whisper

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result of transcription."""
    text: str
    language: str
    language_probability: float
    segments: List[Dict[str, Any]]
    word_timestamps: Optional[List[Dict[str, Any]]] = None
    processing_time_seconds: float = 0.0
    word_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "language": self.language,
            "language_probability": self.language_probability,
            "segments": self.segments,
            "word_timestamps": self.word_timestamps,
            "processing_time_seconds": self.processing_time_seconds,
            "word_count": self.word_count
        }


class WhisperTranscriptionService:
    """Whisper-based transcription service."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.device = settings.WHISPER_DEVICE
        
    def _load_model(self):
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            start_time = time.time()
            self._model = whisper.load_model(self.model_size, device=self.device)
            load_time = time.time() - start_time
            logger.info(f"Whisper model loaded in {load_time:.2f}s")
        return self._model
    
    @property
    def model(self):
        return self._load_model()
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        word_timestamps: bool = True
    ) -> TranscriptionResult:
        """Transcribe an audio file."""
        start_time = time.time()
        logger.info(f"Transcribing: {audio_path}")
        
        options = {
            "word_timestamps": word_timestamps,
            "verbose": False
        }
        
        if language:
            options["language"] = language
        
        result = self.model.transcribe(str(audio_path), **options)
        processing_time = time.time() - start_time
        
        # Extract segments
        segments = []
        for i, seg in enumerate(result.get("segments", [])):
            segment_data = {
                "id": i,
                "text": seg["text"].strip(),
                "start": round(seg["start"], 3),
                "end": round(seg["end"], 3),
            }
            
            if word_timestamps and "words" in seg:
                segment_data["words"] = [
                    {
                        "word": w["word"].strip(),
                        "start": round(w["start"], 3),
                        "end": round(w["end"], 3),
                        "confidence": round(w.get("probability", 1.0), 3)
                    }
                    for w in seg["words"]
                ]
            segments.append(segment_data)
        
        # Extract all word timestamps
        all_words = []
        if word_timestamps:
            for seg in segments:
                if "words" in seg:
                    all_words.extend(seg["words"])
        
        word_count = len(result["text"].split())
        detected_language = result.get("language", "en")
        
        logger.info(f"Transcription complete: {word_count} words, language={detected_language}")
        
        return TranscriptionResult(
            text=result["text"].strip(),
            language=detected_language,
            language_probability=0.95,
            segments=segments,
            word_timestamps=all_words if all_words else None,
            processing_time_seconds=round(processing_time, 2),
            word_count=word_count
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_size": self.model_size,
            "device": self.device,
            "model_loaded": self._model is not None
        }


transcription_service = WhisperTranscriptionService()
