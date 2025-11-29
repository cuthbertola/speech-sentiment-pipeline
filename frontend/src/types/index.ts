export interface AudioFile {
  id: number;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  duration_seconds: number | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  processed_at: string | null;
  error_message: string | null;
}

export interface WordTimestamp {
  word: string;
  start: number;
  end: number;
  confidence: number;
}

export interface TranscriptSegment {
  id: number;
  text: string;
  start: number;
  end: number;
  words?: WordTimestamp[];
}

export interface Transcript {
  id: number;
  audio_file_id: number;
  full_text: string;
  language: string | null;
  segments: TranscriptSegment[] | null;
  word_count: number | null;
  processing_time_seconds: number | null;
  created_at: string;
}

export interface SentimentScores {
  positive: number;
  negative: number;
  neutral: number;
}

export interface SegmentSentiment {
  text: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  start: number | null;
  end: number | null;
}

export interface Sentiment {
  overall_sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  scores: SentimentScores;
  segment_sentiments: SegmentSentiment[] | null;
}

export interface Entity {
  text: string;
  label: string;
  start_char: number | null;
  end_char: number | null;
  confidence: number | null;
}

export interface Entities {
  entities: Entity[];
  entity_counts: Record<string, number>;
}

export interface Summary {
  summary: string;
  key_phrases: string[];
  action_items: string[] | null;
  topics: string[] | null;
}

export interface FullAnalysis {
  audio: AudioFile;
  transcript: Transcript | null;
  sentiment: Sentiment | null;
  entities: Entities | null;
  summary: Summary | null;
  processing_complete: boolean;
}
