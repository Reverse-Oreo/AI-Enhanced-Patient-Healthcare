import React, { useState } from 'react';
import { AgentState } from 'types/medical';

interface ImageAnalysisPageProps {
  workflowState: AgentState | null;
  loading: boolean;
  onSubmitImage: (image: File) => Promise<void>;
  onReset: () => void;
}

export const ImageAnalysisPage: React.FC<ImageAnalysisPageProps> = ({
  workflowState,
  loading,
  onSubmitImage,
  onReset
}) => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedImage) {
      alert('Please select an image first');
      return;
    }
    await onSubmitImage(selectedImage);
  };

  const currentStage = workflowState?.current_workflow_stage || '';
  const isAnalyzing = currentStage === 'analyzing_image';
  const hasResults = workflowState?.skin_lesion_analysis;

  if (!workflowState) {
    return (
      <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
        <p>⏳ Loading image analysis...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      {/* Page Header */}
      <div style={{
        background: 'white',
        padding: 'var(--spacing-lg)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-md)',
        marginBottom: 'var(--spacing-lg)',
        textAlign: 'center'
      }}>
        <h1 style={{ 
          color: 'var(--primary)', 
          marginBottom: 'var(--spacing-sm)',
          fontSize: '2rem'
        }}>
          📸 Medical Image Analysis
        </h1>
        <p style={{ color: 'var(--secondary)', margin: 0 }}>
          Upload a medical image for AI-powered analysis
        </p>
        
        <div style={{
          background: '#e3f2fd',
          padding: 'var(--spacing-sm)',
          borderRadius: 'var(--radius-sm)',
          marginTop: 'var(--spacing-md)',
          fontSize: '14px',
          color: 'var(--primary)'
        }}>
          <strong>Current Stage:</strong> {currentStage.replace('_', ' ')}
        </div>
      </div>

      {/* Show Results if Available */}
      {hasResults && (
        <div style={{
          background: '#f0f8ff',
          border: '2px solid var(--primary)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--spacing-lg)',
          marginBottom: 'var(--spacing-lg)'
        }}>
          <h3 style={{ margin: '0 0 var(--spacing-md) 0' }}>
            🎯 Image Analysis Results
          </h3>
          <p><strong>Diagnosis:</strong> {hasResults.image_diagnosis}</p>
          {hasResults.confidence_score && (
            <p><strong>Confidence:</strong> {JSON.stringify(hasResults.confidence_score)}</p>
          )}
        </div>
      )}

      {/* Image Upload Form */}
      <div style={{
        background: 'white',
        padding: 'var(--spacing-lg)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-md)'
      }}>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: 'var(--spacing-sm)',
              fontWeight: '600',
              color: 'var(--dark)'
            }}>
              Select Medical Image
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
          </div>

          {/* Image Preview */}
          {preview && (
            <div style={{ marginBottom: 'var(--spacing-lg)', textAlign: 'center' }}>
              <img
                src={preview}
                alt="Selected medical image"
                style={{
                  maxWidth: '300px',
                  maxHeight: '300px',
                  borderRadius: 'var(--radius-md)',
                  border: '2px solid #e9ecef'
                }}
              />
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
            <button
              type="submit"
              disabled={loading || !selectedImage}
              style={{
                flex: 1,
                padding: 'var(--spacing-md)',
                background: (loading || !selectedImage) ? 'var(--secondary)' : 'var(--primary)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontSize: '16px',
                fontWeight: '600',
                cursor: (loading || !selectedImage) ? 'not-allowed' : 'pointer'
              }}
            >
              {isAnalyzing ? '🔍 Analyzing Image...' : '📸 Analyze Image'}
            </button>
            
            <button
              type="button"
              onClick={onReset}
              disabled={loading}
              style={{
                padding: 'var(--spacing-md) var(--spacing-lg)',
                background: 'var(--secondary)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontSize: '16px',
                cursor: 'pointer'
              }}
            >
              🔄 Start Over
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};