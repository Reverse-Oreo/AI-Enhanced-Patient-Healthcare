import { useState, useCallback } from 'react';
import { AgentState } from 'types/medical';
import { ApiService, DiagnosisRequest } from 'services/api';

interface DiagnosisState {
  loading: boolean;
  result: AgentState | null;
  error: string | null;
  sessionId: string | null;
  currentStage: string | null;
  workflowInfo: any | null;
}

export const useDiagnosis = () => {
  const [state, setState] = useState<DiagnosisState>({
    loading: false,
    result: null,
    error: null,
    sessionId: null,
    currentStage: null, 
    workflowInfo: null
  });

  // Test backend connection
  const testConnection = useCallback(async () => {
    try {
      const healthData = await ApiService.testConnection();
      return healthData;
    } catch (error) {
      throw error;
    }
  }, []);

  // ✅ NODE 1: Start diagnosis with textual analysis
  const startDiagnosis = useCallback(async (request: DiagnosisRequest) => {
    setState(prev => ({
      ...prev,
      loading: true,
      error: null
    }));

    try {
      const response = await ApiService.startTextualAnalysis(request);
      
      setState(prev => ({
        ...prev,
        loading: false,
        result: response.result,
        sessionId: response.session_id,
        currentStage: response.result.current_workflow_stage,
        workflowInfo: response.workflow_info
      }));

      return response;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Diagnosis failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, []);

  // ✅ NODE 2: Follow-up questions
  const submitFollowUp = useCallback(async (responses: Record<string, string>) => {
    if (!state.sessionId || !state.result) {
      throw new Error('No active session for follow-up');
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await ApiService.runFollowupQuestions(
        state.sessionId,
        state.result,
        responses
      );
      
      setState(prev => ({
        ...prev,
        loading: false,
        result: response.result,
        currentStage: response.result.current_workflow_stage
      }));

      return response;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Follow-up failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, [state.sessionId, state.result]);

  // ✅ NODE 3: Image analysis
  const submitImageAnalysis = useCallback(async (image?: File) => {
    if (!state.sessionId || !state.result) {
      throw new Error('No active session for image analysis');
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await ApiService.runImageAnalysis(
        state.sessionId,
        state.result,
        image
      );
      
      setState(prev => ({
        ...prev,
        loading: false,
        result: response.result,
        currentStage: response.result.current_workflow_stage
      }));

      return response;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Image analysis failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, [state.sessionId, state.result]);

  // ✅ NODE 4: Overall analysis  
  const runOverallAnalysis = useCallback(async () => {
    if (!state.sessionId || !state.result) {
      throw new Error('No active session for overall analysis');
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await ApiService.runOverallAnalysis(
        state.sessionId,
        state.result
      );
      
      setState(prev => ({
        ...prev,
        loading: false,
        result: response.result,
        currentStage: response.result.current_workflow_stage
      }));

      return response;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Overall analysis failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, [state.sessionId, state.result]);

  // ✅ NODE 5: Healthcare recommendations
  const runHealthcareRecommendations = useCallback(async () => {
    if (!state.sessionId || !state.result) {
      throw new Error('No active session for healthcare recommendations');
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await ApiService.runHealthcareRecommendations(
        state.sessionId,
        state.result
      );
      
      setState(prev => ({
        ...prev,
        loading: false,
        result: response.result,
        currentStage: response.result.current_workflow_stage
      }));

      return response;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Healthcare recommendations failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, [state.sessionId, state.result]);

  // ✅ NODE 6: Medical report
  const runMedicalReport = useCallback(async () => {
    if (!state.sessionId || !state.result) {
      throw new Error('No active session for medical report');
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await ApiService.runMedicalReport(
        state.sessionId,
        state.result
      );
      
      setState(prev => ({
        ...prev,
        loading: false,
        result: response.result,
        currentStage: response.result.current_workflow_stage
      }));

      return response;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Medical report failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, [state.sessionId, state.result]);

  // ✅ AUTO-PROGRESSION: Continue to next recommended node
  const continueWorkflow = useCallback(async () => {
    if (!state.workflowInfo || !state.sessionId || !state.result) {
      throw new Error('No workflow info available');
    }

    const { next_endpoint, needs_user_input, workflow_complete } = state.workflowInfo;

    // Check if user input is needed
    if (needs_user_input) {
      return { needsUserInput: needs_user_input };
    }

    // Check if workflow is complete
    if (workflow_complete) {
      return { workflowComplete: true };
    }

    // Continue to next step
    if (next_endpoint) {
      return await callNextEndpoint(next_endpoint);
    }

    throw new Error('No next step determined');
  }, [state.workflowInfo, state.sessionId, state.result]);


  const callNextEndpoint = async (endpoint: string) => {
    // Map endpoint to API call
    switch (endpoint) {
      case '/patient/overall_analysis':
        return await runOverallAnalysis();
      case '/patient/healthcare_recommendations':
        return await runHealthcareRecommendations();
      case '/patient/medical_report':
        return await runMedicalReport();
      default:
        throw new Error(`Unknown endpoint: ${endpoint}`);
    }
  };

  // Reset diagnosis state
  const reset = useCallback(() => {
    setState({
      loading: false,
      result: null,
      error: null,
      sessionId: null,
      currentStage: null,
      workflowInfo: null
    });
  }, []);

const continueToNextStep = useCallback(async () => {
  if (!state.workflowInfo) {
    throw new Error('No workflow info available');
  }
  
  const { next_endpoint, needs_user_input, next_step_description } = state.workflowInfo;
  
  console.log('🔄 Continue to next step:', next_endpoint);
  console.log('🔍 Needs user input:', needs_user_input);
  
  // ✅ ACTUAL IMPLEMENTATION: Route to the appropriate next step
  if (needs_user_input === 'followup_questions') {
    // For follow-up questions, need to first generate the questions
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await ApiService.runFollowupQuestions(
        state.sessionId!,
        state.result!
        // No responses yet - this will generate questions
      );
      
      setState(prev => ({
        ...prev,
        loading: false,
        result: response.result,
        currentStage: response.result.current_workflow_stage,
        workflowInfo: null // Clear workflow info since we're now in a different stage
      }));
      
      console.log('✅ Follow-up questions generated successfully');
      return response;
      
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to generate follow-up questions'
      }));
      throw error;
    }
  } else if (needs_user_input === 'image_upload') {
    // For image upload, update state to show image upload interface
    setState(prev => ({
      ...prev,
      currentStage: 'awaiting_image_upload',
      workflowInfo: null
    }));
    console.log('📸 Ready for image upload');
    return { needsImageUpload: true };
    
  } else if (!needs_user_input && next_endpoint) {
    // Auto-continue to next endpoint
    return await callNextEndpoint(next_endpoint);
  } else {
    throw new Error(`Unknown next step: ${next_step_description}`);
  }
}, [state.workflowInfo, state.sessionId, state.result]);


  return {
    ...state,
    startDiagnosis,
    continueToNextStep,
    submitFollowUp,
    submitImageAnalysis,
    runOverallAnalysis,
    runHealthcareRecommendations,
    runMedicalReport,
    continueWorkflow,
    testConnection,
    reset
  };
};