import React, { useState, useRef } from 'react';
import { Mic, Loader2 } from 'lucide-react';
import { uploadAudio, processAudio } from '../services/api';

interface AudioUploaderProps {
  onUploadComplete: (audioId: number) => void;
}

const styles = {
  container: {
    width: '100%',
    maxWidth: '600px',
    margin: '0 auto',
  },
  dropzone: {
    border: '2px dashed #d1d5db',
    borderRadius: '12px',
    padding: '48px',
    textAlign: 'center' as const,
    cursor: 'pointer',
    transition: 'all 0.2s',
    background: 'white',
  },
  dropzoneActive: {
    borderColor: '#3b82f6',
    background: '#eff6ff',
  },
  dropzoneDisabled: {
    pointerEvents: 'none' as const,
    opacity: 0.6,
  },
  iconWrapper: {
    background: '#dbeafe',
    padding: '16px',
    borderRadius: '50%',
    display: 'inline-block',
    marginBottom: '16px',
  },
  title: {
    fontSize: '18px',
    fontWeight: '500',
    color: '#374151',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '14px',
    color: '#6b7280',
    marginBottom: '16px',
  },
  formats: {
    fontSize: '12px',
    color: '#9ca3af',
  },
  spinner: {
    animation: 'spin 1s linear infinite',
  },
  status: {
    fontSize: '18px',
    fontWeight: '500',
    color: '#374151',
  },
  statusSub: {
    fontSize: '14px',
    color: '#6b7280',
    marginTop: '8px',
  },
  error: {
    marginTop: '16px',
    padding: '16px',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    color: '#dc2626',
    fontSize: '14px',
  },
};

const AudioUploader: React.FC<AudioUploaderProps> = ({ onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await handleFile(files[0]);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    if (!['mp3', 'wav', 'm4a', 'flac', 'ogg'].includes(extension || '')) {
      setError('Please upload an audio file (MP3, WAV, M4A, FLAC, OGG)');
      return;
    }

    setError(null);
    setIsUploading(true);
    setStatus('Uploading audio file...');

    try {
      const uploadResult = await uploadAudio(file);
      setStatus('Processing audio through pipeline...');
      setIsUploading(false);
      setIsProcessing(true);

      await processAudio(uploadResult.id);
      setStatus('Processing complete!');
      setIsProcessing(false);
      onUploadComplete(uploadResult.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process audio');
      setIsUploading(false);
      setIsProcessing(false);
      setStatus('');
    }
  };

  const dropzoneStyle = {
    ...styles.dropzone,
    ...(isDragging ? styles.dropzoneActive : {}),
    ...((isUploading || isProcessing) ? styles.dropzoneDisabled : {}),
  };

  return (
    <div style={styles.container}>
      <div
        style={dropzoneStyle}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".mp3,.wav,.m4a,.flac,.ogg"
          style={{ display: 'none' }}
        />
        
        {isUploading || isProcessing ? (
          <div>
            <Loader2 size={48} color="#3b82f6" style={{ marginBottom: '16px', animation: 'spin 1s linear infinite' }} />
            <p style={styles.status}>{status}</p>
            <p style={styles.statusSub}>This may take a few minutes...</p>
          </div>
        ) : (
          <>
            <div style={styles.iconWrapper}>
              <Mic size={32} color="#2563eb" />
            </div>
            <p style={styles.title}>Drop your audio file here</p>
            <p style={styles.subtitle}>or click to browse</p>
            <p style={styles.formats}>Supports MP3, WAV, M4A, FLAC, OGG (max 100MB)</p>
          </>
        )}
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AudioUploader;
