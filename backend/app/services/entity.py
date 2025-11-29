"""
Entity Extraction Service using spaCy.
"""

import time
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import Counter
import logging

import spacy

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Single extracted entity."""
    text: str
    label: str
    start_char: int
    end_char: int
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "label": self.label,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "confidence": self.confidence
        }


@dataclass
class EntityExtractionResult:
    """Result of entity extraction."""
    entities: List[ExtractedEntity]
    entity_counts: Dict[str, int]
    processing_time_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.entities],
            "entity_counts": self.entity_counts,
            "processing_time_seconds": self.processing_time_seconds
        }


class EntityExtractionService:
    """spaCy-based named entity extraction service."""
    
    _instance = None
    _nlp = None
    
    PRIORITY_LABELS = ["PERSON", "ORG", "DATE", "MONEY", "PRODUCT", "GPE", "TIME"]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.model_name = "en_core_web_sm"
        
    def _load_model(self):
        if self._nlp is None:
            logger.info(f"Loading spaCy model: {self.model_name}")
            start_time = time.time()
            try:
                self._nlp = spacy.load(self.model_name)
            except OSError:
                logger.warning(f"Model {self.model_name} not found, downloading...")
                spacy.cli.download(self.model_name)
                self._nlp = spacy.load(self.model_name)
            load_time = time.time() - start_time
            logger.info(f"spaCy model loaded in {load_time:.2f}s")
        return self._nlp
    
    @property
    def nlp(self):
        return self._load_model()
    
    def extract_entities(self, text: str, include_all: bool = False) -> EntityExtractionResult:
        """Extract named entities from text."""
        start_time = time.time()
        
        if not text or not text.strip():
            return EntityExtractionResult(
                entities=[],
                entity_counts={},
                processing_time_seconds=0.0
            )
        
        doc = self.nlp(text)
        
        entities = []
        seen_texts = set()
        
        for ent in doc.ents:
            if not include_all and ent.label_ not in self.PRIORITY_LABELS:
                continue
            
            key = (ent.text.lower(), ent.label_)
            if key in seen_texts:
                continue
            seen_texts.add(key)
            
            entities.append(ExtractedEntity(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char,
                confidence=1.0
            ))
        
        entity_counts = Counter(e.label for e in entities)
        processing_time = time.time() - start_time
        
        logger.info(f"Entity extraction complete: {len(entities)} entities found")
        
        return EntityExtractionResult(
            entities=entities,
            entity_counts=dict(entity_counts),
            processing_time_seconds=round(processing_time, 3)
        )


entity_service = EntityExtractionService()
