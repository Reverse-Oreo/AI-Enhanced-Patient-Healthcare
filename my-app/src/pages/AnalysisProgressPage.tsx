import React from 'react';
import { AgentState } from 'types/medical';

interface AnalysisProgressPageProps {
  workflowState: AgentState | null;
  loading: boolean;
  onReset: () => void;
}

export const AnalysisProgressPage: React.FC<AnalysisProgressPageProps> = ({
  workflowState,
  loading,
  onReset
}) => {
  if (!workflowState) {
    return (
      <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
        <p>⏳ Loading analysis...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
      <div style={{
        background: 'white',
        padding: 'var(--spacing-xl)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-md)'
      }}>
        <h2 style={{ color: 'var(--primary)', marginBottom: 'var(--spacing-lg)' }}>
          🎯 Overall Analysis in Progress
        </h2>
        <p>Performing comprehensive analysis of all available data...</p>
        
        {loading && (
          <div style={{ margin: 'var(--spacing-lg) 0' }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid #f3f3f3',
              borderTop: '4px solid var(--primary)',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto'
            }} />
          </div>
        )}

        <button
          onClick={onReset}
          style={{
            marginTop: 'var(--spacing-lg)',
            padding: 'var(--spacing-md) var(--spacing-lg)',
            background: 'var(--secondary)',
            color: 'white',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer'
          }}
        >
          🔄 Start Over
        </button>
      </div>
    </div>
  );
};