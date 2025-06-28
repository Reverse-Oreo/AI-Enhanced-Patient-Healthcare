from adapters.local_model_adapter import LocalModelAdapter
from typing import Dict, Any, List
import re

class FollowUpInteractionNode:
    def __init__(self, adapter: LocalModelAdapter):
        self.adapter = adapter
        
    async def __call__(self, state):
        return await self.handle_followup_interaction(state)
    
    async def handle_followup_interaction(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combined follow-up interaction: generate questions OR process responses
        """
        # Check if we already have followup_responses from user
        followup_response = state.get("followup_response", {})
        
        if not followup_response:
            # Step 1: Generate follow-up questions (first time here)
            print("📝 FOLLOW-UP NODE: Generating questions phase")
            state["current_workflow_stage"] = "generating_followup_questions"
            result = await self._generate_questions_phase(state)
            print("✅ Follow-up questions generated")
            return result
        else:
            # Step 2: Process user responses (user has provided answers)
            print("🔄 FOLLOW-UP NODE: Processing responses phase")
            state["current_workflow_stage"] = "processing_followup_responses"
            result = await self._process_responses_phase(state, followup_response)
            state["current_workflow_stage"] = "followup_analysis_complete"
            print("✅ Follow-up responses processed")
            return result
    
    async def _generate_questions_phase(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate follow-up questions and wait for user input"""
        textual_analysis = state.get("textual_analysis", [])
        average_confidence = state.get("average_confidence", 0.0)
        
        # Handle the textual_analysis structure issue from your existing code 
        if textual_analysis and isinstance(textual_analysis, list) and len(textual_analysis) > 0:
            # Extract just the diagnosis names
            diagnosis_names = [
                diagnosis.get("text_diagnosis", "Unknown") 
                for diagnosis in textual_analysis
            ]        
            # Join all 5 diagnoses
            diagnosis_context = ", ".join(diagnosis_names[:5])
        try:
            # Generate follow-up questions using the adapter
            questions_text = await self.adapter.generate_followup_questions(
                diagnosis_context=diagnosis_context, 
                average_confidence=average_confidence
            )
            # Parse the generated questions
            questions_list = self._parse_questions(questions_text)
            # Update state with questions
            state["followup_questions"] = questions_list

        except Exception as e:
            print(f"❌ Question generation failed: {e}")
            # Use fallback questions
            state["followup_questions"] = self._get_fallback_questions()

        # ✅ UPDATED: Set stage to await user input
        state["current_workflow_stage"] = "awaiting_followup_responses"
        state["requires_user_input"] = True        
        
        print(f"📋 Generated {len(state['followup_questions'])} follow-up questions")
        return state
    
    async def _process_responses_phase(self, state: Dict[str, Any], responses: Dict[str, str]) -> Dict[str, Any]:
        """Process follow-up responses and re-analyze"""
        #Will Force frontend to have structured input
        question = state.get("followup_questions", "")
        original_user_input = state.get("userInput_symptoms", "")
        
        # Combine original symptoms with follow-up responses
        enhanced_symptoms = self._combine_symptoms_and_responses(original_user_input, question, responses)
        
        # Determine image requirement from enhanced symptoms
        skin_keywords = ['skin', 'mole', 'lesion', 'growth', 'bump', 'spot', 'rash', 'patch', 'scab']
        is_skin_related = any(keyword in enhanced_symptoms.lower() for keyword in skin_keywords)
        
        if is_skin_related:
            state["userInput_skin_symptoms"] = enhanced_symptoms #Store user input (skin symptoms) to be used later with skin_lesion_analysis for overall analysis
            state["image_required"] = True
            return state
        else:
            state["followup_qna"] = enhanced_symptoms # Store user input (skin symptoms) to be used later with skin_lesion_analysis for overall analysis
            
            # Re-run diagnosis with enhanced information
            output = await self.adapter.generate_diagnosis(enhanced_symptoms)
            
            # Parse results using the same parser as LLMDiagnosisNode
            from nodes.llm_diagnosis_node import parse_diagnosis_details
            diagnosis_results = parse_diagnosis_details(output)
            
            # Update state with improved analysis
            state["followup_diagnosis"] = diagnosis_results if diagnosis_results else []
            state["image_required"] = is_skin_related
            
            # Clear the user input requirement
            state["requires_user_input"] = False
        return state
    
    def _combine_symptoms_and_responses(self, original_symptoms: str, questions: List[str], responses: Dict[str, str]) -> str:
        """Combine original symptoms with follow-up Q&A pairs"""
        
        # Start with original symptoms
        combined = f"Original symptoms: {original_symptoms}\n\n"
        combined += "Follow-up information:\n"
        
        # Add each question-response pair
        for question, response in responses.items():
            combined += f"Q: {question}\n"
            combined += f"A: {response}\n\n"
        
        # Alternative: if responses dict uses question indices instead of full questions
        if len(questions) > 0 and all(key.isdigit() for key in responses.keys()):
            combined = f"Original symptoms: {original_symptoms}\n\n"
            combined += "Follow-up information:\n"
            
            for idx_str, response in responses.items():
                try:
                    idx = int(idx_str)
                    if 0 <= idx < len(questions):
                        question = questions[idx]
                        combined += f"Q: {question}\n"
                        combined += f"A: {response}\n\n"
                except (ValueError, IndexError):
                    # Handle malformed indices
                    combined += f"Q: Question {idx_str}\n"
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