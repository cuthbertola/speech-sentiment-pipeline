import React from 'react';
import { FileText, Clock, Globe } from 'lucide-react';
import { Transcript } from '../types';

interface TranscriptViewerProps {
  transcript: Transcript;
}

const styles = {
  card: {
    background: 'white',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    border: '1px solid #e5e7eb',
    padding: '24px',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '16px',
  },
  title: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
    margin: 0,
  },
  meta: {
    display: 'flex',
    gap: '16px',
    marginBottom: '16px',
    fontSize: '14px',
    color: '#6b7280',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
  content: {
    background: '#f9fafb',
    borderRadius: '8px',
    padding: '16px',
    maxHeight: '400px',
    overflowY: 'auto' as const,
  },
  segment: {
    display: 'flex',
    gap: '12px',
    marginBottom: '12px',
  },
  timestamp: {
    fontSize: '12px',
    color: '#9ca3af',
    fontFamily: 'monospace',
    minWidth: '50px',
  },
  text: {
    fontSize: '14px',
    color: '#374151',
    lineHeight: 1.6,
  },
  fullText: {
    fontSize: '14px',
    color: '#374151',
    lineHeight: 1.6,
    whiteSpace: 'pre-wrap' as const,
  },
};

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const TranscriptViewer: React.FC<TranscriptViewerProps> = ({ transcript }) => {
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <FileText size={20} color="#2563eb" />
        <h3 style={styles.title}>Transcript</h3>
      </div>

      <div style={styles.meta}>
        {transcript.language && (
          <div style={styles.metaItem}>
            <Globe size={16} />
            <span>Language: {transcript.language.toUpperCase()}</span>
          </div>
        )}
        {transcript.word_count && (
          <div style={styles.metaItem}>
            <FileText size={16} />
            <span>{transcript.word_count} words</span>
          </div>
        )}
        {transcript.processing_time_seconds && (
          <div style={styles.metaItem}>
            <Clock size={16} />
            <span>{transcript.processing_time_seconds.toFixed(1)}s</span>
          </div>
        )}
      </div>

      <div style={styles.content}>
        {transcript.segments && transcript.segments.length > 0 ? (
          <div>
            {transcript.segments.filter(s => s.text).map((segment, index) => (
              <div key={index} style={styles.segment}>
                <span style={styles.timestamp}>{formatTime(segment.start)}</span>
                <p style={styles.text}>{segment.text}</p>
              </div>
            ))}
          </div>
        ) : (
          <p style={styles.fullText}>{transcript.full_text}</p>
        )}
      </div>
    </div>
  );
};

export default TranscriptViewer;
