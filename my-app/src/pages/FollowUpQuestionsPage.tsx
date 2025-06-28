import React, { useState } from 'react';
import { AgentState } from 'types/medical';

interface FollowUpQuestionsPageProps {
  workflowState: AgentState | null;
  loading: boolean;
  onSubmitResponses: (responses: Record<string, string>) => void;
  onReset: () => void;
}

export const FollowUpQuestionsPage: React.FC<FollowUpQuestionsPageProps> = ({
  workflowState,
  loading,
  onSubmitResponses,
  onReset
}) => {
  const [responses, setResponses] = useState<Record<string, string>>({});
  
  // Extract follow-up questions from the workflow state
  const questions = workflowState?.followup_questions || [];
  
  const handleResponseChange = (question: string, response: string) => {
    setResponses(prev => ({
      ...prev,
      [question]: response
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate that all questions are answered
    const unansweredQuestions = questions.filter(q => !responses[q]?.trim());
    if (unansweredQuestions.length > 0) {
      alert('Please answer all questions before continuing.');
      return;
    }
    
    try {
      await onSubmitResponses(responses);
    } catch (error) {
      console.error('Failed to submit follow-up responses:', error);
    }
  };

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
          📝 Follow-Up Questions
        </h1>
        <p style={{ color: 'var(--secondary)', margin: 0 }}>
          Please answer these questions to improve diagnosis accuracy
        </p>
        
        <div style={{
          background: '#e3f2fd',
          padding: 'var(--spacing-sm)',
          borderRadius: 'var(--radius-sm)',
          marginTop: 'var(--spacing-md)',
          fontSize: '14px',
          color: 'var(--primary)'
        }}>
          💡 Step 2 of 6: Enhanced symptom analysis
        </div>
      </div>

      {/* Show initial diagnosis results */}
      {workflowState?.textual_analysis && workflowState.textual_analysis.length > 0 && (
        <div style={{
          background: '#f8f9fa',
          border: '1px solid #e9ecef',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--spacing-lg)',
          marginBottom: 'var(--spacing-lg)'
        }}>
          <h3 style={{ margin: '0 0 var(--spacing-md) 0' }}>
            📋 Initial Analysis Summary
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 'var(--spacing-md)',
            marginBottom: 'var(--spacing-md)'
          }}>
            <div>
              <strong>Top Diagnosis:</strong>
              <div style={{ color: 'var(--primary)' }}>
                {workflowState.textual_analysis[0]?.text_diagnosis}
              </div>
            </div>
            <div>
              <strong>Average Confidence:</strong>
              <div style={{ color: 'var(--warning)' }}>
                {workflowState.average_confidence ? 
                  `${(workflowState.average_confidence * 100).toFixed(1)}%` : 
                  'N/A'
                }
              </div>
            </div>
          </div>
          
          <div style={{
            background: '#fff3cd',
            border: '1px solid var(--warning)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--spacing-sm)',
            fontSize: '14px'
          }}>
            ⚠️ Low confidence detected - additional information needed
          </div>
        </div>
      )}

      {/* Follow-up Questions Form */}
      {questions.length > 0 ? (
        <div style={{
          background: 'white',
          padding: 'var(--spacing-lg)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-md)',
          marginBottom: 'var(--spacing-lg)'
        }}>
          <h3 style={{ 
            color: 'var(--dark)', 
            marginBottom: 'var(--spacing-md)',
            fontSize: '1.25rem'
          }}>
            Additional Questions ({questions.length})
          </h3>
          
          <form onSubmit={handleSubmit}>
            {questions.map((question, index) => (
              <div key={index} style={{ marginBottom: 'var(--spacing-lg)' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: 'var(--spacing-sm)',
                  fontWeight: '600',
                  color: 'var(--dark)'
                }}>
                  {index + 1}. {question}
                </label>
                <textarea
                  value={responses[question] || ''}
                  onChange={(e) => handleResponseChange(question, e.target.value)}
                  placeholder="Please provide a detailed answer..."
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: 'var(--spacing-md)',
                    border: '2px solid #e9ecef',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '16px',
                    minHeight: '80px',
                    resize: 'vertical',
                    fontFamily: 'inherit',
                    lineHeight: '1.5'
                  }}
                />
              </div>
            ))}

            <button
              type="submit"
              disabled={loading || questions.some(q => !responses[q]?.trim())}
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
              {loading ? '🧠 Processing Responses...' : '✅ Submit Answers'}
            </button>
          </form>
        </div>
      ) : (
        <div style={{
          background: '#fff3cd',
          border: '2px solid var(--warning)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--spacing-lg)',
          textAlign: 'center'
        }}>
          <h3 style={{ color: 'var(--warning)', margin: 0 }}>
            ⏳ Generating Follow-Up Questions...
          </h3>
          <p style={{ margin: 'var(--spacing-sm) 0 0 0' }}>
            Please wait while we prepare personalized questions based on your symptoms.
          </p>
        </div>
      )}

      {/* Reset Option */}
      <div style={{ textAlign: 'center', marginTop: 'var(--spacing-md)' }}>
        <button
          onClick={onReset}
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
          🔄 Start Over
        </button>
      </div>
    </div>
  );
};