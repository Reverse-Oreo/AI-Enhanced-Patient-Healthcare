from typing import List, TypedDict, Tuple
import re
# from models.ai_schema import SymptomAnalysis  # We still use this to define and validate the output schema
from adapters.local_model_adapter import LocalModelAdapter
from schemas.medical_schemas import TextualSymptomAnalysisResult

import re
from typing import List, TypedDict

def parse_diagnosis_details(raw_response: str) -> List[TextualSymptomAnalysisResult]:
    results: List[TextualSymptomAnalysisResult] = []
    
    # --- Extract Each Diagnosis Block ---
    diagnosis_pattern = re.compile(
        r"-\s*Diagnosis:\s*(.*?)\s*"
        r"-\s*Confidence:\s*([0-9.]+)\s*",

        re.IGNORECASE | re.DOTALL
    )

    for match in diagnosis_pattern.finditer(raw_response):
        diagnosis, confidence = match.groups()
        result: TextualSymptomAnalysisResult = {
            "text_diagnosis": diagnosis.strip(),
            "diagnosis_confidence": float(confidence.strip()),
        }
        results.append(result)
        
    results.sort(key=lambda x: x["diagnosis_confidence"], reverse=True)

    return results

class LLMDiagnosisNode:
    def __init__(self, adapter: LocalModelAdapter):
        self.adapter = adapter
    
    async def __call__(self, state:dict) -> dict:
        state["current_workflow_stage"] = "textual_analysis"
        
        print("🩺 LLM DIAGNOSIS NODE CALLED!")
        print(f"    Input: {state.get('latest_user_message', 'NO MESSAGE')}")
        print(f"    Stage: {state.get('current_workflow_stage', 'NO STAGE')}")
        
        # Process the diagnosis
        state = await self.diagnose(state)
        
        print(f"✅ LLM Diagnosis complete - found {len(state.get('textual_analysis', []))} diagnoses")
        
        return state
        
    async def diagnose(self, state:dict) -> dict:
        # Directly use the text since validation was done upstream.'
        text = state.get("latest_user_message", "")
        
        # Pre-filter for skin conditions
        skin_keywords = ['skin', 'mole', 'lesion', 'growth', 'bump', 'spot', 'rash', 'patch', 'scab']
        is_skin_related = any(keyword in text.lower() for keyword in skin_keywords)
        
        if is_skin_related:
            state["userInput_skin_symptoms"] = text # Store user input (skin symptoms) to be used later with skin_lesion_analysis for overall analysis
            state["image_required"] = True 

            placeholder_skin_diagnoses = [
                {"text_diagnosis": "Skin Condition (Image Analysis Required)", "diagnosis_confidence": 0.5},
                {"text_diagnosis": "Dermatological Assessment Needed", "diagnosis_confidence": 0.4},
                {"text_diagnosis": "Visual Examination Required", "diagnosis_confidence": 0.3}
            ]
            
            state["textual_analysis"] = placeholder_skin_diagnoses
            state["average_confidence"] = 0.4  # Low confidence to ensure proper routing
            
            return state
        else:
            state["userInput_symptoms"] = text # Store user input (non-skin symptoms) to be used later with textual_analysis for overall analysis
            output = await self.adapter.generate_diagnosis(text)
            
            #parse multiple diagnoses
            parsed_diagnosis = parse_diagnosis_details(output)
            
            #Save list to the agent state
            state["textual_analysis"] = parsed_diagnosis
            #Save bool to indicate if image is required
            state["image_required"] = False #When diagnosis is needed to be parsed from llm response, then it is assumed that image is not required 

            return state