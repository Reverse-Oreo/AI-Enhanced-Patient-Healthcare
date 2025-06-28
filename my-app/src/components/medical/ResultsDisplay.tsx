import React from 'react';
import { AgentState } from 'types/medical';

interface ResultsDisplayProps {
  result: AgentState | null;
  loading?: boolean;
  error?: string;
}

function ResultsDisplay({ result, loading, error }: ResultsDisplayProps) {
  if (loading) {
    return (
      <div style={{
        background: '#f0f8ff',
        border: '2px solid var(--primary)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--spacing-lg)',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '1.2rem', color: 'var(--primary)' }}>
          ⏳ Analyzing your symptoms...
        </div>
        <div style={{ fontSize: '14px', marginTop: 'var(--spacing-sm)', opacity: 0.7 }}>
          This may take a few moments
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        background: '#fff5f5',
        border: '2px solid var(--danger)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--spacing-lg)'
      }}>
        <h3 style={{ color: 'var(--danger)', margin: 0 }}>❌ Error</h3>
        <p style={{ margin: 'var(--spacing-sm) 0 0 0' }}>{error}</p>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: 'var(--radius-lg)',
      boxShadow: 'var(--shadow-md)',
      overflow: 'hidden'
    }}>
      
      {/* FIRST STAGE: Initial Textual Analysis Results */}
      {result.textual_analysis && result.textual_analysis.length > 0 && (
        <div style={{
          padding: 'var(--spacing-lg)',
          borderBottom: '1px solid #e9ecef'
        }}>
          <h3 style={{ 
            color: 'var(--dark)', 
            marginBottom: 'var(--spacing-md)',
            fontSize: '1.25rem'
          }}>
            📋 Initial Analysis Results
          </h3>
          
          {/* Display current workflow stage if available */}
          {result.current_workflow_stage && (
            <div style={{
              background: '#e3f2fd',
              padding: 'var(--spacing-sm)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: 'var(--spacing-md)',
              fontSize: '14px',
              color: 'var(--primary)'
            }}>
              <strong>Current Stage:</strong> {result.current_workflow_stage.replace('_', ' ')}
            </div>
          )}

          {/* Show average confidence if available */}
          {result.average_confidence && (
            <div style={{
              background: '#f0f8ff',
              padding: 'var(--spacing-sm)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: 'var(--spacing-md)',
              fontSize: '14px'
            }}>
              <strong>Average Confidence:</strong> {(result.average_confidence * 100).toFixed(1)}%
              {result.average_confidence < 0.6 && (
                <span style={{ color: 'var(--warning)', marginLeft: '8px' }}>
                  (Follow-up questions may be needed)
                </span>
              )}
            </div>
          )}
          
          {/* Display all possible diagnoses from textual_analysis */}
          <div style={{ marginBottom: 'var(--spacing-md)' }}>
            <h4 style={{ margin: '0 0 var(--spacing-sm) 0', color: 'var(--dark)' }}>
              Possible Diagnoses ({result.textual_analysis.length})
            </h4>
            
            {result.textual_analysis.map((diagnosis, index) => (
              <div key={index} style={{
                background: index === 0 ? '#f0f8ff' : '#f8f9fa',
                border: `1px solid ${index === 0 ? 'var(--primary)' : '#e9ecef'}`,
                borderRadius: 'var(--radius-md)',
                padding: 'var(--spacing-md)',
                marginBottom: 'var(--spacing-sm)'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: 'var(--spacing-sm)'
                }}>
                  <div style={{ flex: 1 }}>
                    <h5 style={{ 
                      margin: 0, 
                      color: index === 0 ? 'var(--primary)' : 'var(--dark)',
                      fontSize: '1.1rem'
                    }}>
                      {index === 0 ? '🥇 ' : `${index + 1}. `}
                      {diagnosis.text_diagnosis}
                    </h5>
                  </div>
                  
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ 
                      fontSize: '1rem', 
                      fontWeight: '600',
                      color: diagnosis.diagnosis_confidence >= 0.8 ? 'var(--success)' :
                             diagnosis.diagnosis_confidence >= 0.6 ? 'var(--warning)' : 'var(--danger)'
                    }}>
                      {(diagnosis.diagnosis_confidence * 100).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--secondary)' }}>
                      Confidence
                    </div>
                  </div>
                </div>
                
                {/* Confidence bar */}
                <div style={{
                  width: '100%',
                  height: '6px',
                  background: '#e9ecef',
                  borderRadius: '3px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${diagnosis.diagnosis_confidence * 100}%`,
                    height: '100%',
                    background: diagnosis.diagnosis_confidence >= 0.8 ? 'var(--success)' :
                               diagnosis.diagnosis_confidence >= 0.6 ? 'var(--warning)' : 'var(--danger)',
                    transition: 'width 0.5s ease'
                  }} />
                </div>
              </div>
            ))}
          </div>

          {/* Show if image is required */}
          {result.image_required && (
            <div style={{
              background: '#fff3cd',
              border: '1px solid var(--warning)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-md)',
              marginTop: 'var(--spacing-md)'
            }}>
              <h5 style={{ margin: '0 0 var(--spacing-sm) 0', color: 'var(--warning)' }}>
                📸 Image Analysis Required
              </h5>
              <p style={{ margin: 0, fontSize: '14px' }}>
                Based on your symptoms, a medical image may be needed for accurate diagnosis.
                The system will request an image upload to continue the analysis.
              </p>
            </div>
          )}
        </div>
      )}

      {/* LATER STAGES: Overall Analysis Results (if available) */}
      {result.overall_analysis && (
        <div style={{
          padding: 'var(--spacing-lg)',
          borderBottom: '1px solid #e9ecef'
        }}>
          <h3 style={{ 
            color: 'var(--dark)', 
            marginBottom: 'var(--spacing-md)',
            fontSize: '1.25rem'
          }}>
            🎯 Final Diagnosis
          </h3>
          
          <div style={{
            background: '#e8f5e8',
            border: '1px solid var(--success)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--spacing-md)'
          }}>
            <h4 style={{ margin: '0 0 var(--spacing-sm) 0', color: 'var(--success)' }}>
              Final Diagnosis
            </h4>
            <p style={{ margin: '0 0 var(--spacing-sm) 0', fontSize: '1.1rem', fontWeight: '600' }}>
              {result.overall_analysis.final_diagnosis}
            </p>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr 1fr', 
              gap: 'var(--spacing-md)',
              marginTop: 'var(--spacing-md)' 
            }}>
              <div>
                <strong>Confidence:</strong>
                <div style={{ fontSize: '1.1rem', color: 'var(--success)' }}>
                  {(result.overall_analysis.final_confidence * 100).toFixed(1)}%
                </div>
              </div>
              
              <div>
                <strong>Severity:</strong>
                <div style={{ 
                  fontSize: '1.1rem',
                  color: result.overall_analysis.final_severity === 'emergency' ? 'var(--danger)' : 
                        result.overall_analysis.final_severity === 'severe' ? 'var(--warning)' : 'var(--success)',
                  textTransform: 'capitalize',
                  fontWeight: '600'
                }}>
                  {result.overall_analysis.final_severity}
                </div>
              </div>

              <div>
                <strong>Specialist:</strong>
                <div style={{ 
                  fontSize: '1rem',
                  textTransform: 'capitalize',
                  color: 'var(--dark)'
                }}>
                  {result.overall_analysis.specialist_recommendation}
                </div>
              </div>
            </div>

            {/* Medical reasoning */}
            {result.overall_analysis.reasoning && (
              <div style={{ marginTop: 'var(--spacing-md)' }}>
                <strong>Medical Reasoning:</strong>
                <p style={{ 
                  margin: 'var(--spacing-sm) 0 0 0', 
                  fontSize: '14px', 
                  lineHeight: '1.5',
                  color: 'var(--secondary)' 
                }}>
                  {result.overall_analysis.reasoning}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Healthcare Recommendations */}
      {result.healthcare_recommendation && (
        <div style={{
          padding: 'var(--spacing-lg)',
          borderBottom: '1px solid #e9ecef'
        }}>
          <h3 style={{ 
            color: 'var(--dark)', 
            marginBottom: 'var(--spacing-md)',
            fontSize: '1.25rem'
          }}>
            🏥 Healthcare Recommendations
          </h3>
          
          <div style={{
            background: '#f0f8ff',
            border: '1px solid var(--info)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--spacing-md)'
          }}>
            <div style={{ marginBottom: 'var(--spacing-sm)' }}>
              <strong>Recommendation Type:</strong> {result.healthcare_recommendation.recommendation_type}
            </div>
            
            {result.healthcare_recommendation.self_care_advice && (
              <div>
                <strong>Self-Care Advice:</strong>
                <ul style={{ margin: 'var(--spacing-sm) 0', paddingLeft: '20px' }}>
                  {result.healthcare_recommendation.self_care_advice.map((advice, index) => (
                    <li key={index} style={{ margin: '4px 0' }}>{advice}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Final Medical Report */}
      {result.medical_report && (
        <div style={{
          padding: 'var(--spacing-lg)',
          background: '#f8f9fa'
        }}>
          <h3 style={{ 
            color: 'var(--dark)', 
            marginBottom: 'var(--spacing-md)',
            fontSize: '1.25rem'
          }}>
            📄 Medical Report
          </h3>
          <pre style={{
            whiteSpace: 'pre-wrap',
            fontFamily: 'inherit',
            fontSize: '14px',
            lineHeight: '1.6',
            margin: 0,
            color: 'var(--dark)'
          }}>
            {result.medical_report}
          </pre>
        </div>
      )}

      {/* Workflow Progress Debug Info */}
      {result.workflow_path && result.workflow_path.length > 0 && (
        <div style={{
          padding: 'var(--spacing-md)',
          background: '#f8f9fa',
          borderTop: '1px solid #e9ecef'
        }}>
          <details>
            <summary style={{ cursor: 'pointer', fontSize: '14px', color: 'var(--secondary)' }}>
              🔍 Workflow Progress ({result.workflow_path.length} stages)
            </summary>
            <div style={{ marginTop: 'var(--spacing-sm)', fontSize: '12px' }}>
              <strong>Path:</strong> {result.workflow_path.join(' → ')}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}

export default ResultsDisplay;