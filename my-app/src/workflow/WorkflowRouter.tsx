// To organize the routing of frontend UI pages according to the current workflow stage (AgentState)

import React from 'react';
import { AgentState } from 'types/medical';

// Import all page components (we'll create these next)
import { DiagnosisFormPage } from 'pages/DiagnosisFormPage';
import { FollowUpQuestionsPage } from 'pages/FollowUpQuestionsPage';
import { ImageAnalysisPage } from 'pages/ImageAnalysisPage';
import { AnalysisProgressPage } from 'pages/AnalysisProgressPage';
import { RecommendationsPage } from 'pages/RecommendationsPage';
import { FinalReportPage } from 'pages/FinalReportPage';
import { ErrorPage } from 'pages/ErrorPage';

interface WorkflowRouterProps {
  workflowState: AgentState | null;
  loading: boolean;
  error: string | null;
  sessionId: string | null;
  onStartDiagnosis: (symptoms: string) => Promise<void>;
  onSubmitFollowUp: (responses: Record<string, string>) => Promise<void>;
  onSubmitImage: (image: File) => Promise<void>;
  onReset: () => void;
  onContinue: () => void; 
}

export const WorkflowRouter: React.FC<WorkflowRouterProps> = ({
  workflowState,
  loading,
  error,
  sessionId,
  onStartDiagnosis,
  onSubmitFollowUp,
  onSubmitImage,
  onReset,
  onContinue
}) => {
  
  // Handle error state
  if (error) {
    return (
      <ErrorPage 
        error={error}
        onReset={onReset}
      />
    );
  }

  // Handle initial state (no workflow started)
  if (!workflowState && !loading) {
    return (
      <DiagnosisFormPage
        onSubmit={onStartDiagnosis}
        onContinue={onContinue}
        loading={loading}
        sessionId={sessionId}
        workflowState={null}
        workflowInfo={null}
      />
    );
  }

  // Get current workflow stage
  const currentStage = workflowState?.current_workflow_stage || 'textual_analysis';
  
  console.log('🔄 Current workflow stage:', currentStage);

  // Route to appropriate page based on workflow stage
  switch (currentStage) {
    //INITIAL DIAGNOSIS: Show form and results
    case 'textual_analysis':
    case 'textual_analysis_complete':
      return (
        <DiagnosisFormPage
          onSubmit={onStartDiagnosis}
          onContinue={onContinue}
          loading={loading}
          sessionId={sessionId}
          workflowState={workflowState}
          workflowInfo={null} // Will be passed from useDiagnosis when available
        />
      );

    // FOLLOW-UP QUESTIONS: Generate or collect responses
    case 'generating_followup_questions':
    case 'awaiting_followup_responses':
      return (
        <FollowUpQuestionsPage
          workflowState={workflowState}
          loading={loading}
          onSubmitResponses={onSubmitFollowUp}
          onReset={onReset}
        />
      );

    // IMAGE ANALYSIS: Upload and analyze image
    case 'awaiting_image_upload':
    case 'analyzing_image':
    case 'image_analysis_complete':
      return (
        <ImageAnalysisPage
          workflowState={workflowState}
          loading={loading}
          onSubmitImage={onSubmitImage} 
          onReset={onReset}
        />
      );

    // OVERALL ANALYSIS: Processing all data
    case 'overall_analysis':
    case 'followup_analysis_complete':
      return (
        <AnalysisProgressPage
          workflowState={workflowState}
          loading={loading}
          onReset={onReset}
        />
      );

    // HEALTHCARE RECOMMENDATIONS
    case 'overall_analysis_complete':
    case 'generating_healthcare_recommendations':
      return (
        <RecommendationsPage
          workflowState={workflowState}
          loading={loading}
          onReset={onReset}
        />
      );

    // FINAL MEDICAL REPORT
    case 'healthcare_recommendation_complete':
    case 'generating_medical_report':
    case 'workflow_complete':
      return (
        <FinalReportPage
          workflowState={workflowState}
          loading={loading}
          onReset={onReset}
        />
      );

  default:
    console.warn('⚠️ Unknown workflow stage:', currentStage);
    return (
      <ErrorPage 
        error={`Unknown workflow stage: ${currentStage}`}
        onReset={onReset}
      />
    );
  }
};