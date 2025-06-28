from .base import ModelInterface
from typing import Any, Dict, List, Union
import asyncio
import functools
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
import logging
import time

logger = logging.getLogger(__name__)

class LocalModelAdapter(ModelInterface):  
    def __init__(self, 
                 llm_path: str): #locks the model in RAM, which can improve inference speed by preventing paging.
        self.model_path = llm_path
        self.model = None
        self.load_time = None
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
    # Older version of the system prompt for reference
    # """You a helpful, expert AI-powered medical assistant specialized in text symptom evaluation and general health guidance. 
            
    # Follow these instructions at all times:

    # 1. **IDENTITY & PURPOSE**
    # - You are not a licensed medical professional, but you provide evidence-based medical information.
    # - Your role is to interpret user-described symptoms (text and/or images), give potential explanations, advise on urgency of care, and offer general health education.
    # - Always include a clear disclaimer: "I am not a licensed healthcare provider. My responses are informational only and not a substitute for professional medical advice."

    # 2. **SCOPE & LIMITATIONS**
    # - Address only health/medical questions. If the user asks about non-medical topics, respond politely that you can only help with medical matters.
    # - If uncertain, say "I'm not sure; please consult a qualified healthcare professional."

    # 3. **EVIDENCE-BASED & PREVENT HALLUCINATIONS**
    # - Only share well-established medical facts or widely accepted clinical guidelines.
    # - Do not fabricate sources or make up treatment protocols.
    # - When using medical terms, define them briefly in plain language.

    # 4. **SAFETY & TRIAGE**
    # - Recognize "red-flag" symptoms (e.g., chest pain, difficulty breathing, uncontrolled bleeding, stroke signs).
    # - If identified, instruct the user to seek immediate medical attention (e.g., "Call emergency services or go to the nearest hospital.").
    # - For mild to moderate symptoms, suggest general, conservative self-care (e.g., rest, hydration, over-the-counter meds) but remind users to follow up with a provider if symptoms persist.

    # 5. **PRIVACY & CONFIDENTIALITY**
    # - Do not ask for or store personally identifiable information (e.g., full name, address).
    # - Remind users to protect their own privacy when describing sensitive details.

    # 6. **TONE & STYLE**
    # - Be empathetic, respectful, and patient.
    # - Use clear, concise sentences.
    # - Include bullet points or numbered steps for clarity when listing differential diagnoses or management advice.

    # 7. **CLOSING RECOMMENDATION**
    # - End each interaction with a reminder to seek professional care if unsure or if symptoms worsen.
    # - Example closing: "If your condition does not improve or you have any concerns, please consult your healthcare provider promptly."
    # """
        return (
            "You are a helpful, expert AI-powered medical assistant specialized in text symptom evaluation and general health guidance.\n"
            "Always include this disclaimer: 'I am not a licensed healthcare provider. My responses are informational only and not a substitute for professional medical advice.'\n\n"
            "Follow these rules:\n"
            "- Only discuss health/medical topics.\n"
            "- If unsure, say so and recommend seeing a healthcare provider.\n"
            "- Do not hallucinate or fabricate facts.\n"
            "- Define medical terms simply.\n"
            "- Identify red-flag symptoms and escalate when necessary.\n"
            "- Be concise, empathetic, and structured.\n"
            "- stop generating if <|end_of_text|> is reached.\n"
        )
        
    async def load_model(self):
        """Load the medical LLM model"""
        try:
            logger.info(f"🧠 Loading LLM from {self.model_path}")
            start_time = time.time()
            
            # Initialize llama-cpp model
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=8192,           # Context window
                n_threads=8,          # CPU threads
                n_gpu_layers=-1,  # GPU layers
                verbose=True,            # Enable verbose for debugging
                f16_kv=True,
                use_mlock=True,
                temperature=0.3,         # Add temperature
                top_p=0.9,              # Add top_p
            )
            
            self.load_time = time.time() - start_time
            logger.info(f"✅ LLM loaded successfully in {self.load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to load LLM: {e}")
            raise

    async def run_sync(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        func_with_kwargs = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, func_with_kwargs)

    def _format_prompt(self, user_input: str) -> str:
        return (
            # "<|begin_of_text|>"
            "<|start_header_id|>system<|end_header_id|>\n"
            f"{self.system_prompt}<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n"
            f"{user_input}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n"
        )

    def _generate_text_sync(self, prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> str:
        try:
            if not self.model:
                raise ValueError("Model not loaded")
            
            # Format using Llama-3 chat template
            formatted_prompt = self._format_prompt(prompt)
            
            # Use direct generation instead of chat completion
            response = self.model(
                formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["<|eot_id|>", "<|end_of_text|>", "STOP_GENERATION","Human:","User:","\n\n---"],
                echo=False
            )
            result = response['choices'][0]['text'].strip()
            logger.debug(f"🧠 Generated output: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            return ""

    async def generate_diagnosis(self, symptoms: str, context: Union[str, None] = None) -> str: 
        prompt = f"""
    Symptoms: {symptoms}
    Provide 5 most possible diagnoses in this EXACT format:

    - Diagnosis: <condition name>
    - Confidence: <0.0-1.0> 
    
    Repeat the above 2 lines per diagnosis. No additional text allowed.
    """
        return await self.run_sync(self._generate_text_sync, prompt, 150, 0.5)

    async def generate_followup_questions(self, diagnosis_context: str, average_confidence: float) -> str:
        """Generate follow-up questions based on diagnosis context and confidence"""
        
        # Determine confidence level for question targeting
        if average_confidence < 0.3:
            confidence_note = "Low confidence - need detailed clarification"
            question_focus = "comprehensive symptom details, duration, and medical history"
        elif average_confidence < 0.6:
            confidence_note = "Moderate confidence - need specific clarification" 
            question_focus = "specific symptoms, timing, and related factors"
        
        prompt = f"""
    Based on suspected condition(s): {diagnosis_context}
    Confidence level: {average_confidence:.2f} ({confidence_note})

    Generate ONLY 5 focused follow-up questions to help clarify the diagnosis.

    Focus on {question_focus}.

    Questions should cover:
    1. Symptom duration and progression
    2. Associated symptoms not yet mentioned  
    3. Relevant medical history or medications
    4. Triggers, patterns, or timing
    5. Severity and impact on daily activities

    Format as numbered questions (1., 2., 3., etc.).
    Keep questions clear, specific, and medically relevant.
    """
        
        return await self.run_sync(self._generate_text_sync, prompt, 400, 0.5)
    
    # async def retrieve_medical_evidence(self, diagnosis: str) -> List[str]:
    #     """Retrieve supporting medical evidence for a diagnosis (RAG-style)"""
    #     prompt = f"""
    #     Provide 2-3 evidence-based facts or guidelines related to: {diagnosis}
        
    #     Focus on:
    #     1. Clinical presentation
    #     2. Standard treatment approaches  
    #     3. When to seek specialist care
        
    #     Format each as a separate, concise statement.
    #     Reference medical guidelines where applicable.
    #     """
        
    #     result = await self.run_sync(self._generate_text_sync, prompt, 300, 0.3)
    #     return [line.lstrip('-•*0123456789. ').strip() for line in result.split('\n') if line.strip()][:3]
    
    # async def generate_medical_evidence(self, prompt: str) -> str:
    #     """Generate evidence-based medical recommendations"""
    #     full_prompt = (
    #     "You are a medical evidence specialist. Provide evidence-based recommendations with the input below:\n"
        
    #     f"{prompt}\n"
        
    #     "Reference established medical guidelines and clinical best practices.\n"
    #     "Keep recommendations concise and clinically relevant.\n"
    #     "Mention the strength of evidence when possible."
    #     )
    #     return await self.run_sync(self._generate_text_sync, full_prompt, 400, 0.3)

    async def generate_enhanced_textual_analysis(self, symptoms: str, diagnosis: str, confidence: float) -> str:
        """Generate enhanced analysis for textual-only workflow (Instance 1)"""
        
        prompt = f"""
    Original Symptoms: {symptoms}
    Initial Diagnosis: {diagnosis}
    Initial Confidence: {confidence:.2f}
    
    Provide enhanced analysis with:
    1. Final refined diagnosis
    2. Enhanced confidence level (0.0-1.0)
    3. Severity assessment (mild/moderate/severe/critical/emergency)
    4. Detailed medical reasoning and justification
    5. Appropriate specialist recommendation
    
    Format:
    Final Diagnosis: [refined diagnosis]
    Confidence: [0.0-1.0]
    Severity: [mild/moderate/severe/critical/emergency]
    Reasoning: [detailed medical justification]
    Specialist: [most appropriate specialist - be specific, e.g., "pediatric cardiologist", "interventional radiologist", "infectious disease specialist"]
        """
        
        return await self.run_sync(self._generate_text_sync, prompt, 400, 0.3)

    async def generate_combined_analysis(self, skin_symptoms: str, image_diagnosis: str, image_confidence: Dict) -> str:
        """Generate analysis for textual + image workflow (Instance 2)"""
        
        max_confidence = max(image_confidence.values()) / 100 if image_confidence else 0.0
        
        prompt = f"""
        Skin Symptoms: {skin_symptoms}
        Image Diagnosis: {image_diagnosis}
        Image Confidence: {max_confidence:.2f}
        
        Provide integrated analysis considering both skin symptoms and image findings:
        1. Final integrated diagnosis
        2. Combined confidence assessment
        3. Severity level
        4. Consistency between symptom description and image
        5. Specialist recommendations
        
        Format:
        Final Diagnosis: [integrated diagnosis]
        Confidence: [0.0-1.0]
        Severity: [mild/moderate/severe/critical]
        Reasoning: [integration justification]
        Specialist: [most appropriate specialist - be specific, e.g., "pediatric cardiologist", "interventional radiologist", "infectious disease specialist"]
        """
        
        return await self.run_sync(self._generate_text_sync, prompt, 500, 0.3)

    async def generate_followup_enhanced_analysis(self, original_symptoms: str, followup_responses: Dict, enhanced_diagnosis: str, enhanced_confidence: float) -> str:
        """Generate analysis for textual + follow-up workflow (Instance 3)"""
        
        # Format follow-up responses
        followup_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in followup_responses.items()])
        
        prompt = f"""
        FOLLOW-UP ENHANCED ANALYSIS
        
        Original Symptoms: {original_symptoms}
        Enhanced Diagnosis: {enhanced_diagnosis}
        Enhanced Confidence: {enhanced_confidence:.2f}
        
        Follow-up Information:
        {followup_text}
        
        Provide comprehensive analysis incorporating follow-up responses:
        1. Refined final diagnosis
        2. Updated confidence level
        3. Severity assessment
        4. How follow-up responses changed the diagnosis
        5. Remaining uncertainties or concerns
        
        Format:
        Final Diagnosis: [refined diagnosis]
        Confidence: [0.0-1.0]
        Severity: [mild/moderate/severe/critical]
        Reasoning: [follow-up integration reasoning]
        Specialist: [most appropriate specialist - be specific, e.g., "pediatric cardiologist", "interventional radiologist", "infectious disease specialist"]
        """
        
        return await self.run_sync(self._generate_text_sync, prompt, 600, 0.3)

    async def generate_comprehensive_analysis(self, original_symptoms: str, followup_responses: Dict, followup_diagnosis: Dict, skin_symptoms: str, image_analysis: Dict) -> str:
        """Generate comprehensive analysis for all data workflow (Instance 4)"""
        
        # Format all available data
        followup_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in followup_responses.items()])
        image_diagnosis = image_analysis.get("image_diagnosis", "No image diagnosis")
        image_confidence = image_analysis.get("confidence_score", {})
        max_image_conf = max(image_confidence.values()) / 100 if image_confidence else 0.0
        
        prompt = f"""
        COMPREHENSIVE MEDICAL ANALYSIS
        
        Original Symptoms: {original_symptoms}
        Follow-up Diagnosis: {followup_diagnosis.get("text_diagnosis", "Unknown")}
        Follow-up Confidence: {followup_diagnosis.get("diagnosis_confidence", 0.0):.2f}
        
        Follow-up Responses:
        {followup_text}
        
        Skin Symptoms: {skin_symptoms}
        Image Diagnosis: {image_diagnosis}
        Image Confidence: {max_image_conf:.2f}
        
        Provide the most comprehensive analysis possible:
        1. Final integrated diagnosis considering ALL data
        2. Highest confidence assessment possible
        3. Definitive severity level
        4. Complete medical reasoning
        5. Most appropriate specialist recommendation
        
        Format:
        Final Diagnosis: [most comprehensive diagnosis]
        Confidence: [0.0-1.0]
        Severity: [mild/moderate/severe/critical]
        Reasoning: [complete integration reasoning]
        Specialist: [most appropriate specialist - be specific, e.g., "pediatric cardiologist", "interventional radiologist", "infectious disease specialist"]
        """
        
        return await self.run_sync(self._generate_text_sync, prompt, 800, 0.3)

    async def generate_self_care_advice(self, prompt: str) -> str:
        """Generate self-care advice based on user symptoms or diagnosis"""
        full_prompt = (
            "You are a medical self-care advisor. Provide practical, evidence-based self-care advice:\n"
            f"{prompt}\n"
            "Focus on home remedies, lifestyle changes, and over-the-counter options.\n"
            "Avoid suggesting prescription medications or invasive procedures."
        )
        return await self.run_sync(self._generate_text_sync, full_prompt, 512, 0.3)

    async def generate_medical_report(self, report_prompt: str) -> str:
        """Generate a comprehensive medical report based on analysis data"""
        prompt = (
            "Generate a structured, professional medical report:\n"
            f"{report_prompt}\n"
            "Include sections: Summary, Observations, Recommendations.\n"
            "Use clinical tone and terminology."
        )
        return await self.run_sync(self._generate_text_sync, prompt, 1024, 0.3)