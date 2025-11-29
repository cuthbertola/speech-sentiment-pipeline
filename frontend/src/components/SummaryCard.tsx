import React from 'react';
import { FileText, Key, CheckSquare, Hash } from 'lucide-react';
import { Summary } from '../types';

interface SummaryCardProps {
  summary: Summary;
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
  summaryText: {
    color: '#374151',
    lineHeight: 1.6,
    marginBottom: '24px',
  },
  section: {
    marginBottom: '16px',
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '8px',
  },
  sectionTitle: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#6b7280',
    margin: 0,
  },
  tags: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '8px',
  },
  tagBlue: {
    padding: '4px 12px',
    background: '#eff6ff',
    color: '#2563eb',
    borderRadius: '16px',
    fontSize: '14px',
  },
  tagPurple: {
    padding: '4px 12px',
    background: '#faf5ff',
    color: '#7c3aed',
    borderRadius: '16px',
    fontSize: '14px',
    textTransform: 'capitalize' as const,
  },
  actionList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  actionItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '8px',
    fontSize: '14px',
    color: '#374151',
    marginBottom: '4px',
  },
  bullet: {
    color: '#22c55e',
    marginTop: '2px',
  },
};

const SummaryCard: React.FC<SummaryCardProps> = ({ summary }) => {
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <FileText size={20} color="#2563eb" />
        <h3 style={styles.title}>Summary</h3>
      </div>

      {summary.summary && (
        <p style={styles.summaryText}>{summary.summary}</p>
      )}

      {summary.key_phrases && summary.key_phrases.length > 0 && (
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <Key size={16} color="#6b7280" />
            <h4 style={styles.sectionTitle}>Key Phrases</h4>
          </div>
          <div style={styles.tags}>
            {summary.key_phrases.map((phrase, index) => (
              <span key={index} style={styles.tagBlue}>{phrase}</span>
            ))}
          </div>
        </div>
      )}

      {summary.action_items && summary.action_items.length > 0 && (
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <CheckSquare size={16} color="#6b7280" />
            <h4 style={styles.sectionTitle}>Action Items</h4>
          </div>
          <ul style={styles.actionList}>
            {summary.action_items.map((item, index) => (
              <li key={index} style={styles.actionItem}>
                <span style={styles.bullet}>•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {summary.topics && summary.topics.length > 0 && (
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <Hash size={16} color="#6b7280" />
            <h4 style={styles.sectionTitle}>Topics</h4>
          </div>
          <div style={styles.tags}>
            {summary.topics.map((topic, index) => (
              <span key={index} style={styles.tagPurple}>{topic}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryCard;
