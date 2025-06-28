from adapters.local_model_adapter import LocalModelAdapter
from typing import Dict, Any, Optional, List
import re

class OverallAnalysisNode:
    def __init__(self, adapter: LocalModelAdapter):
        self.adapter = adapter
    
    async def __call__(self, state):
        print("🎯 OVERALL ANALYSIS NODE CALLED!")
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
            
            # **INSTANCE 1: Textual Analysis Only**
            if workflow_path == ["textual_only"]:
                enhanced_analysis = await self._analyze_textual_only(state)
                analysis_type = "textual_only"
            
            # **INSTANCE 2: Textual -> Image Analysis**
            elif workflow_path == ["textual_to_image"]:
                enhanced_analysis = await self._analyze_textual_and_image(state)
                analysis_type = "textual_and_image"
            
            # **INSTANCE 3: Textual -> Follow-up Only**
            elif "followup_only" in workflow_path:
                enhanced_analysis = await self._analyze_textual_and_followup(state)
                analysis_type = "textual_and_followup"
            
            # **INSTANCE 4: Textual -> Follow-up -> Image**
            elif "followup_to_image" in workflow_path:
                enhanced_analysis = await self._analyze_comprehensive(state)
                analysis_type = "comprehensive_analysis"
            
            else:
                # Fallback for unknown paths
                enhanced_analysis = await self._analyze_fallback(state)
                analysis_type = "fallback"
            
           # Store simplified overall analysis results
            state["overall_analysis"] = {
                "final_diagnosis": enhanced_analysis["diagnosis"],
                "final_confidence": enhanced_analysis["confidence"],
                "final_severity": enhanced_analysis["severity"],
                "reasoning": enhanced_analysis["reasoning"],
                "specialist_recommendation": enhanced_analysis["specialist_recommendation"]
            }
            
            print(f"✅ Overall analysis complete: {analysis_type}")
            print(f"🎯 Specialist recommended: {enhanced_analysis['specialist_recommendation']}")
            
        except Exception as e:
            print(f"❌ Overall analysis failed: {e}")
            state["overall_analysis"] = self._create_fallback_analysis(state, str(e))
        
        return state
    
    # **INSTANCE 1: Textual Only Analysis**
    async def _analyze_textual_only(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """High confidence textual analysis - enhance with reasoning and severity"""
        
        userInput_symptoms = state.get("userInput_symptoms", "")
        textual_analysis = state.get("textual_analysis", [])
        
        if not textual_analysis:
            raise ValueError("No textual analysis available")
        
        primary_diagnosis = textual_analysis[0]  # Highest confidence diagnosis
        
        # Generate enhanced analysis with reasoning and severity
        assessment_text = await self.adapter.generate_enhanced_textual_analysis(
            symptoms=userInput_symptoms,
            diagnosis=primary_diagnosis.get("text_diagnosis", "Unknown"),
            confidence=primary_diagnosis.get("diagnosis_confidence", 0.0)
        )
        
        return self._parse_enhanced_analysis(assessment_text, primary_diagnosis, "textual_only")
    
    # **INSTANCE 2: Textual + Image Analysis**
    async def _analyze_textual_and_image(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Combine textual and image analysis"""
        
        userInput_skin_symptoms = state.get("userInput_skin_symptoms", "")
        skin_lesion_analysis = state.get("skin_lesion_analysis", {})
        
        if not skin_lesion_analysis.get("image_diagnosis"):
            raise ValueError("No image analysis available")
        
        # Generate combined analysis
        assessment_text = await self.adapter.generate_combined_analysis(
            skin_symptoms=userInput_skin_symptoms,
            image_diagnosis=skin_lesion_analysis.get("image_diagnosis", "Unknown"),
            image_confidence=skin_lesion_analysis.get("confidence_score", {})
        )
        
        return self._parse_enhanced_analysis(assessment_text, skin_lesion_analysis, "textual_and_image")
    
    # **INSTANCE 3: Textual + Follow-up Analysis**
    async def _analyze_textual_and_followup(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze textual diagnosis enhanced with follow-up responses"""
        
        userInput_symptoms = state.get("userInput_symptoms", "")
        followup_qna = state.get("followup_qna", {})
        followup_diagnosis = state.get("followup_diagnosis", [])
        
        if not followup_diagnosis:
            raise ValueError("No follow-up diagnosis available")
        
        enhanced_diagnosis = followup_diagnosis[0]  # Best follow-up diagnosis
        
        # Generate enhanced analysis with follow-up context
        assessment_text = await self.adapter.generate_followup_enhanced_analysis(
            original_symptoms=userInput_symptoms,
            followup_responses=followup_qna,
            enhanced_diagnosis=enhanced_diagnosis.get("text_diagnosis", "Unknown"),
            enhanced_confidence=enhanced_diagnosis.get("diagnosis_confidence", 0.0)
        )
        
        return self._parse_enhanced_analysis(assessment_text, enhanced_diagnosis, "textual_and_followup")
    
    # **INSTANCE 4: Comprehensive Analysis (All Data)**
    async def _analyze_comprehensive(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Full comprehensive analysis with all available data"""
        
        userInput_symptoms = state.get("userInput_symptoms", "")
        followup_qna = state.get("followup_qna", {})
        followup_diagnosis = state.get("followup_diagnosis", [])
        userInput_skin_symptoms = state.get("userInput_skin_symptoms", "")
        skin_lesion_analysis = state.get("skin_lesion_analysis", {})
        
        # Generate comprehensive analysis with all data
        assessment_text = await self.adapter.generate_comprehensive_analysis(
            original_symptoms=userInput_symptoms,
            followup_responses=followup_qna,
            followup_diagnosis=followup_diagnosis[0] if followup_diagnosis else {},
            skin_symptoms=userInput_skin_symptoms,
            image_analysis=skin_lesion_analysis
        )
        
        # Use the most recent diagnosis (follow-up takes precedence)
        primary_analysis = followup_diagnosis[0] if followup_diagnosis else {}
        
        return self._parse_enhanced_analysis(assessment_text, primary_analysis, "comprehensive_analysis")
    
    def _parse_enhanced_analysis(self, assessment_text: str, primary_analysis: Dict, analysis_type: str) -> Dict[str, Any]:
        """Parse LLM assessment into simplified structured data"""
        
        # Extract final diagnosis
        diagnosis_match = re.search(r"final\s+diagnosis[:\s]+([^\n]+)", assessment_text, re.IGNORECASE)
        final_diagnosis = diagnosis_match.group(1).strip() if diagnosis_match else primary_analysis.get("text_diagnosis", "Unknown")
        
        # Extract confidence
        confidence_match = re.search(r"confidence[:\s]+([0-9]*\.?[0-9]+)", assessment_text, re.IGNORECASE)
        if confidence_match:
            final_confidence = float(confidence_match.group(1))
            if final_confidence > 1:
                final_confidence = final_confidence / 100
        else:
            # Apply confidence boost based on analysis type
            base_confidence = primary_analysis.get("diagnosis_confidence", 0.0)
            confidence_boosts = {
                "comprehensive_analysis": 0.15,
                "textual_and_image": 0.12,
                "textual_and_followup": 0.08,
                "textual_only": 0.05
            }
            boost = confidence_boosts.get(analysis_type, 0.05)
            final_confidence = min(1.0, base_confidence + boost)
        
        # Extract severity
        severity_match = re.search(r"severity[:\s]+(\w+)", assessment_text, re.IGNORECASE)
        final_severity = severity_match.group(1).strip().lower() if severity_match else "moderate"
        
        # Extract reasoning
        reasoning_match = re.search(r"reasoning[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\nSpecialist|$)", assessment_text, re.IGNORECASE | re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "Enhanced analysis performed based on available data"
        
        # Extract specialist recommendation
        specialist_match = re.search(r"specialist[:\s]+(\w+)", assessment_text, re.IGNORECASE)
        specialist_recommendation = specialist_match.group(1).strip().lower() if specialist_match else self._determine_default_specialist(final_diagnosis)
        
        return {
            "diagnosis": final_diagnosis,
            "confidence": final_confidence,
            "severity": final_severity,
            "reasoning": reasoning,
            "specialist_recommendation": specialist_recommendation
        }
    
    def _determine_default_specialist(self, diagnosis: str) -> str:
        """Determine default specialist based on diagnosis keywords"""
        diagnosis_lower = diagnosis.lower()
        
        specialist_mapping = {
            "skin": "dermatologist",
            "mole": "dermatologist",
            "lesion": "dermatologist",
            "rash": "dermatologist",
            "melanoma": "dermatologist",
            "heart": "cardiologist",
            "chest": "cardiologist",
            "cardiac": "cardiologist",
            "headache": "neurologist",
            "migraine": "neurologist",
            "neurological": "neurologist",
            "cancer": "oncologist",
            "tumor": "oncologist",
            "stomach": "gastroenterologist",
            "digestive": "gastroenterologist",
            "lung": "pulmonologist",
            "breathing": "pulmonologist",
            "diabetes": "endocrinologist",
            "thyroid": "endocrinologist",
            "joint": "rheumatologist",
            "arthritis": "rheumatologist",
            "bone": "orthopedist",
            "fracture": "orthopedist",
            "mental": "psychiatrist",
            "depression": "psychiatrist",
            "anxiety": "psychiatrist",
            "urinary": "urologist",
            "kidney": "urologist",
            "gynecology": "gynecologist",
            "emergency": "emergency_physician"
        }
        
        for keyword, specialist in specialist_mapping.items():
            if keyword in diagnosis_lower:
                return specialist
        
        return "general_practitioner"  # Default fallback
    
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
        
        diagnosis = primary.get("text_diagnosis", "Unknown")
        
        return {
            "final_diagnosis": diagnosis,
            "final_confidence": primary.get("diagnosis_confidence", 0.0),
            "final_severity": "unknown",
            "reasoning": f"Analysis incomplete due to technical error: {error_msg}",
            "specialist_recommendation": self._determine_default_specialist(diagnosis)
        }
    
    def _extract_recommendation_guidance(self, assessment_text: str) -> str:
        """Extract guidance for healthcare recommendations"""
        urgency_keywords = ["urgent", "immediate", "emergency", "critical"]
        specialist_keywords = ["specialist", "referral", "dermatologist", "cardiologist"]
        selfcare_keywords = ["self-care", "home treatment", "conservative"]
        
        text_lower = assessment_text.lower()
        
        if any(keyword in text_lower for keyword in urgency_keywords):
            return "urgent_care_recommended"
        elif any(keyword in text_lower for keyword in specialist_keywords):
            return "specialist_consultation_recommended"
        elif any(keyword in text_lower for keyword in selfcare_keywords):
            return "self_care_appropriate"
        else:
            return "standard_care_recommended"
    
    def _extract_key_findings(self, assessment_text: str) -> List[str]:
        """Extract key findings from assessment"""
        findings = []
        lines = assessment_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or 
                        (len(line) > 0 and line[0].isdigit() and '.' in line[:3])):
                clean_finding = line.lstrip('-•0123456789. ').strip()
                if len(clean_finding) > 15:
                    findings.append(clean_finding)
        
        return findings[:5]  # Limit to 5 key findings