from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import Optional, Dict
import uuid
import base64
from datetime import datetime

import os
from nodes import LLMDiagnosisNode, ImageClassificationNode, FollowUpInteractionNode, OverallAnalysisNode, HealthcareRecommendationNode, MedicalReportNode 
from schemas.medical_schemas import AgentState
from managers.workflow_state_manager import WorkflowStateManager
from managers.websocket_manager import ConnectionManager
from managers.workflow_state_manager import workflow_state_manager
from managers.model_manager import model_manager

# Create router
diagnosis_router = APIRouter()

# Initialize workflow state manager
workflow_state_manager = WorkflowStateManager()

# Create connection manager instance (shared with main.py)
manager = ConnectionManager()

#Global node instances
llm_diagnosis_node: Optional[LLMDiagnosisNode] = None
followup_interaction_node: Optional[FollowUpInteractionNode] = None
image_classification_node: Optional[ImageClassificationNode] = None
overall_analysis_node: Optional[OverallAnalysisNode] = None
healthcare_recommendation_node: Optional[HealthcareRecommendationNode] = None
medical_report_node: Optional[MedicalReportNode] = None

print("✅ All nodes initialized for API routes!")

session_states: Dict[str, AgentState] = {}

def get_or_create_session_state(session_id: str, initial_state: Optional[AgentState] = None) -> AgentState:
    """Get existing session state or create new one"""
    if session_id not in session_states:
        if initial_state:
            session_states[session_id] = initial_state
        else:
            session_states[session_id] = AgentState(
                session_id=session_id,
                latest_user_message="",
                image_required=False
            )
    return session_states[session_id]

def update_session_state(session_id: str, updated_state: AgentState) -> None:
    """Update session state in storage"""
    session_states[session_id] = updated_state
    
def ensure_nodes_initialized():
    """Ensure all nodes are initialized with loaded models"""
    global llm_diagnosis_node, followup_interaction_node, image_classification_node
    global overall_analysis_node, healthcare_recommendation_node, medical_report_node
    
    if not model_manager.is_loaded():
        raise HTTPException(status_code=503, detail="Models not loaded yet. Please wait for startup to complete.")
    
    # Initialize nodes if not already done
    if llm_diagnosis_node is None:
        local_adapter = model_manager.get_local_adapter()
        efficientnet_adapter = model_manager.get_efficientnet_adapter()
        
        if local_adapter is None:
            raise HTTPException(status_code=503, detail="LLM model not available")
        
        llm_diagnosis_node = LLMDiagnosisNode(adapter=local_adapter)
        followup_interaction_node = FollowUpInteractionNode(adapter=local_adapter)
        overall_analysis_node = OverallAnalysisNode(adapter=local_adapter)
        healthcare_recommendation_node = HealthcareRecommendationNode(
            adapter=local_adapter,
            google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY")
        )
        medical_report_node = MedicalReportNode(adapter=local_adapter)
        
        if efficientnet_adapter:
            image_classification_node = ImageClassificationNode(adapter=efficientnet_adapter)
        
        print("✅ All nodes initialized with shared model adapters!")

