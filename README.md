# 🎙️ Speech-to-Text + Sentiment Analysis Pipeline

Real-time speech transcription with sentiment analysis and entity extraction for customer service call analysis.

## 🎯 Features

- **Audio Upload**: Support for MP3, WAV, M4A, FLAC, OGG formats
- **Transcription**: Real-time speech-to-text using OpenAI Whisper
- **Sentiment Analysis**: Positive/negative/neutral classification using RoBERTa
- **Entity Extraction**: Named entity recognition (names, dates, organizations)
- **Summarization**: Automatic call summary with key phrases and action items
- **Word Timestamps**: Word-level timing for transcript synchronization

## 📊 Target Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| WER | <10% | Word Error Rate |
| Sentiment Accuracy | 85%+ | Classification accuracy |
| Processing Time | <2x audio | 1 min audio = <2 min processing |
| Entity F1 | 0.82+ | Entity extraction quality |

## 🛠️ Tech Stack

- **Speech-to-Text**: OpenAI Whisper
- **NLP**: spaCy, HuggingFace Transformers
- **Sentiment**: RoBERTa (cardiffnlp/twitter-roberta-base-sentiment)
- **Backend**: FastAPI
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **MLOps**: MLflow

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- FFmpeg

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/speech-sentiment-pipeline.git
cd speech-sentiment-pipeline

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# Run server
python -m uvicorn app.main:app --reload --port 8002
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/audio/upload` | Upload audio file |
| POST | `/api/v1/audio/{id}/process` | Process audio through pipeline |
| GET | `/api/v1/audio/` | List all audio files |
| GET | `/api/v1/analysis/{id}/full` | Get full analysis |
| GET | `/api/v1/analysis/{id}/transcript` | Get transcript |
| GET | `/api/v1/analysis/{id}/sentiment` | Get sentiment analysis |
| GET | `/api/v1/analysis/{id}/entities` | Get extracted entities |
| GET | `/api/v1/analysis/{id}/summary` | Get summary |
| GET | `/api/v1/health/` | Health check |

### Example Usage
```bash
# Upload audio
curl -X POST "http://localhost:8002/api/v1/audio/upload" \
  -F "file=@audio.wav"

# Process audio (returns transcript, sentiment, entities, summary)
curl -X POST "http://localhost:8002/api/v1/audio/1/process"

# Get full analysis
curl "http://localhost:8002/api/v1/analysis/1/full"
```

## 📁 Project Structure
```
speech-sentiment-pipeline/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── api/routes/          # API endpoints
│   │   ├── models/              # Database & Pydantic models
│   │   ├── services/            # ML services
│   │   │   ├── transcription.py # Whisper service
│   │   │   ├── sentiment.py     # Sentiment analysis
│   │   │   ├── entity.py        # Entity extraction
│   │   │   ├── summarization.py # Summarization
│   │   │   └── pipeline.py      # Orchestration
│   │   └── core/                # Database connection
│   ├── requirements.txt
│   └── .env
├── data/
│   └── audio_samples/
└── README.md
```

## 🔧 Configuration

Environment variables (`.env`):
```env
WHISPER_MODEL_SIZE=base    # tiny, base, small, medium, large
WHISPER_DEVICE=cpu         # cpu or cuda
SENTIMENT_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
```

## 📈 API Response Example
```json
{
  "audio": {
    "id": 1,
    "filename": "call_001.wav",
    "duration_seconds": 122.0,
    "status": "completed"
  },
  "transcript": {
    "full_text": "Hello, I'm calling about my order...",
    "language": "en",
    "word_count": 150
  },
  "sentiment": {
    "overall_sentiment": "neutral",
    "confidence": 0.85,
    "scores": {"positive": 0.10, "negative": 0.05, "neutral": 0.85}
  },
  "entities": {
    "entities": [{"text": "John Smith", "label": "PERSON"}],
    "entity_counts": {"PERSON": 1}
  },
  "summary": {
    "summary": "Customer called regarding order status...",
    "key_phrases": ["order status", "delivery date"],
    "action_items": ["Follow up on delivery"]
  }
}
```

## 👤 Author

**Olawale Badekale**
- GitHub: [@cuthbertola](https://github.com/cuthbertola)
- LinkedIn: [Olawale Badekale](https://linkedin.com/in/olawalebadekale)

## 📄 License

This project is licensed under the MIT License.
