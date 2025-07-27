from ray import state
from adapters.local_model_adapter import LocalModelAdapter
from typing import Dict, Any, List
import re

#responses contain both qna pairs, the parsing is used to combine initial user input and structured qna 
#for context later (followup_qna_overall)

class FollowUpInteractionNode:
    def __init__(self, adapter: LocalModelAdapter):
        self.adapter = adapter
        
    async def __call__(self, state):
        return await self.handle_followup_interaction(state)
    
    async def handle_followup_interaction(self, state: dict[str, Any]) -> dict[str, Any]:
        # Check if already have followup_responses from user
        followup_response = state.get("followup_response", {})
        requires_user_input = state.get("requires_user_input", True)
        followup_type = state.get("followup_type", "standard")
        followup_questions = state.get("followup_questions", None)
        current_stage = state.get("current_workflow_stage", "")

        print(f"🔍 Follow-up interaction debug:")
        print(f"   followup_response exists: {bool(followup_response)}")
        print(f"   requires_user_input: {requires_user_input}")
        print(f"   followup_type: {followup_type}")
        print(f"   followup_response keys: {list(followup_response.keys()) if followup_response else 'None'}")
        print(f"   followup_questions: {bool(followup_questions)}")
        print(f"   current_stage: {current_stage}")
        
        if not followup_response and requires_user_input:
            return await self._generate_questions_phase(state)
        elif followup_response and not requires_user_input:
            result = await self._process_responses_phase(state, followup_response)
            if result.get("image_required"): ## skin cancer screening -> image analysis
                result["current_workflow_stage"] = "awaiting_image_upload"
            elif result.get("requires_user_input"): ## skin cancer screening -> standard follow up
                result["current_workflow_stage"] = "awaiting_followup_responses"
            else: # standard follow-up -> overall analysis 
                result["current_workflow_stage"] = "followup_analysis_complete"
            return result
    
    async def _generate_questions_phase(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate questions based on skin cancer screening needs"""
        
        requires_screening = state.get("requires_skin_cancer_screening", False) 
        
        print("Is requires_skin_cancer_screening set?", requires_screening)
        
        if requires_screening:
            print("🔍 Generating skin cancer screening questions")
            questions_list = self._get_skin_cancer_screening_questions()
            state["followup_questions"] = questions_list
            state["followup_type"] = "skin_cancer_screening"
        else:
            print("📝 Using standard follow-up questions")
            questions_list = self._get_universal_medical_questions()
            state["followup_questions"] = questions_list
            state["followup_type"] = "standard"

        state["current_workflow_stage"] = "awaiting_followup_responses"
        return state

    def _get_universal_medical_questions(self) -> list[str]:
        """Comprehensive medical questions that apply to all conditions"""
        return [
            "How long have you been experiencing these symptoms? (hours, days, weeks, months)",
            "Have your symptoms gotten worse, better, or stayed the same since they started?",
            "On a scale of 1-10, how would you rate the severity of your symptoms?",
            "Do you have any other symptoms that you haven't mentioned yet?",
            "Are you currently taking any medications, supplements, or have any known allergies?"
        ]
        
    def _get_skin_cancer_screening_questions(self) -> list[str]:
        """Each questions follows the ABCDE criteria correspondingly which is widely used by clinicians and patients
        to quickly screen for skin cancer warning signs. It stands for:
        Asymmetry, Border, Color, Diameter, and Evolving.
        """
    # "Is the spot asymmetric in shape?",
    # "Are the borders irregular or blurred?",
    # "Does it contain multiple colors?",
    # "Is the size larger than 6mm (pencil eraser)?",
    # "Has the spot changed recently in any way?"
        return [
            #ABCDE criteria questions
            "Is the mole or lesion asymmetrical? (One half doesn't match the other)",
            "Does the border of the mole or lesion appear irregular, ragged, or blurred?",
            "Does it contain more than one color (e.g., black, brown, red)?",
            "Is the diameter of the mole or lesion larger than 6mm (about the size of a pencil eraser)?",
            "Has the mole or lesion changed in size, shape, or color over time?",
            #Additional questions for skin cancer screening
            "Does it bleed, itch, or cause pain?",
            "Do you have a personal or family history of skin cancer or high sun exposure?"
        ]
        
    async def _process_responses_phase(self, state: dict[str, Any], responses: dict[str, str]) -> dict[str, Any]:
        """Process follow-up responses and re-analyze"""
        original_user_input = state.get("userInput_symptoms", "") or state.get("userInput_skin_symptoms", "")
        followup_type = state.get("followup_type", "standard")
        
        state["followup_responses"] = responses  # Store response 
        
        # Combine original symptoms with follow-up responses
        enhanced_symptoms = self._combine_symptoms_and_responses(original_user_input, responses)

        state["followup_qna_overall"] = enhanced_symptoms  # Store user input and qna pairs for overall analysis

        if followup_type == "skin_cancer_screening":
            needs_image_analysis = self.analyze_skin_cancer_risk(responses)
            
            if needs_image_analysis: ## skin cancer screening only
                print("🔍 SKIN CANCER RISK DETECTED - proceeding to image analysis")
                state["image_required"] = True
                state["skin_cancer_risk_detected"] = True
                state["current_workflow_stage"] = "awaiting_image_upload"
                
                enhanced_diagnosis = [
                    {"text_diagnosis": "Skin Cancer Risk Detected - Image Analysis Required", "diagnosis_confidence": None}
                ]
                state["followup_diagnosis"] = enhanced_diagnosis
                
                return state
            else: ## skin cancer screening -> standard follow-up
                print("✅ Low skin cancer risk - transitioning to standard follow-up")

                # Transition to standard follow-up
                state["followup_type"] = "standard"
                state["requires_skin_cancer_screening"] = False
                state["skin_cancer_risk_detected"] = False
                state["image_required"] = False                
                state["skin_cancer_screening_responses"] = state["followup_qna_overall"]
                state["requires_user_input"] = True
                
                #Clean up
                state.pop("followup_questions", None)
                questions_list = self._get_universal_medical_questions()
                state["followup_questions"] = questions_list
                
                state.pop("followup_response", None)
                state.pop("followup_diagnosis", None)
                print("🔄 Transition complete - standard questions generated")
                
                return state
        else: ## standard follow-up only
            state["image_required"] = False
            state["skin_cancer_risk_detected"] = False
            state["requires_user_input"] = False
               
            # Get Q8 model for re-diagnosis
            print(f"🔄 Generating standard follow-up diagnosis with enhanced symptoms...")
            output = await self.adapter.generate_diagnosis(enhanced_symptoms)

            # Parse results using the same parser as LLMDiagnosisNode
            from nodes.llm_diagnosis_node import parse_diagnosis_details
            diagnosis_results = parse_diagnosis_details(output)
            
            # Update state with improved analysis
            state["followup_diagnosis"] = diagnosis_results if diagnosis_results else []
            
            followup_diagnosis = state.get("followup_diagnosis", None)
            if followup_diagnosis and isinstance(followup_diagnosis, list):
                confidence_scores = [
                    diagnosis.get("diagnosis_confidence", 0.0) 
                    for diagnosis in followup_diagnosis
                ]
                
            state["average_confidence"] = sum(confidence_scores) / len(confidence_scores)
            
            print(f"✅ Standard follow-up diagnosis complete - found {len(diagnosis_results)} diagnoses")
            return state
    
    def analyze_skin_cancer_risk(self, responses: dict[str, str]) -> bool:
        threshold = 5
        
        """Risk analysis based on weighted Yes/Neutral/No responses.
        Returns True if risk_score >= threshold."""
        weights = {
            0: 3,  # Asymmetry
            1: 3,  # Border irregularity
            2: 2,  # Color variation
            3: 2,  # Diameter >6mm
            4: 1,  # Evolution
            5: 1,  # Symptoms (bleeding/itching/pain)
            6: 1   # History/exposure
        }

        risk_score = 0
        total_questions = len(weights)

        for idx, (question, response) in enumerate(responses.items()):
            resp = response.lower().strip()
            w = weights.get(idx, 0)

            if resp == 'yes':
                risk_score += w
            elif resp == 'neutral':
                # half weight (rounded down, minimum 1)
                risk_score += max(1, w // 2)
            # 'no' adds 0

        needs_image = risk_score >= threshold

        print(f"🔍 Skin cancer risk analysis:")
        print(f"   Risk score: {risk_score} (threshold: {threshold})")
        print(f"   Needs image analysis: {needs_image}")
        print(f"   Responses: {responses}")

        return needs_image
                    
    
    def _combine_symptoms_and_responses(self, original_symptoms: str, responses: dict[str, str]) -> str:
        """Combine original symptoms with follow-up Q&A pairs"""
        
        # Start with original symptoms
        combined = f"Initial user symptom input: {original_symptoms}\n\n"
        combined += "Follow-up information:\n"
        
        # Add each question-response pair
        for question, response in responses.items():
            combined += f"Q: {question}\n"
            combined += f"A: {response}\n\n"
        
        return combined.strip()
    
    def _parse_questions(self, questions_text: str) -> List[str]:
        """Parse numbered questions from LLM response"""
        lines = questions_text.strip().split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering and clean up
                question = re.sub(r'^\d+\.\s*', '', line)  # Remove "1. "
                question = re.sub(r'^[-•]\s*', '', question)  # Remove "- " or "• "
                if question: 
                    questions.append(question)
        
        # If no structured questions found, return the whole text as one question
        return questions if questions else [questions_text.strip()]
    
    def _get_fallback_questions(self) -> List[str]:
        """Fallback questions if generation fails"""
        return [
            "Can you describe your symptoms in more detail?",
            "How long have you been experiencing these symptoms?",
            "Have you noticed any triggers or patterns?", 
            "Do you have any relevant medical history?",
            "Are you currently taking any medications?"
        ]