# ✅ NODE 1: Textual Analysis Endpoint
@diagnosis_router.post("/patient/textual_analysis")
async def run_textual_analysis(
    user_symptoms: str = Form(..., description="Patient symptoms"),
    session_id: Optional[str] = Form(None, description="Session ID"),
):
    """Run LLM textual analysis on symptoms"""
    
    # Ensure nodes are initialized with loaded models
    ensure_nodes_initialized()
    
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    try:
        #Create or get session state
        state = get_or_create_session_state(session_id, AgentState(
            session_id=session_id,
            latest_user_message=user_symptoms,
            userInput_symptoms=user_symptoms,
            image_required=False,
            current_workflow_stage="initializing"  # Start with initializing
        ))
                
        # Send progress update
        await manager.send_message(session_id, {
            "type": "node_started",
            "node": "textual_analysis",
            "message": "Analyzing symptoms with AI...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the LLM diagnosis node
        result = await llm_diagnosis_node(state)
        
        #workflow state manager to set completion stage and determine next step
        workflow_info = workflow_state_manager.update_workflow_stage_and_determine_next(
            result, "textual_analysis"
        )

        print(f"🔍 After WorkflowStateManager - stage: {result.get('current_workflow_stage')}")
        print(f"📊 Workflow info: {workflow_info}")
        
        update_session_state(session_id, result)

        # Send completion update
        await manager.send_message(session_id, {
            "type": "node_completed", 
            "node": "textual_analysis",
            "result": result,
            "workflow_info": workflow_info,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result,
            "workflow_info": workflow_info #Frontend will use this to determine next step
        }
        
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "node_error",
            "node": "textual_analysis", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

# ✅ NODE 2: Follow-up Questions Endpoint
@diagnosis_router.post("/patient/followup_questions")
async def run_followup_questions(
    session_id: str = Form(..., description="Session ID"),
    previous_state: str = Form(..., description="JSON of previous AgentState"),
    followup_responses: Optional[str] = Form(None, description="JSON of user responses")
):
    """Generate follow-up questions OR process responses"""
    
    # Ensure nodes are initialized with loaded models
    ensure_nodes_initialized()
    
    try:
        import json
        state = json.loads(previous_state)
        
        # Add follow-up responses if provided
        if followup_responses:
            state["followup_response"] = json.loads(followup_responses)
            state["requires_user_input"] = False
        
        await manager.send_message(session_id, {
            "type": "node_started",
            "node": "followup_questions",
            "message": "Processing follow-up interaction...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the follow-up interaction node
        result = await followup_interaction_node(state)
        
        await manager.send_message(session_id, {
            "type": "node_completed",
            "node": "followup_questions", 
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result,
        }
        
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "node_error",
            "node": "followup_questions",
            "error": str(e), 
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

# ✅ NODE 3: Image Analysis Endpoint  
@diagnosis_router.post("/patient/image_analysis")
async def run_image_analysis(
    session_id: str = Form(...),
    previous_state: str = Form(..., description="JSON of previous AgentState"),
    image_file: Optional[UploadFile] = File(None, description="Medical image")
):
    """Run image classification analysis"""
    
    # Ensure nodes are initialized with loaded models
    ensure_nodes_initialized()
    
    try:
        import json
        state = json.loads(previous_state)
        
        # Handle new image upload
        if image_file:
            image_bytes = await image_file.read()
            state["image_input"] = base64.b64encode(image_bytes).decode('utf-8')
        
        await manager.send_message(session_id, {
            "type": "node_started",
            "node": "image_analysis",
            "message": "Analyzing medical image...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the image classification node
        result = await image_classification_node(state)
        
        await manager.send_message(session_id, {
            "type": "node_completed",
            "node": "image_analysis",
            "result": result, 
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result,
        }
        
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "node_error",
            "node": "image_analysis",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

# ✅ NODE 4: Overall Analysis Endpoint
@diagnosis_router.post("/patient/overall_analysis")
async def run_overall_analysis(
    session_id: str = Form(...),
    previous_state: str = Form(..., description="JSON of previous AgentState")
):
    """Run comprehensive overall analysis"""
    
    # Ensure nodes are initialized with loaded models
    ensure_nodes_initialized()
    
    try:
        import json
        state = json.loads(previous_state)
        
        await manager.send_message(session_id, {
            "type": "node_started",
            "node": "overall_analysis",
            "message": "Performing comprehensive analysis...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the overall analysis node
        result = await overall_analysis_node(state)
        
        await manager.send_message(session_id, {
            "type": "node_completed",
            "node": "overall_analysis",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result,
        }
        
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "node_error",
            "node": "overall_analysis",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

# ✅ NODE 5: Healthcare Recommendations Endpoint
@diagnosis_router.post("/patient/healthcare_recommendations")
async def run_healthcare_recommendations(
    session_id: str = Form(...),
    previous_state: str = Form(..., description="JSON of previous AgentState")
):
    """Generate healthcare recommendations"""
    
    # Ensure nodes are initialized with loaded models
    ensure_nodes_initialized()
    
    try:
        import json
        state = json.loads(previous_state)
        
        await manager.send_message(session_id, {
            "type": "node_started",
            "node": "healthcare_recommendations",
            "message": "Finding healthcare recommendations...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the healthcare recommendation node
        result = await healthcare_recommendation_node(state)
        
        await manager.send_message(session_id, {
            "type": "node_completed",
            "node": "healthcare_recommendations",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result,
        }
        
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "node_error",
            "node": "healthcare_recommendations",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

# ✅ NODE 6: Medical Report Endpoint
@diagnosis_router.post("/patient/medical_report")
async def run_medical_report(
    session_id: str = Form(...),
    previous_state: str = Form(..., description="JSON of previous AgentState")
):
    """Generate final medical report"""
    
    # Ensure nodes are initialized with loaded models
    ensure_nodes_initialized()
    
    try:
        import json
        state = json.loads(previous_state)
        
        await manager.send_message(session_id, {
            "type": "node_started",
            "node": "medical_report",
            "message": "Generating medical report...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the medical report node  
        result = await medical_report_node(state)
        
        await manager.send_message(session_id, {
            "type": "workflow_completed",
            "final_result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result,
            "next_recommended_endpoint": None  # Workflow complete
        }
        
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "node_error",
            "node": "medical_report",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))



@diagnosis_router.get("/debug/routes")
async def debug_routes():
    return {
        "message": "Routes are working!",
        "available_endpoints": [
            "/patient/textual_analysis",
            "/patient/followup_questions", 
            "/patient/image_analysis",
            "/patient/overall_analysis",
            "/patient/healthcare_recommendations",
            "/patient/medical_report",
            "/health"
        ]
    }

# Enhanced diagnostic endpoint with WebSocket integration
@diagnosis_router.post("/patient/diagnose_patient_realtime")
async def diagnose_patient_realtime(
    user_symptoms: str = Form(..., description="Symptoms provided by the patient"),
    session_id: Optional[str] = Form(None, description="Session ID for WebSocket connection"),
    user_lat: Optional[float] = Form(None, description="User latitude for location services"),
    user_lng: Optional[float] = Form(None, description="User longitude for location services"),
    image_file: Optional[UploadFile] = File(None, description="Medical image file")
):
    """Enhanced diagnosis with real-time WebSocket updates"""
    
    # Ensure nodes are initialized with loaded models
    ensure_nodes_initialized()
    
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    try:
        # Initialize workflow state
        initial_state = AgentState(
            session_id=session_id,
            latest_user_message=user_symptoms,
            userInput_symptoms=user_symptoms,
            workflow_path=[],
            image_required=False,
            user_location={"lat": user_lat, "lng": user_lng} if user_lat and user_lng else None,
            image_input=None
        )
        
        # Handle image upload
        if image_file:
            try:
                if not image_file.content_type.startswith('image/'):
                    raise HTTPException(status_code=400, detail="File must be an image")
                
                image_bytes = await image_file.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                initial_state["image_input"] = image_base64
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
            finally:
                await image_file.close()
        
        # Store session in connection manager
        manager.session_workflows[session_id] = {
            "status": "started",
            "current_stage": "initializing",
            "progress": 0,
            "started_at": datetime.now().isoformat()
        }
        
        # Send workflow started notification
        await manager.send_message(session_id, {
            "type": "workflow_started",
            "session_id": session_id,
            "initial_symptoms": user_symptoms,
            "timestamp": datetime.now().isoformat()
        })
        
        # Run workflow with real-time updates
        result = await run_workflow_with_updates(initial_state, session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result,
            "message": "Diagnosis completed successfully"
        }
        
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "workflow_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))



# Endpoint to submit follow-up responses
@diagnosis_router.post("/patient/submit_followup_responses")
async def submit_followup_responses(
    session_id: str = Form(..., description="Session ID"),
    responses: str = Form(..., description="JSON string of responses")
):
    """Submit follow-up question responses and continue workflow"""
    
    # Ensure nodes are initialized with loaded models
    ensure_nodes_initialized()
    
    try:
        import json
        responses_dict = json.loads(responses)
        
        # Get current workflow state
        if session_id not in manager.session_workflows:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await manager.send_message(session_id, {
            "type": "followup_responses_received",
            "responses": responses_dict,
            "message": "Continuing analysis with your responses...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Update workflow state with follow-up responses
        updated_state = AgentState(
            session_id=session_id,
            followup_response=responses_dict,
            requires_user_input=False,
            current_workflow_stage="processing_followup"
        )
        
        # Continue workflow from follow-up node
        result = await run_workflow_with_updates(updated_state, session_id)
        
        return {
            "success": True,
            "message": "Follow-up responses processed successfully",
            "result": result
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in responses")
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "followup_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@diagnosis_router.get("/health")
async def health_check():
    """System health check with WebSocket connection info"""
    return {
        "status": "healthy",
        "service": "AI Medical Diagnosis API", 
        "version": "2.0.0",
        "features": {
            "llm_analysis": True,
            "image_classification": True,
            "location_services": True,
            "medical_reporting": True,
            "realtime_websocket": True,
            "active_connections": len(manager.active_connections)
        },
        "websocket_endpoint": "/ws/{session_id}",
        "timestamp": datetime.now().isoformat()
    }

# Workflow execution with real-time updates
async def run_workflow_with_updates(state: AgentState, session_id: str):
    """Run the LangGraph workflow with real-time WebSocket updates"""
    
    workflow_stages = [
        ("llm_diagnosis", "Analyzing symptoms with AI", 20),
        ("followup_interaction", "Generating follow-up questions", 40), 
        ("image_analysis", "Processing medical images", 60),
        ("overall_analysis_step", "Comprehensive medical analysis", 80), 
        ("healthcare_recommendation_step", "Finding healthcare recommendations", 90),  
        ("generate_report", "Generating medical report", 100)
    ]
    current_progress = 0
    
    # Create a custom callback for workflow updates
    async def workflow_callback(node_name: str, node_result: dict):
        nonlocal current_progress
        
        # Find current stage info
        stage_info = next((s for s in workflow_stages if s[0] == node_name), None)
        if stage_info:
            stage_name, description, progress = stage_info
            current_progress = progress
            
            # Update session workflow data
            manager.session_workflows[session_id].update({
                "status": "running",
                "current_stage": stage_name,
                "stage_description": description,
                "progress": progress,
                "last_updated": datetime.now().isoformat()
            })
            
            # Send real-time update
            await manager.send_message(session_id, {
                "type": "workflow_progress",
                "stage": stage_name,
                "description": description,
                "progress": progress,
                "node_result": node_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Special handling for follow-up questions
            if node_name == "followup_interaction" and node_result.get("requires_user_input"):
                await manager.send_message(session_id, {
                    "type": "user_input_required",
                    "questions": node_result.get("followup_questions", []),
                    "message": "Please answer the following questions to improve diagnosis accuracy",
                    "timestamp": datetime.now().isoformat()
                })
    
    # Execute workflow with custom monitoring
    try:
        # Execute the workflow
        result = await execute_workflow_with_monitoring(state, workflow_callback)
        
        # Final completion message
        manager.session_workflows[session_id].update({
            "status": "completed",
            "progress": 100,
            "completed_at": datetime.now().isoformat()
        })
        
        await manager.send_message(session_id, {
            "type": "workflow_completed",
            "final_result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
        
    except Exception as e:
        manager.session_workflows[session_id].update({
            "status": "error",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })
        
        await manager.send_message(session_id, {
            "type": "workflow_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise e

async def execute_workflow_with_monitoring(state: AgentState, callback):
    """Execute the LangGraph workflow with monitoring callbacks"""
    
    # This is a wrapper around your existing patient_app workflow
    # We'll add monitoring by intercepting node execution
    
    from graphs.patient_workflow import patient_app
    
    # Execute the workflow
    result = await patient_app.ainvoke(state)
    
    return result

# Session management endpoints
@diagnosis_router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get current status of a diagnosis session"""
    if session_id not in manager.session_workflows:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "workflow_status": manager.session_workflows[session_id],
        "websocket_connected": session_id in manager.active_connections,
        "timestamp": datetime.now().isoformat()
    }

@diagnosis_router.delete("/session/{session_id}")
async def terminate_session(session_id: str):
    """Terminate a diagnosis session"""
    if session_id in manager.session_workflows:
        del manager.session_workflows[session_id]
    
    if session_id in manager.active_connections:
        await manager.send_message(session_id, {
            "type": "session_terminated",
            "message": "Session has been terminated",
            "timestamp": datetime.now().isoformat()
        })
        manager.disconnect(session_id)
    
    return {
        "success": True,
        "message": f"Session {session_id} terminated",
        "timestamp": datetime.now().isoformat()
    }

# System monitoring endpoints
@diagnosis_router.get("/admin/connections")
async def list_active_connections():
    """List all active WebSocket connections (admin endpoint)"""
    return {
        "active_connections": list(manager.active_connections.keys()),
        "active_workflows": list(manager.session_workflows.keys()),
        "total_connections": len(manager.active_connections),
        "total_workflows": len(manager.session_workflows),
        "timestamp": datetime.now().isoformat()
    }