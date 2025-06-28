import React from 'react';
import './App.css';
import { WorkflowRouter } from 'workflow/WorkflowRouter';
import { useDiagnosis } from 'hooks/useDiagnosis';

function App(): React.JSX.Element {
  const { 
    loading, 
    result, 
    error, 
    sessionId, 
    currentStage,
    workflowInfo,
    startDiagnosis, 
    submitFollowUp,
    submitImageAnalysis,
    continueWorkflow,
    continueToNextStep,
    testConnection, 
    reset 
  } = useDiagnosis();

const handleStartDiagnosis = async (symptoms: string) => {
  try {
    await startDiagnosis({
      symptoms
    });
    
    console.log('✅ Diagnosis completed successfully');
    
  } catch (err) {
    console.error('❌ Diagnosis submission failed:', err);
  }
};

const handleContinueToNext = async () => {
  try {
    const result = await continueToNextStep();
    
    if (result?.needsImageUpload) {
      console.log('📸 Ready for image upload');
    }
    
  } catch (err) {
    console.error('❌ Continue failed:', err);
  }
};

const handleSubmitFollowUp = async (responses: Record<string, string>) => {
  try {
    await submitFollowUp(responses);
    
    // Auto-continue workflow
    setTimeout(async () => {
      try {
        await continueWorkflow();
      } catch (err) {
        console.log('Workflow completed or needs user input');
      }
    }, 1000);
    
  } catch (err) {
    console.error('❌ Follow-up submission failed:', err);
  }
};

const handleImageSubmit = async (image: File) => {
  try {
    await submitImageAnalysis(image);
    
    // Auto-continue workflow
    setTimeout(async () => {
      try {
        await continueWorkflow();
      } catch (err) {
        console.log('Workflow completed');
      }
    }, 1000);
    
  } catch (err) {
    console.error('❌ Image submission failed:', err);
  }
};

  const handleTestConnection = async () => {
    try {
      const healthData = await testConnection();
      alert(`✅ Backend Connected!\nStatus: ${healthData.status}\nActive Connections: ${healthData.features.active_connections}`);
    } catch (err) {
      alert(`❌ Connection Failed:\n${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="App">
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, var(--medical-blue) 0%, var(--primary-dark) 100%)',
        color: 'white',
        padding: 'var(--spacing-lg) 0',
        marginBottom: 'var(--spacing-xl)'
      }}>
        <div style={{ 
          maxWidth: '1200px', 
          margin: '0 auto', 
          padding: '0 var(--spacing-md)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.8rem' }}>
              AI Medical Assistant
            </h1>
            <p style={{ margin: '4px 0 0 0', opacity: 0.9, fontSize: '14px' }}>
              Powered by Node-Based LangGraph Workflow
            </p>
          </div>
          
          <button
            onClick={handleTestConnection}
            style={{
              padding: 'var(--spacing-sm) var(--spacing-md)',
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.3)',
              borderRadius: 'var(--radius-md)',
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            🔧 Test Backend
          </button>
        </div>
      </header>

      {/* Main Content - Workflow Router */}
      <main style={{ 
        padding: '0 var(--spacing-md)',
        minHeight: '60vh'
      }}>
        <WorkflowRouter
          workflowState={result}
          loading={loading}
          error={error}
          sessionId={sessionId}
          onStartDiagnosis={handleStartDiagnosis}
          onContinue={handleContinueToNext}
          onSubmitFollowUp={handleSubmitFollowUp}
          onSubmitImage={handleImageSubmit}
          onReset={reset}
        />
      </main>

      {/* Footer */}
      <footer style={{
        background: '#f8f9fa',
        padding: 'var(--spacing-md)',
        textAlign: 'center',
        marginTop: 'var(--spacing-xxl)',
        borderTop: '1px solid #e9ecef',
        fontSize: '12px',
        color: 'var(--secondary)'
      }}>
        <p>🔍 Debug: Session {sessionId} | Stage: {currentStage || 'none'}</p>
        <p>Node-Based API: Each workflow step is an independent endpoint</p>
      </footer>
    </div>
  );
}

export default App;