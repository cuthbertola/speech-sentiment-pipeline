import React from 'react';
import { Smile, Frown, Meh, TrendingUp } from 'lucide-react';
import { Sentiment } from '../types';

interface SentimentChartProps {
  sentiment: Sentiment;
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
  sentimentBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
  },
  sentimentPositive: {
    background: '#dcfce7',
    border: '1px solid #bbf7d0',
    color: '#16a34a',
  },
  sentimentNegative: {
    background: '#fef2f2',
    border: '1px solid #fecaca',
    color: '#dc2626',
  },
  sentimentNeutral: {
    background: '#fefce8',
    border: '1px solid #fef08a',
    color: '#ca8a04',
  },
  sentimentLabel: {
    fontSize: '18px',
    fontWeight: '600',
    textTransform: 'capitalize' as const,
    margin: 0,
  },
  sentimentConfidence: {
    fontSize: '14px',
    opacity: 0.8,
    margin: 0,
  },
  barContainer: {
    marginBottom: '12px',
  },
  barHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '14px',
    marginBottom: '4px',
  },
  barLabel: {
    color: '#6b7280',
  },
  barTrack: {
    height: '8px',
    background: '#f3f4f6',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.3s',
  },
};

const SentimentChart: React.FC<SentimentChartProps> = ({ sentiment }) => {
  const getSentimentIcon = () => {
    switch (sentiment.overall_sentiment) {
      case 'positive':
        return <Smile size={32} color="#16a34a" />;
      case 'negative':
        return <Frown size={32} color="#dc2626" />;
      default:
        return <Meh size={32} color="#ca8a04" />;
    }
  };

  const getSentimentStyle = () => {
    switch (sentiment.overall_sentiment) {
      case 'positive':
        return styles.sentimentPositive;
      case 'negative':
        return styles.sentimentNegative;
      default:
        return styles.sentimentNeutral;
    }
  };

  const bars = [
    { label: 'Positive', value: sentiment.scores.positive, color: '#22c55e' },
    { label: 'Neutral', value: sentiment.scores.neutral, color: '#eab308' },
    { label: 'Negative', value: sentiment.scores.negative, color: '#ef4444' },
  ];

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <TrendingUp size={20} color="#2563eb" />
        <h3 style={styles.title}>Sentiment Analysis</h3>
      </div>

      <div style={{ ...styles.sentimentBox, ...getSentimentStyle() }}>
        {getSentimentIcon()}
        <div>
          <p style={styles.sentimentLabel}>{sentiment.overall_sentiment}</p>
          <p style={styles.sentimentConfidence}>
            {(sentiment.confidence * 100).toFixed(1)}% confidence
          </p>
        </div>
      </div>

      <div>
        {bars.map((bar, index) => (
          <div key={index} style={styles.barContainer}>
            <div style={styles.barHeader}>
              <span style={styles.barLabel}>{bar.label}</span>
              <span style={{ color: bar.color, fontWeight: 500 }}>
                {(bar.value * 100).toFixed(1)}%
              </span>
            </div>
            <div style={styles.barTrack}>
              <div
                style={{
                  ...styles.barFill,
                  width: `${bar.value * 100}%`,
                  background: bar.color,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SentimentChart;
