from adapters.local_model_adapter import LocalModelAdapter
from typing import Dict, Any, Optional, List
import re

class OverallAnalysisNode:
    def __init__(self, adapter: LocalModelAdapter):
        self.adapter = adapter
    
    async def __call__(self, state):
        print("OVERALL ANALYSIS NODE CALLED!")
        state["current_workflow_stage"] = "performing_overall_analysis"
        
        state = await self.perform_overall_analysis(state)
        
        state["current_workflow_stage"] = "overall_analysis_complete"
        return state
    
    async def perform_overall_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis based on workflow path.
        Optimized for each of the 4 workflow instances.
        """
        
        try:
            workflow_path = state.get("workflow_path", [])
            
            # Get the best available diagnosis
            followup_diagnosis = state.get("followup_diagnosis", [])
            textual_analysis = state.get("textual_analysis", [])
            
            if followup_diagnosis:
                primary_diagnosis = followup_diagnosis[0]
            elif textual_analysis:
                primary_diagnosis = textual_analysis[0]
            else:
                raise ValueError("No diagnosis available")
            
            diagnosis_text = primary_diagnosis.get("text_diagnosis", "Unknown")
            diagnosis_confidence = primary_diagnosis.get("diagnosis_confidence", 0.0)
            
            # Handle None confidence values (from skin cancer screening)
            if diagnosis_confidence is None:
                print("⚠️ Warning: diagnosis_confidence is None, setting to 0.0")
                diagnosis_confidence = 0.0
            
            # Create safe primary diagnosis dict
            safe_primary_diagnosis = {
                "text_diagnosis": diagnosis_text,
                "diagnosis_confidence": float(diagnosis_confidence)
            }
            
            ##Determine analysis type and run appropriate method
            if workflow_path == ["textual_only"]:
                print("📊 Running Instance 1: Textual Only Analysis")
                enhanced_analysis = await self._analyze_textual_only(state)
            elif workflow_path == ['textual_to_skin_screening']:
                print("📊 Running Instance 2: Textual + Image Analysis")
                enhanced_analysis = await self._analyze_textual_and_image(state)
            elif "followup_only" in workflow_path or "skin_to_standard_followup" in workflow_path:
                print("📊 Running Instance 3: Textual + Follow-up Analysis")
                enhanced_analysis = await self._analyze_textual_and_followup(state)
            # elif "followup_to_image" in workflow_path:
            #     print("📊 Running Instance 4: Comprehensive Analysis (All Data)")
            #     enhanced_analysis = await self._analyze_all(state)
            else:
                print("⚠️ Running Fallback Analysis")
                enhanced_analysis = await self._analyze_fallback(state)
            
           # Store simplified overall analysis results
            state["overall_analysis"] = {
                "final_diagnosis": safe_primary_diagnosis.get("text_diagnosis", "Unknown"),
                "final_confidence": safe_primary_diagnosis.get("diagnosis_confidence", 0.0),
                "final_severity": enhanced_analysis["severity"],
                "user_explanation": enhanced_analysis.get("user_explanation", "Enhanced analysis performed based on available data"),
                "clinical_reasoning": enhanced_analysis.get("clinical_reasoning", "Diagnosis determined through systematic analysis of symptoms and clinical indicators"),
                "specialist_recommendation": enhanced_analysis["specialist_recommendation"]
            }
            
        except Exception as e:
            print(f"❌ Overall analysis failed: {e}")
            state["overall_analysis"] = self._create_fallback_analysis(state, str(e))
        
        return state
    
    #INSTANCE 1: Textual Only Analysis**
    async def _analyze_textual_only(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Textual-only analysis with Q4 model"""
        
        userInput_symptoms = state.get("userInput_symptoms", "")
        textual_analysis = state.get("textual_analysis", [])
        
        if not textual_analysis:
            raise ValueError("No textual analysis available")
        
        primary_diagnosis = textual_analysis[0]  # Highest confidence diagnosis
        
        # Generate enhanced analysis with reasoning and severity
        assessment_text = await self.adapter.generate_overall_instance1(
            symptoms=userInput_symptoms,
            diagnosis=primary_diagnosis.get("text_diagnosis", "Unknown"),
            confidence=primary_diagnosis.get("diagnosis_confidence", 0.0)
        )
        
        return self._parse_enhanced_analysis(assessment_text, primary_diagnosis)
    
    #INSTANCE 2: Textual + Image Analysis**
    async def _analyze_textual_and_image(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Combine textual and image analysis"""
        followup_qna = state.get("followup_qna_overall", "") #includes the original symptom and followup qna
        #Followup_diagnosis not needed as its a placeholder to inform user about suspicious skin lesion
        skin_lesion_analysis = state.get("skin_lesion_analysis", {})
        
        if not skin_lesion_analysis.get("image_diagnosis"):
            raise ValueError("No image analysis available")
        
        # Generate combined analysis
        assessment_text = await self.adapter.generate_overall_instance2(
            followup_qna=followup_qna,
            image_diagnosis=skin_lesion_analysis.get("image_diagnosis", "Unknown"),
            image_confidence=skin_lesion_analysis.get("confidence_score", {})
        )
        
        ##create proper primary diagnosis from image analysis
        image_confidence_scores = skin_lesion_analysis.get("confidence_score", {})
        max_image_confidence = max(image_confidence_scores.values()) / 100 if image_confidence_scores else 0.0        
        
        primary_analysis = {
            "text_diagnosis": skin_lesion_analysis.get("image_diagnosis", "Unknown"),
            "diagnosis_confidence": max_image_confidence
        }
        
        return self._parse_enhanced_analysis(assessment_text, primary_analysis)
    
    #INSTANCE 3: Textual + Follow-up Analysis**
    async def _analyze_textual_and_followup(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze textual diagnosis enhanced with follow-up responses"""
        
        followup_qna = state.get("followup_qna_overall", {}) #includes the original symptom and followup qna
        followup_diagnosis = state.get("followup_diagnosis", [])
        
        if not followup_diagnosis:
            raise ValueError("No follow-up diagnosis available")
        
        enhanced_diagnosis = followup_diagnosis[0]  # Best follow-up diagnosis
    
        
        # Generate enhanced analysis with follow-up context
        assessment_text = await self.adapter.generate_overall_instance3(
            followup_qna=followup_qna,
            enhanced_diagnosis=enhanced_diagnosis.get("text_diagnosis", "Unknown"),
            enhanced_confidence=enhanced_diagnosis.get("diagnosis_confidence", 0.0)
        )
        
        return self._parse_enhanced_analysis(assessment_text, enhanced_diagnosis)
    
    # # **INSTANCE 4: Comprehensive Analysis (All Data)**
    # async def _analyze_all(self, state: dict[str, Any]) -> dict[str, Any]:
    #     """Full comprehensive analysis with all available data"""
        
    #     followup_qna = state.get("followup_qna_overall", {}) #includes the original symptom and followup qna
    #     followup_diagnosis = state.get("followup_diagnosis", [])
    #     userInput_skin_symptoms = state.get("userInput_skin_symptoms", "")
    #     skin_lesion_analysis = state.get("skin_lesion_analysis", {})
        
    #     # Generate comprehensive analysis with all data
    #     assessment_text = await self.adapter.generate_overall_instance4(
    #         followup_overall=followup_qna,
    #         followup_diagnosis=followup_diagnosis[0] if followup_diagnosis else {},
    #         skin_symptoms=userInput_skin_symptoms,
    #         image_analysis=skin_lesion_analysis
    #     )
        
        # # Use the most recent diagnosis (follow-up takes precedence)
        # primary_analysis = followup_diagnosis[0] if followup_diagnosis else {}
        # return self._parse_enhanced_analysis(assessment_text, primary_analysis)
    
    def _parse_enhanced_analysis(self, assessment_text: str, primary_analysis: dict) -> dict[str, Any]:
        """Parse LLM assessment into simplified structured data"""
        
        print(f"🔍 Raw assessment text:\n{assessment_text}")
        #Use diagnosis and confidence from primary analysis
        forced_diagnosis = primary_analysis.get("text_diagnosis", "Unknown")
        forced_confidence = primary_analysis.get("diagnosis_confidence", 0.0)
        
        # Extract severity
        severity_match = re.search(r"(?:^|\n)\s*-?\s*Severity:\s*(\w+)", assessment_text, re.IGNORECASE)
        final_severity = severity_match.group(1).strip().lower() if severity_match else "moderate"
        
        #User Explanation extraction
        user_explanation_patterns = [
            r"(?:^|\n)\s*-?\s*User Explanation:\s*(.+?)(?=\n\s*-?\s*Clinical Reasoning|\n\s*-?\s*Specialist|$)",
            r"User Explanation:\s*(.+?)(?=Clinical Reasoning|Specialist|$)",
        ]
        
        user_explanation = None
        for pattern in user_explanation_patterns:
            explanation_match = re.search(pattern, assessment_text, re.IGNORECASE | re.DOTALL)
            if explanation_match:
                user_explanation = explanation_match.group(1).strip()
                # Clean up formatting
                user_explanation = re.sub(r'\n+', ' ', user_explanation)
                user_explanation = re.sub(r'\s+', ' ', user_explanation)
                if len(user_explanation) > 10:  # Must be meaningful content
                    break
                else:
                    user_explanation = None
        
        #Clinical Reasoning extraction
        clinical_reasoning_patterns = [
            r"(?:^|\n)\s*-?\s*Clinical Reasoning:\s*(.+?)(?=\n\s*-?\s*Specialist|$)",
            r"Clinical Reasoning:\s*(.+?)(?=Specialist|$)",
        ]
        
        clinical_reasoning = None
        for pattern in clinical_reasoning_patterns:
            reasoning_match = re.search(pattern, assessment_text, re.IGNORECASE | re.DOTALL)
            if reasoning_match:
                clinical_reasoning = reasoning_match.group(1).strip()
                # Clean up formatting
                clinical_reasoning = re.sub(r'\n+', ' ', clinical_reasoning)
                clinical_reasoning = re.sub(r'\s+', ' ', clinical_reasoning)
                if len(clinical_reasoning) > 20:  # Must be meaningful content
                    break
                else:
                    clinical_reasoning = None
        
        if not clinical_reasoning:
            clinical_reasoning = f"The diagnosis {forced_diagnosis} was determined based on systematic analysis of the provided symptoms and clinical evidence. The confidence level reflects diagnostic certainty based on available data."
        
        # Extract specialist
        specialist_match = re.search(r"(?:^|\n)\s*-?\s*Specialist:\s*([^\n]+)", assessment_text, re.IGNORECASE)
        if specialist_match:
            specialist = specialist_match.group(1).strip().lower()
            #Cleanup - remove underscores and special characters but keep forward slashes
            specialist = re.sub(r'[^a-z\s/]', '', specialist)
            # Replace "or" with " / "
            specialist = re.sub(r'\s+or\s+', ' / ', specialist)
            specialist_recommendation = specialist if specialist else "general_practitioner"
        else:
            specialist_recommendation = "general_practitioner"
        
        return {
            "diagnosis": forced_diagnosis,
            "confidence": forced_confidence,
            "severity": final_severity,
            "user_explanation": user_explanation,
            "clinical_reasoning": clinical_reasoning,
            "specialist_recommendation": specialist_recommendation
        }
        
    async def _analyze_fallback(self, state: dict[str, Any]) -> dict[str, Any]:
        """Fallback analysis when other methods fail"""
        
        # Try to get any available diagnosis data
        textual_analysis = state.get("textual_analysis", [])
        followup_diagnosis = state.get("followup_diagnosis", [])
        
        # Use the best available diagnosis
        if followup_diagnosis:
            primary = followup_diagnosis[0]
        elif textual_analysis:
            primary = textual_analysis[0]
        else:
            primary = {"text_diagnosis": "Unknown condition", "diagnosis_confidence": 0.0}
        
        return {
            "diagnosis": primary.get("text_diagnosis", "Unknown condition"),
            "confidence": primary.get("diagnosis_confidence", 0.0),
            "severity": "moderate",
            "reasoning": "Fallback analysis - comprehensive analysis could not be completed",
            "specialist_recommendation": "general_practitioner"
        }
    
    def _create_fallback_analysis(self, state: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Create fallback analysis for error cases"""
        
        # Try to get any available diagnosis
        textual_analysis = state.get("textual_analysis", [])
        followup_diagnosis = state.get("followup_diagnosis", [])
        
        if followup_diagnosis:
            primary = followup_diagnosis[0]
        elif textual_analysis:
            primary = textual_analysis[0]
        else:
            primary = {"text_diagnosis": "Unknown", "diagnosis_confidence": 0.0}
        
        return {
            "final_diagnosis": primary.get("text_diagnosis", "Unknown"),
            "final_confidence": primary.get("diagnosis_confidence", 0.0),
            "final_severity": "unknown",
            "user_explanation": f"We've analyzed your symptoms but encountered a technical issue. Please consult with a healthcare professional for proper evaluation.",
            "clinical_reasoning": f"Analysis incomplete due to technical error: {error_msg}. Diagnosis based on preliminary symptom assessment.",
            "specialist_recommendation": "general_practitioner"
        }