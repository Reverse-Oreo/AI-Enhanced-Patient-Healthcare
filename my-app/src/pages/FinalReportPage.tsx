import React from 'react';
import { AgentState } from 'types/medical';

interface FinalReportPageProps {
  workflowState: AgentState | null;
  loading: boolean;
  onReset: () => void;
}

export const FinalReportPage: React.FC<FinalReportPageProps> = ({
  workflowState,
  loading,
  onReset
}) => {

  if (!workflowState) {
    return (
      <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
        <p>⏳ Loading report...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{
        background: 'white',
        padding: 'var(--spacing-xl)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-md)',
        textAlign: 'center'
      }}>
        <h2 style={{ color: 'var(--primary)', marginBottom: 'var(--spacing-lg)' }}>
          📄 Final Medical Report
        </h2>
        <p>Your comprehensive medical analysis report is ready.</p>
        
        {workflowState?.medical_report ? (
          <div style={{
            background: '#f8f9fa',
            padding: 'var(--spacing-lg)',
            borderRadius: 'var(--radius-md)',
            textAlign: 'left',
            margin: 'var(--spacing-lg) 0'
          }}>
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '14px' }}>
              {workflowState.medical_report}
            </pre>
          </div>
        ) : (
          <p>Report generation in progress...</p>
        )}

        <button
          onClick={onReset}
          style={{
            marginTop: 'var(--spacing-lg)',
            padding: 'var(--spacing-md) var(--spacing-lg)',
            background: 'var(--primary)',
            color: 'white',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer'
          }}
        >
          🆕 New Diagnosis
        </button>
      </div>
    </div>
  );
};