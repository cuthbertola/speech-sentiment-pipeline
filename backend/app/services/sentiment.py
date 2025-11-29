"""
Sentiment Analysis Service using RoBERTa.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np

from app.config import settings
from app.models.schemas import SentimentLabel

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    label: SentimentLabel
    confidence: float
    scores: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label.value,
            "confidence": self.confidence,
            "scores": self.scores
        }


@dataclass
class FullSentimentAnalysis:
    """Full sentiment analysis with segments."""
    overall: SentimentResult
    segments: List[Dict[str, Any]]
    processing_time_seconds: float


class SentimentAnalysisService:
    """Transformer-based sentiment analysis service."""
    
    _instance = None
    _model = None
    _tokenizer = None
    
    LABEL_MAPPING = {
        "positive": SentimentLabel.POSITIVE,
        "negative": SentimentLabel.NEGATIVE,
        "neutral": SentimentLabel.NEUTRAL,
        "POSITIVE": SentimentLabel.POSITIVE,
        "NEGATIVE": SentimentLabel.NEGATIVE,
        "NEUTRAL": SentimentLabel.NEUTRAL,
        "LABEL_0": SentimentLabel.NEGATIVE,
        "LABEL_1": SentimentLabel.NEUTRAL,
        "LABEL_2": SentimentLabel.POSITIVE,
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.model_name = settings.SENTIMENT_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_length = 512
        
    def _load_model(self):
        if self._model is None:
            logger.info(f"Loading sentiment model: {self.model_name}")
            start_time = time.time()
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()
            load_time = time.time() - start_time
            logger.info(f"Sentiment model loaded in {load_time:.2f}s on {self.device}")
        return self._model, self._tokenizer
    
    @property
    def model(self):
        return self._load_model()[0]
    
    @property
    def tokenizer(self):
        return self._load_model()[1]
    
    def _get_label_names(self) -> List[str]:
        if hasattr(self.model.config, 'id2label'):
            return [self.model.config.id2label[i] for i in range(len(self.model.config.id2label))]
        return ["negative", "neutral", "positive"]
    
    def analyze_text(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text."""
        if not text or not text.strip():
            return SentimentResult(
                label=SentimentLabel.NEUTRAL,
                confidence=1.0,
                scores={"positive": 0.0, "negative": 0.0, "neutral": 1.0}
            )
        
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()
        
        label_names = self._get_label_names()
        
        scores = {}
        for i, name in enumerate(label_names):
            mapped_label = self.LABEL_MAPPING.get(name, SentimentLabel.NEUTRAL)
            scores[mapped_label.value] = float(probs[i])
        
        for sentiment in SentimentLabel:
            if sentiment.value not in scores:
                scores[sentiment.value] = 0.0
        
        predicted_idx = int(np.argmax(probs))
        predicted_name = label_names[predicted_idx]
        predicted_label = self.LABEL_MAPPING.get(predicted_name, SentimentLabel.NEUTRAL)
        confidence = float(probs[predicted_idx])
        
        return SentimentResult(
            label=predicted_label,
            confidence=round(confidence, 4),
            scores={k: round(v, 4) for k, v in scores.items()}
        )
    
    def analyze_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment for each segment."""
        analyzed = []
        for seg in segments:
            text = seg.get("text", "")
            result = self.analyze_text(text)
            analyzed.append({
                "text": text,
                "start": seg.get("start"),
                "end": seg.get("end"),
                "sentiment": result.label.value,
                "confidence": result.confidence,
                "scores": result.scores
            })
        return analyzed
    
    def analyze_full(self, text: str, segments: Optional[List[Dict[str, Any]]] = None) -> FullSentimentAnalysis:
        """Perform full sentiment analysis."""
        start_time = time.time()
        overall = self.analyze_text(text)
        segment_results = self.analyze_segments(segments) if segments else []
        processing_time = time.time() - start_time
        
        logger.info(f"Sentiment analysis complete: {overall.label.value} ({overall.confidence:.2f})")
        
        return FullSentimentAnalysis(
            overall=overall,
            segments=segment_results,
            processing_time_seconds=round(processing_time, 2)
        )


sentiment_service = SentimentAnalysisService()
