from schemas.medical_schemas import AgentState
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WorkflowStateManager:
    """Centralized workflow state management - MINIMAL VERSION for textual analysis only"""
    
    def __init__(self):
        self.CONFIDENCE_THRESHOLD = 0.6
    
    def calculate_average_confidence(self, state: AgentState) -> float:
        """Calculate average confidence from textual analysis"""
        textual_analysis = state.get("textual_analysis", [])
        if textual_analysis and isinstance(textual_analysis, list):
            confidence_scores = [
                diagnosis.get("diagnosis_confidence", 0.0) 
                for diagnosis in textual_analysis
            ]
            return sum(confidence_scores) / len(confidence_scores)
        return 0.0
    
    def update_workflow_stage_and_determine_next(self, state: AgentState, completed_node: str) -> Dict[str, Any]:
        """Update workflow stage and determine next endpoint - TEXTUAL ANALYSIS ONLY"""
        
        if completed_node == "textual_analysis":
            # ✅ Set completion stage - this is what was missing!
            state["current_workflow_stage"] = "textual_analysis_complete"
            
            # Calculate confidence
            if "average_confidence" not in state:
                state["average_confidence"] = self.calculate_average_confidence(state)
            
            avg_confidence = state.get("average_confidence", 1.0)
            
            # Determine what should happen next (but don't auto-execute)
            if avg_confidence < self.CONFIDENCE_THRESHOLD:
                next_endpoint = "/patient/followup_questions"
                needs_user_input = "followup_questions"
                next_step_description = "Follow-up questions needed to improve accuracy"
            elif state.get("image_required", False):
                next_endpoint = "/patient/image_analysis"
                needs_user_input = "image_upload"
                next_step_description = "Image analysis required"
            else:
                next_endpoint = "/patient/overall_analysis"
                needs_user_input = None
                next_step_description = "Ready for comprehensive analysis"
            
            logger.info(f"✅ Textual analysis complete. Confidence: {avg_confidence:.2f}, Next: {next_step_description}")
            
            return {
                "current_stage": "textual_analysis_complete",
                "next_endpoint": next_endpoint,
                "needs_user_input": needs_user_input,
                "next_step_description": next_step_description,
                "workflow_complete": False,
                "show_next_button": True,  # Always show next button for user control
                "confidence_score": avg_confidence,
                "image_required": state.get("image_required", False)
            }
        
        # For now, only handle textual analysis
        return {
            "current_stage": state.get("current_workflow_stage", "unknown"),
            "next_endpoint": None,
            "needs_user_input": None,
            "workflow_complete": False,
            "show_next_button": False
        }

# Global instance
workflow_state_manager = WorkflowStateManager()