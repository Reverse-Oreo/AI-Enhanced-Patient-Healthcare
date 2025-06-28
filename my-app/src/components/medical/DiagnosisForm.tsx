import React, { useState } from 'react';

// Define the props for our component
interface DiagnosisFormProps {
  onSubmit: (data: DiagnosisData) => void;
  loading?: boolean;
}

// Define the data structure for diagnosis
export interface DiagnosisData {
  symptoms: string;
  image?: File;
}

function DiagnosisForm({ onSubmit, loading = false }: DiagnosisFormProps) {
  const [symptoms, setSymptoms] = useState('');
  const [image, setImage] = useState<File | undefined>();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!symptoms.trim()) {
      alert('Please describe your symptoms');
      return;
    }

    onSubmit({
      symptoms: symptoms.trim(),
      image
    });
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
    }
  };

  return (
    <div style={{
      background: 'white',
      padding: 'var(--spacing-lg)',
      borderRadius: 'var(--radius-lg)',
      boxShadow: 'var(--shadow-md)',
      marginBottom: 'var(--spacing-lg)'
    }}>
      <h2 style={{ 
        color: 'var(--dark)', 
        marginBottom: 'var(--spacing-md)',
        fontSize: '1.5rem'
      }}>
        🩺 Describe Your Symptoms
      </h2>
      
      <form onSubmit={handleSubmit}>
        {/* Symptoms Input */}
        <div style={{ marginBottom: 'var(--spacing-md)' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: 'var(--spacing-sm)',
            fontWeight: '600',
            color: 'var(--dark)'
          }}>
            What symptoms are you experiencing?
          </label>
          <textarea
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            placeholder="Please describe your symptoms in detail..."
            disabled={loading}
            style={{
              width: '100%',
              padding: 'var(--spacing-sm)',
              border: '2px solid #e9ecef',
              borderRadius: 'var(--radius-md)',
              fontSize: '16px',
              minHeight: '100px',
              resize: 'vertical',
              fontFamily: 'inherit'
            }}
          />
        </div>

        {/* Image Upload */}
        <div style={{ marginBottom: 'var(--spacing-lg)' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: 'var(--spacing-sm)',
            fontWeight: '600',
            color: 'var(--dark)'
          }}>
            Medical Image (optional)
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            disabled={loading}
            style={{
              width: '100%',
              padding: 'var(--spacing-sm)',
              border: '2px dashed #e9ecef',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer'
            }}
          />
          {image && (
            <p style={{ 
              margin: 'var(--spacing-sm) 0 0 0', 
              fontSize: '14px', 
              color: 'var(--success)' 
            }}>
              ✓ Selected: {image.name}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !symptoms.trim()}
          style={{
            width: '100%',
            padding: 'var(--spacing-md)',
            background: loading ? 'var(--secondary)' : 'var(--primary)',
            color: 'white',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'background 0.2s ease'
          }}
        >
          {loading ? '⏳ Analyzing...' : '🚀 Start AI Diagnosis'}
        </button>
      </form>
    </div>
  );
}

export default DiagnosisForm;