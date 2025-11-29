import React, { useState } from 'react';
import { Mic, Activity, RefreshCw } from 'lucide-react';
import AudioUploader from './components/AudioUploader';
import TranscriptViewer from './components/TranscriptViewer';
import SentimentChart from './components/SentimentChart';
import EntityList from './components/EntityList';
import SummaryCard from './components/SummaryCard';
import { getFullAnalysis } from './services/api';
import { FullAnalysis } from './types';

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%)',
  },
  header: {
    background: 'white',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    borderBottom: '1px solid #e5e7eb',
  },
  headerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  logo: {
    background: '#2563eb',
    padding: '8px',
    borderRadius: '8px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
  },
  subtitle: {
    fontSize: '14px',
    color: '#6b7280',
    margin: 0,
  },
  resetButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    background: '#f3f4f6',
    border: 'none',
    borderRadius: '8px',
    color: '#374151',
    cursor: 'pointer',
    fontSize: '14px',
  },
  main: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '32px 16px',
  },
  centerContent: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: '48px',
  },
  heroTitle: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '8px',
  },
  heroSubtitle: {
    color: '#6b7280',
    marginBottom: '32px',
  },
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
    marginTop: '48px',
    width: '100%',
    maxWidth: '600px',
  },
  featureCard: {
    background: 'white',
    padding: '16px',
    borderRadius: '12px',
    border: '1px solid #e5e7eb',
    textAlign: 'center' as const,
  },
  featureIcon: {
    fontSize: '24px',
    marginBottom: '8px',
  },
  featureTitle: {
    fontWeight: '500',
    color: '#1f2937',
    fontSize: '14px',
  },
  featureDesc: {
    fontSize: '12px',
    color: '#6b7280',
  },
  audioInfo: {
    background: 'white',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    border: '1px solid #e5e7eb',
    padding: '24px',
    marginBottom: '24px',
  },
  audioInfoContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  audioIcon: {
    background: '#dcfce7',
    padding: '12px',
    borderRadius: '50%',
  },
  audioTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
    margin: 0,
  },
  audioMeta: {
    fontSize: '14px',
    color: '#6b7280',
    margin: 0,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '24px',
  },
  column: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '24px',
  },
  error: {
    marginTop: '16px',
    padding: '16px',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    color: '#dc2626',
  },
  footer: {
    borderTop: '1px solid #e5e7eb',
    marginTop: '48px',
    padding: '24px',
    textAlign: 'center' as const,
    fontSize: '14px',
    color: '#6b7280',
  },
};

function App() {
  const [analysis, setAnalysis] = useState<FullAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUploadComplete = async (audioId: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getFullAnalysis(audioId);
      setAnalysis(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setAnalysis(null);
    setError(null);
  };

  const features = [
    { icon: '🎤', title: 'Transcription', desc: 'Whisper AI' },
    { icon: '😊', title: 'Sentiment', desc: 'RoBERTa' },
    { icon: '👤', title: 'Entities', desc: 'spaCy NER' },
    { icon: '📝', title: 'Summary', desc: 'Key insights' },
  ];

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.headerLeft}>
            <div style={styles.logo}>
              <Mic size={24} color="white" />
            </div>
            <div>
              <h1 style={styles.title}>Speech-Sentiment Pipeline</h1>
              <p style={styles.subtitle}>Transcription • Sentiment • Entities • Summary</p>
            </div>
          </div>
          {analysis && (
            <button style={styles.resetButton} onClick={handleReset}>
              <RefreshCw size={16} />
              New Analysis
            </button>
          )}
        </div>
      </header>

      <main style={styles.main}>
        {!analysis ? (
          <div style={styles.centerContent}>
            <h2 style={styles.heroTitle}>Analyze Your Audio</h2>
            <p style={styles.heroSubtitle}>
              Upload an audio file to get instant transcription, sentiment analysis, and more
            </p>
            <AudioUploader onUploadComplete={handleUploadComplete} />
            <div style={styles.features}>
              {features.map((feature, index) => (
                <div key={index} style={styles.featureCard}>
                  <div style={styles.featureIcon}>{feature.icon}</div>
                  <div style={styles.featureTitle}>{feature.title}</div>
                  <div style={styles.featureDesc}>{feature.desc}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div>
            <div style={styles.audioInfo}>
              <div style={styles.audioInfoContent}>
                <div style={styles.audioIcon}>
                  <Activity size={24} color="#16a34a" />
                </div>
                <div>
                  <h2 style={styles.audioTitle}>{analysis.audio.original_filename}</h2>
                  <p style={styles.audioMeta}>
                    {analysis.audio.duration_seconds?.toFixed(1)}s • 
                    {(analysis.audio.file_size_bytes / 1024 / 1024).toFixed(2)} MB • 
                    Status: <span style={{ color: '#16a34a', fontWeight: 500 }}>{analysis.audio.status}</span>
                  </p>
                </div>
              </div>
            </div>

            <div style={styles.grid}>
              <div style={styles.column}>
                {analysis.transcript && <TranscriptViewer transcript={analysis.transcript} />}
                {analysis.summary && <SummaryCard summary={analysis.summary} />}
              </div>
              <div style={styles.column}>
                {analysis.sentiment && <SentimentChart sentiment={analysis.sentiment} />}
                {analysis.entities && <EntityList entities={analysis.entities} />}
              </div>
            </div>
          </div>
        )}

        {error && <div style={styles.error}>{error}</div>}
      </main>

      <footer style={styles.footer}>
        <p>Speech-Sentiment Pipeline • Built with Whisper, RoBERTa, spaCy & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
