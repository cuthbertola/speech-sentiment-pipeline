import React from 'react';
import { Users, Building, Calendar, DollarSign, MapPin, Tag } from 'lucide-react';
import { Entities } from '../types';

interface EntityListProps {
  entities: Entities;
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
  counts: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '8px',
    marginBottom: '16px',
  },
  countBadge: {
    padding: '4px 12px',
    background: '#f3f4f6',
    color: '#6b7280',
    borderRadius: '16px',
    fontSize: '14px',
  },
  entities: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '8px',
  },
  entity: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: '6px 12px',
    borderRadius: '16px',
    fontSize: '14px',
    border: '1px solid',
  },
  entityText: {
    fontWeight: 500,
  },
  entityLabel: {
    opacity: 0.7,
    fontSize: '12px',
  },
  empty: {
    color: '#6b7280',
    fontSize: '14px',
  },
};

const getEntityStyle = (label: string) => {
  switch (label) {
    case 'PERSON':
      return { background: '#f3e8ff', color: '#7c3aed', borderColor: '#ddd6fe' };
    case 'ORG':
      return { background: '#dbeafe', color: '#2563eb', borderColor: '#bfdbfe' };
    case 'DATE':
    case 'TIME':
      return { background: '#dcfce7', color: '#16a34a', borderColor: '#bbf7d0' };
    case 'MONEY':
      return { background: '#fef9c3', color: '#ca8a04', borderColor: '#fef08a' };
    case 'GPE':
    case 'LOC':
      return { background: '#fee2e2', color: '#dc2626', borderColor: '#fecaca' };
    case 'PRODUCT':
      return { background: '#ffedd5', color: '#ea580c', borderColor: '#fed7aa' };
    default:
      return { background: '#f3f4f6', color: '#6b7280', borderColor: '#e5e7eb' };
  }
};

const getEntityIcon = (label: string) => {
  const size = 14;
  switch (label) {
    case 'PERSON':
      return <Users size={size} />;
    case 'ORG':
      return <Building size={size} />;
    case 'DATE':
    case 'TIME':
      return <Calendar size={size} />;
    case 'MONEY':
      return <DollarSign size={size} />;
    case 'GPE':
    case 'LOC':
      return <MapPin size={size} />;
    default:
      return <Tag size={size} />;
  }
};

const EntityList: React.FC<EntityListProps> = ({ entities }) => {
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <Tag size={20} color="#2563eb" />
        <h3 style={styles.title}>Extracted Entities</h3>
      </div>

      {Object.keys(entities.entity_counts).length > 0 && (
        <div style={styles.counts}>
          {Object.entries(entities.entity_counts).map(([label, count]) => (
            <span key={label} style={styles.countBadge}>
              {label}: {count}
            </span>
          ))}
        </div>
      )}

      {entities.entities.length > 0 ? (
        <div style={styles.entities}>
          {entities.entities.map((entity, index) => {
            const entityStyle = getEntityStyle(entity.label);
            return (
              <span
                key={index}
                style={{
                  ...styles.entity,
                  background: entityStyle.background,
                  color: entityStyle.color,
                  borderColor: entityStyle.borderColor,
                }}
              >
                {getEntityIcon(entity.label)}
                <span style={styles.entityText}>{entity.text}</span>
                <span style={styles.entityLabel}>({entity.label})</span>
              </span>
            );
          })}
        </div>
      ) : (
        <p style={styles.empty}>No entities found</p>
      )}
    </div>
  );
};

export default EntityList;
