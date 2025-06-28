from typing_extensions import TypedDict, Literal
from typing import Optional, List, Dict, Union, Any

WorkflowPathType = Literal[
    "textual_only",           # Instance 1: Direct textual analysis
    "textual_to_image",       # Instance 2: Textual -> Image
    "textual_to_followup",    # Instance 3 & 4: Textual -> Follow-up (start)
    "followup_only",          # Instance 3: Follow-up -> Overall analysis
    "followup_to_image"       # Instance 4: Follow-up -> Image -> Overall analysis
]

#Minimal schema on purpose during early stages to enable lazy loading for performance(without reasoning/severity)
class TextualSymptomAnalysisResult(TypedDict):
    text_diagnosis: str
    diagnosis_confidence: float
    
class SkinLesionImageAnalysisResult(TypedDict):
    image_diagnosis: Optional[str]
    confidence_score: Optional[Union[dict[str, float]]]
    
class OverallAnalysisResult(TypedDict):
    final_diagnosis: str
    final_confidence: float
    final_severity: str                     # mild/moderate/severe/critical/emergency
    reasoning: str                          # Medical justification
    specialist_recommendation: str  # For Google Maps integration
    
class HealthcareRecommendationResult(TypedDict):
    recommendation_type: str              
    self_care_advice: Optional[List[str]]
    specialist_type: Optional[str] 
    nearby_facilities: Optional[List[Dict[str, Any]]]  
    facility_search_radius: Optional[str]  
    emergency_contacts: Optional[List[Dict[str, str]]]  
    appointment_urgency: Optional[str]     
    insurance_guidance: Optional[List[str]] 
    rag_evidence: Optional[List[str]]
    telemedicine_options: Optional[List[Dict[str, Any]]] 
    cost_estimates: Optional[Dict[str, str]]

class AgentState(TypedDict, total=False):
    session_id: str #Unique ID for session
    current_workflow_stage: Optional[str] # Current stage of the workflow(e.g., "textual_analysis", "skin_lesion_analysis") for guiding frontend 
    workflow_path: Optional[List[WorkflowPathType]] # Tracks the path taken through the workflow for debugging and analysis
    image_required: bool
    latest_user_message: str # Raw user input for current step
    image_input: Optional[str] # Stores uploaded image in the form of file path, base64, or raw bytes
    user_location: Optional[Dict[str, float]] # User location for Google Maps API
    
    #STAGE 1: Textual Symptom Analysis 
    userInput_symptoms: Optional[str] #Used to store user input of their symptoms to be used as a value with textual_analysis for overall analysis
    textual_analysis: Optional[List[TextualSymptomAnalysisResult]] 
    average_confidence: Optional[float] # Average confidence score across all textual analyses

    #Follow-up stage (if required based on confidence)
    requires_user_input: Optional[bool] # Indicates if user input is required for follow-up questions
    followup_questions: Optional[List[str]]
    followup_response: Optional[Dict[str, str]] # Follow-up responses from user
    followup_qna: Optional[Dict[str, str]] # Combined Q&A pairs from follow-up interaction
    followup_diagnosis: Optional[List[TextualSymptomAnalysisResult]]

    #STAGE 2: Skin LesionImage Analysis (Optional)
    userInput_skin_symptoms: Optional[str] #Used to store user input of their skin symptoms to be used as a value with skin_lesion_analysis for overall analysis (if image_required is True)
    skin_lesion_analysis: Optional[SkinLesionImageAnalysisResult] 
    
    #STAGE 3: Overall Analysis
    overall_analysis: Optional[OverallAnalysisResult]
    
    #STAGE 4: Healthcare Treatment Recommendation
    healthcare_recommendation: Optional[HealthcareRecommendationResult] # Final recommendation based on analysis
    
    #FINAL STAGE: Medical Report Generation
    medical_report: Optional[str] #Generated comprehensive medical report