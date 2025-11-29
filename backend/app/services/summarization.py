"""
Summarization Service for call summaries and key phrase extraction.
"""

import time
import re
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import Counter
import logging

import spacy

logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    """Result of summarization."""
    summary: str
    key_phrases: List[str]
    action_items: List[str]
    topics: List[str]
    processing_time_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "key_phrases": self.key_phrases,
            "action_items": self.action_items,
            "topics": self.topics,
            "processing_time_seconds": self.processing_time_seconds
        }


class SummarizationService:
    """Text summarization and key information extraction."""
    
    _instance = None
    _nlp = None
    
    ACTION_PATTERNS = [
        r'\b(need to|needs to|should|must|will|going to|have to|has to)\b',
        r'\b(please|kindly|ensure|make sure|follow up|schedule|call|email|send)\b',
        r'\b(action required|next step|todo|to-do|task)\b',
    ]
    
    TOPIC_KEYWORDS = {
        "billing": ["bill", "charge", "payment", "invoice", "fee", "cost", "price"],
        "technical": ["error", "issue", "problem", "bug", "crash", "not working", "broken"],
        "account": ["account", "login", "password", "profile", "settings", "access"],
        "shipping": ["delivery", "shipping", "package", "order", "track", "arrive"],
        "refund": ["refund", "return", "exchange", "money back", "cancel"],
        "product": ["product", "item", "feature", "quality", "defect"],
        "support": ["help", "support", "assist", "service", "representative"],
        "complaint": ["complaint", "unhappy", "frustrated", "disappointed", "angry"]
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_nlp(self):
        if self._nlp is None:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                spacy.cli.download("en_core_web_sm")
                self._nlp = spacy.load("en_core_web_sm")
        return self._nlp
    
    @property
    def nlp(self):
        return self._load_nlp()
    
    def _extract_sentences(self, text: str) -> List[str]:
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    def _score_sentence(self, sentence: str, word_freq: Dict[str, float]) -> float:
        doc = self.nlp(sentence.lower())
        score = 0.0
        word_count = 0
        for token in doc:
            if not token.is_stop and not token.is_punct and token.text in word_freq:
                score += word_freq[token.text]
                word_count += 1
        if word_count > 0:
            return score / (word_count ** 0.5)
        return 0.0
    
    def _build_word_frequencies(self, text: str) -> Dict[str, float]:
        doc = self.nlp(text.lower())
        word_freq = {}
        for token in doc:
            if not token.is_stop and not token.is_punct and token.is_alpha:
                word = token.text
                word_freq[word] = word_freq.get(word, 0) + 1
        if word_freq:
            max_freq = max(word_freq.values())
            word_freq = {k: v / max_freq for k, v in word_freq.items()}
        return word_freq
    
    def generate_summary(self, text: str, num_sentences: int = 3) -> str:
        """Generate extractive summary."""
        if not text or not text.strip():
            return ""
        
        sentences = self._extract_sentences(text)
        if len(sentences) <= num_sentences:
            return text
        
        word_freq = self._build_word_frequencies(text)
        scored = [(sent, self._score_sentence(sent, word_freq)) for sent in sentences]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        top_sentences = scored[:num_sentences]
        original_order = sorted(top_sentences, key=lambda x: sentences.index(x[0]))
        
        return " ".join([sent for sent, _ in original_order])
    
    def extract_key_phrases(self, text: str, top_n: int = 5) -> List[str]:
        """Extract key phrases using noun chunks."""
        if not text:
            return []
        
        doc = self.nlp(text)
        phrases = []
        
        for chunk in doc.noun_chunks:
            phrase = chunk.text.strip().lower()
            if len(phrase.split()) >= 2 and len(phrase) > 5:
                phrases.append(phrase)
        
        phrase_counts = Counter(phrases)
        return [phrase for phrase, _ in phrase_counts.most_common(top_n)]
    
    def extract_action_items(self, text: str) -> List[str]:
        """Extract potential action items."""
        if not text:
            return []
        
        sentences = self._extract_sentences(text)
        action_items = []
        
        for sent in sentences:
            for pattern in self.ACTION_PATTERNS:
                if re.search(pattern, sent.lower()):
                    if sent not in action_items:
                        action_items.append(sent)
                    break
        
        return action_items[:5]
    
    def identify_topics(self, text: str) -> List[str]:
        """Identify topics from text."""
        if not text:
            return []
        
        text_lower = text.lower()
        found_topics = []
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if topic not in found_topics:
                        found_topics.append(topic)
                    break
        
        return found_topics
    
    def summarize_full(self, text: str) -> SummaryResult:
        """Generate full summary with all components."""
        start_time = time.time()
        
        summary = self.generate_summary(text)
        key_phrases = self.extract_key_phrases(text)
        action_items = self.extract_action_items(text)
        topics = self.identify_topics(text)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Summarization complete: {len(key_phrases)} phrases, {len(action_items)} actions")
        
        return SummaryResult(
            summary=summary,
            key_phrases=key_phrases,
            action_items=action_items,
            topics=topics,
            processing_time_seconds=round(processing_time, 3)
        )


summarization_service = SummarizationService()
