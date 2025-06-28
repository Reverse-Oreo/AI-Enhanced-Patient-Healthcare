import React, { useState } from 'react';
import { AgentState } from 'types/medical';
import {ApiService} from 'services/api';

interface DiagnosisFormPageProps {
  onSubmit: (symptoms: string) => void;  
  onContinue?: () => void;
  loading: boolean;
  sessionId: string | null;
  workflowState?: AgentState | null;
  workflowInfo?: any | null;
}

export const DiagnosisFormPage: React.FC<DiagnosisFormPageProps> = ({
  onSubmit,
  onContinue,
  loading,
  sessionId,
  workflowState,
  workflowInfo
}) => {
  const [symptoms, setSymptoms] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!symptoms.trim()) {
      alert('Please describe your symptoms');
      return;
    }
    onSubmit(symptoms.trim());  
  };

  const hasResults = workflowState?.textual_analysis && workflowState.textual_analysis.length > 0;
  const isAnalysisComplete = workflowState?.current_workflow_stage === 'textual_analysis_complete';

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
          🩺 AI Medical Diagnosis
        </h1>
        <p style={{ color: 'var(--secondary)', margin: 0 }}>
          {isAnalysisComplete ? 
            '✅ Initial analysis complete - Review results below' : 
            'Describe your symptoms to get started with AI-powered analysis'
          }
        </p>
        
        <div style={{
          background: '#e3f2fd',
          padding: 'var(--spacing-sm)',
          borderRadius: 'var(--radius-sm)',
          marginTop: 'var(--spacing-md)',
          fontSize: '14px',
          color: 'var(--primary)'
        }}>
          💡 Step 1 of 6: Initial symptom analysis
          {isAnalysisComplete && ' - COMPLETE ✅'}
        </div>
        
        {sessionId && (
          <div style={{ 
            marginTop: 'var(--spacing-sm)', 
            fontSize: '12px', 
            color: 'var(--secondary)',
            fontFamily: 'monospace'
          }}>
            Session: {sessionId}
          </div>
        )}
      </div>

      {/* RESULTS SECTION - Show results if available */}
      {hasResults && isAnalysisComplete && (
        <div style={{
          background: '#f0f8ff',
          border: '2px solid var(--primary)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--spacing-lg)',
          marginBottom: 'var(--spacing-lg)'
        }}>
          <h3 style={{ margin: '0 0 var(--spacing-md) 0' }}>
            📋 Analysis Results
          </h3>
          
          {/* Summary */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr',
            gap: 'var(--spacing-md)',
            marginBottom: 'var(--spacing-lg)',
            padding: 'var(--spacing-md)',
            background: 'white',
            borderRadius: 'var(--radius-md)'
          }}>
            <div>
              <strong>Diagnoses Found:</strong>
              <div style={{ fontSize: '1.2rem', color: 'var(--primary)' }}>
                {workflowState.textual_analysis?.length}
              </div>
            </div>
            
            {workflowState?.average_confidence ! == undefined && (
              <div>
                <strong>Average Confidence:</strong>
                <div style={{ 
                  fontSize: '1.2rem', 
                  color: workflowInfo.confidence_score >= 0.6 ? 'var(--success)' : 'var(--warning)'
                }}>
                  {(workflowInfo.confidence_score * 100).toFixed(1)}%
                </div>
              </div>
            )}
            
            <div>
              <strong>Status:</strong>
              <div style={{ 
                fontSize: '1rem', 
                color: 'var(--success)',
                fontWeight: '600'
              }}>
                ✅ Complete
              </div>
            </div>
          </div>

          {/* Detailed Results */}
          <h4 style={{ margin: '0 0 var(--spacing-sm) 0' }}>Possible Diagnoses:</h4>
          {workflowState.textual_analysis?.map((diagnosis, index) => (
            <div key={index} style={{
              background: index === 0 ? '#e8f5e8' : 'white',
              border: `1px solid ${index === 0 ? 'var(--success)' : '#e9ecef'}`,
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-md)',
              marginBottom: 'var(--spacing-sm)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <strong style={{ color: index === 0 ? 'var(--success)' : 'var(--dark)' }}>
                  {index === 0 ? '🥇 ' : `${index + 1}. `}
                  {diagnosis.text_diagnosis}
                </strong>
              </div>
              <div style={{
                background: diagnosis.diagnosis_confidence >= 0.8 ? 'var(--success)' :
                           diagnosis.diagnosis_confidence >= 0.6 ? 'var(--warning)' : 'var(--danger)',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                {(diagnosis.diagnosis_confidence * 100).toFixed(1)}%
              </div>
            </div>
          ))}

          {/* Next Step Information */}
          <div style={{
            background: workflowState?.image_required ? '#e3f2fd' : 
                      (workflowState?.average_confidence || 0) < 0.6 ? '#fff3cd' : '#d4edda',
            border: `1px solid ${workflowState?.image_required ? 'var(--primary)' : 
                                (workflowState?.average_confidence || 0) < 0.6 ? 'var(--warning)' : 'var(--success)'}`,
            borderRadius: 'var(--radius-md)',
            padding: 'var(--spacing-md)',
            marginTop: 'var(--spacing-md)'
          }}>
            <strong>Next Step:</strong> {
              workflowState?.image_required 
                ? 'Medical image upload required for accurate skin analysis'
                : (workflowState?.average_confidence || 0) < 0.6 
                  ? 'Follow-up questions needed to improve accuracy' 
                  : 'Ready for comprehensive analysis'
            }
            {workflowState?.image_required && (
              <div style={{ fontSize: '14px', marginTop: '4px', fontStyle: 'italic' }}>
                💡 Skin-related symptoms detected - image analysis will provide the most accurate diagnosis
              </div>
            )}
            {!workflowState?.image_required && (workflowState?.average_confidence || 0) < 0.6 && (
              <div style={{ fontSize: '14px', marginTop: '4px', fontStyle: 'italic' }}>
                ⚠️ Additional questions will be asked to improve confidence from {((workflowState?.average_confidence || 0) * 100).toFixed(1)}% to 60%
              </div>
            )}
          </div>

          {/* NEXT BUTTON - Only show when analysis is complete */}
          {onContinue && (
            <div style={{ marginTop: 'var(--spacing-lg)', textAlign: 'center' }}>
              <button
                onClick={onContinue}  // ✅ Use the hook function
                disabled={loading}
                style={{
                  padding: 'var(--spacing-md) var(--spacing-lg)',
                  background: loading ? 'var(--secondary)' : 'var(--success)',
                  color: 'white',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  minWidth: '200px'
                }}
              >
                {loading ? '⏳ Processing...' : '➡️ Continue to Next Step'}
              </button>
              <div style={{ fontSize: '12px', marginTop: '8px', color: 'var(--secondary)' }}>
                Next: {workflowState?.image_required 
                  ? '📸 Image Upload (Skin Analysis)'
                  : (workflowState?.average_confidence || 0) < 0.6 
                    ? `Follow-up Questions (Current: ${((workflowState?.average_confidence || 0) * 100).toFixed(1)}%)` 
                    : 'Overall Analysis'
                }
              </div>
            </div>
          )}
        </div>
      )}
      
      {/*DIAGNOSIS FORM - Show only if no results or allow new analysis */}
      {!hasResults && (
        <div style={{
          background: 'white',
          padding: 'var(--spacing-lg)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-md)'
        }}>
          <h2 style={{ 
            color: 'var(--dark)', 
            marginBottom: 'var(--spacing-md)',
            fontSize: '1.5rem'
          }}>
            Describe Your Symptoms
          </h2>
          
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: 'var(--spacing-lg)' }}>
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
                placeholder="Please describe your symptoms in detail (e.g., 'I have a headache, feel nauseous, and have been experiencing dizziness for the past 2 days...')"
                disabled={loading}
                style={{
                  width: '100%',
                  padding: 'var(--spacing-md)',
                  border: '2px solid #e9ecef',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '16px',
                  minHeight: '150px',
                  resize: 'vertical',
                  fontFamily: 'inherit',
                  lineHeight: '1.5'
                }}
              />
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: 'var(--spacing-xs)',
                fontSize: '12px',
                color: 'var(--secondary)'
              }}>
                {/* <span>💡 Be as detailed as possible for better analysis</span> */}
                <span>{symptoms.length}/500 characters</span>
              </div>
            </div>

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
                fontSize: '18px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background 0.2s ease'
              }}
            >
              {loading ? '🧠 AI Analyzing Symptoms...' : '🚀 Start AI Diagnosis'}
            </button>
          </form>
        </div>
      )}

      {/* Reset Option */}
      {hasResults && (
        <div style={{ textAlign: 'center', marginTop: 'var(--spacing-md)' }}>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: 'var(--spacing-sm) var(--spacing-md)',
              background: 'transparent',
              color: 'var(--secondary)',
              border: '1px solid var(--secondary)',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            🔄 Start New Analysis
          </button>
        </div>
      )}
    </div>
  );
};