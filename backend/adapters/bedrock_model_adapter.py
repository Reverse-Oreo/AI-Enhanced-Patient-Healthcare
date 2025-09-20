from .base import ModelInterface
from typing import Any, Dict
import asyncio
import json
import logging
import re
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class BedrockModelAdapter(ModelInterface):  
    def __init__(self, 
                 model_id: str,
                 region_name: str = "us-east-1"):
        self.model_id = model_id
        self.region_name = region_name
        self.client = None
        
        # Simple model detection - just check if it's Llama or use default
        self.is_llama = "llama" in model_id.lower()
        
        logger.info(f"🔧 Bedrock Medical Adapter:")
        logger.info(f"   Model ID: {model_id}")
        logger.info(f"   Model Type: {'Llama' if self.is_llama else 'Default (Claude-like)'}")
        logger.info(f"   Region: {region_name}")

    async def load_model(self):
        """Initialize Bedrock client"""
        try:
            logger.info("🚀 Initializing AWS Bedrock client...")
            
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=self.region_name
            )
            
            # Test with simple request
            await self._test_connection()
            
            model_name = "Llama" if self.is_llama else "Bedrock Model"
            logger.info(f"✅ {model_name} ready for medical inference")
                
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found. Configure AWS credentials first.")
            raise
        except ClientError as e:
            logger.error(f"❌ Bedrock access error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Client initialization failed: {e}")
            raise

    async def _test_connection(self):
        """Test Bedrock connection"""
        try:
            body = self._prepare_request_body("Test", max_tokens=10, temperature=0.1)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.invoke_model(
                    modelId=self.model_id,
                    body=body,
                    contentType='application/json',
                    accept='application/json'
                )
            )
            
            if response:
                logger.info("🔍 Connection test successful")
            else:
                raise Exception("Connection test failed")
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            raise

    def _prepare_request_body(self, prompt: str, max_tokens: int = 512, temperature: float = 0.1) -> str:
        """Prepare request body - Llama format or default Claude format"""
        
        # Llama 3.1 instruction format
        formatted_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an AI medical assistant. Provide accurate, structured responses. Always follow the exact format requested. Be concise and professional.<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        body = {
            "prompt": formatted_prompt,
            "max_gen_len": max_tokens,
            "temperature": temperature,
            "top_p": 0.7
        }
        
        return json.dumps(body)

    def _extract_text_from_response(self, response_body: dict) -> str:
        """Extract text from response - try Llama format first, then common patterns"""
        try:
            if self.is_llama:
                # Llama response format
                return response_body.get("generation", "").strip()
            else:
                # Default Claude format
                return response_body.get("content", [{}])[0].get("text", "").strip()
                
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"Primary extraction failed: {e}")
            
            # Fallback: try common response patterns
            fallback_patterns = [
                "generation",  # Llama
                ["content", 0, "text"],  # Claude
                ["results", 0, "outputText"],  # Titan
                ["generations", 0, "text"],  # Cohere
                "text",  # Generic
                "response"  # Generic
            ]
            
            for pattern in fallback_patterns:
                try:
                    if isinstance(pattern, str):
                        result = response_body.get(pattern, "")
                    else:
                        result = response_body
                        for field in pattern:
                            result = result[field]
                    
                    if result:
                        return str(result).strip()
                        
                except (KeyError, IndexError, TypeError):
                    continue
            
            logger.error(f"Could not extract text from response: {response_body}")
            return ""

    async def _generate_text_async(self, prompt: str, max_tokens: int = 512, temperature: float = 0.1) -> str:
        """Generate text using Bedrock model"""
        try:
            if not self.client:
                raise ValueError("Bedrock client not initialized")
            
            body = self._prepare_request_body(prompt, max_tokens, temperature)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.invoke_model(
                    modelId=self.model_id,
                    body=body,
                    contentType='application/json',
                    accept='application/json'
                )
            )
            
            response_body = json.loads(response['body'].read().decode('utf-8'))
            return self._extract_text_from_response(response_body)
            
        except Exception as e:
            logger.error(f"Bedrock generation error: {e}")
            return ""

    # =============================================================================
    # CONFIDENCE CALCULATION METHODS (unchanged)
    # =============================================================================

    def _calculate_diagnosis_specificity(self, diagnosis: str) -> float:
        """Calculate how specific/detailed the diagnosis is"""
        word_count = len(diagnosis.split())
        
        medical_terms = ['syndrome', 'disease', 'disorder', 'condition', 'infection', 
                        'deficiency', 'inflammation', 'acute', 'chronic', 'primary', 'secondary']
        has_medical_terms = any(term.lower() in diagnosis.lower() for term in medical_terms)
        
        specificity_indicators = ['stage', 'grade', 'type', 'variant', 'sub', 'mild', 'severe', 'moderate']
        has_specificity = any(ind.lower() in diagnosis.lower() for ind in specificity_indicators)
        
        score = 0.5
        score += min(0.3, word_count * 0.05)
        score += 0.15 if has_medical_terms else 0
        score += 0.1 if has_specificity else 0
        
        return min(1.0, score)

    def _calculate_symptom_alignment(self, diagnosis: str, symptoms: str) -> float:
        """Calculate how well diagnosis aligns with reported symptoms"""
        if not symptoms:
            return 0.5
        
        symptom_keywords = symptoms.lower().split()
        diagnosis_keywords = diagnosis.lower().split()
        
        alignment_keywords = {
            'chest pain': ['heart', 'cardiac', 'angina', 'myocardial', 'coronary'],
            'headache': ['migraine', 'tension', 'cluster', 'neurological'],
            'fever': ['infection', 'inflammatory', 'viral', 'bacterial'],
            'cough': ['respiratory', 'bronchitis', 'pneumonia', 'asthma'],
            'fatigue': ['anemia', 'thyroid', 'depression', 'chronic'],
            'skin': ['dermatitis', 'eczema', 'psoriasis', 'rash', 'lesion']
        }
        
        alignment_score = 0.5
        
        for symptom_word in symptom_keywords:
            if any(symptom_word in diag_word for diag_word in diagnosis_keywords):
                alignment_score += 0.1
        
        for symptom_phrase, related_terms in alignment_keywords.items():
            if symptom_phrase in symptoms.lower():
                if any(term in diagnosis.lower() for term in related_terms):
                    alignment_score += 0.15
        
        return min(1.0, alignment_score)

    def _get_condition_commonality(self, diagnosis: str) -> float:
        """Get commonality score (common conditions = higher confidence)"""
        common_conditions = [
            'common cold', 'flu', 'hypertension', 'diabetes', 'migraine', 'tension headache', 'gastritis',
            'bronchitis', 'pneumonia', 'urinary tract infection', 'allergic rhinitis', 'asthma',
            'eczema', 'anemia', 'depression', 'anxiety', 'otitis media', 'sinusitis', 'conjunctivitis'
        ]
        
        rare_conditions = [
            'lupus', 'multiple sclerosis', 'rare genetic', 'exotic', 'zebra diagnosis', 'uncommon', 'atypical'
        ]
        
        diagnosis_lower = diagnosis.lower()
        
        if any(common in diagnosis_lower for common in common_conditions):
            return 0.8
        elif any(rare in diagnosis_lower for rare in rare_conditions):
            return 0.4
        else:
            return 0.6

    def _assess_diagnosis_quality(self, diagnosis: str) -> float:
        """Assess the quality of the diagnosis text"""
        vague_terms = ['possible', 'maybe', 'could be', 'might be', 'uncertain', 'unclear']
        has_vague_terms = any(term in diagnosis.lower() for term in vague_terms)
        
        confident_terms = ['definitely', 'certain', 'verified', 'confirmed', 'definitive']
        has_confident_terms = any(term in diagnosis.lower() for term in confident_terms)
        
        score = 0.7
        score -= 0.2 if has_vague_terms else 0
        score += 0.15 if has_confident_terms else 0
        
        return max(0.3, min(1.0, score))

    def _calculate_enhanced_confidence(self, diagnosis_text: str, position: int, temperature: float, 
                                     total_diagnoses: int, symptoms: str) -> float:
        """Calculate confidence using multiple medical factors"""
        
        position_factor = 0.95 ** position
        temp_factor = max(0.6, 1.0 - (temperature * 1.5))
        specificity_score = self._calculate_diagnosis_specificity(diagnosis_text)
        alignment_score = self._calculate_symptom_alignment(diagnosis_text, symptoms)
        commonality_score = self._get_condition_commonality(diagnosis_text)
        quality_score = self._assess_diagnosis_quality(diagnosis_text)
        
        base_confidence = (
            position_factor * 0.25 +
            temp_factor * 0.20 +
            specificity_score * 0.20 +
            alignment_score * 0.15 +
            commonality_score * 0.10 +
            quality_score * 0.10
        )
        
        if position >= 2:
            base_confidence *= (0.85 ** (position - 1))
        
        return max(0.25, min(0.92, base_confidence))

    async def _generate_with_confidences_async(self, prompt: str, max_tokens: int = 65, temperature: float = 0.1) -> str:
        """Generate diagnoses with enhanced confidence calculation"""
        if not self.client:
            raise ValueError("Bedrock client not initialized")

        prompt_no_conf = re.sub(r"-\s*confidence.*?<0.0-1.0>", "", prompt, flags=re.IGNORECASE)
        
        model_type = "Llama" if self.is_llama else "Default"
        logger.info(f"Using blackbox-based confidence calculation for {model_type}")
        
        raw_text = await self._generate_text_async(prompt_no_conf, max_tokens, temperature)
        
        if not raw_text:
            logger.warning(f"Empty response from {model_type}")
            return ""

        diag_pattern = re.compile(r"^\s*-\s*diagnosis\s*:\s*(.+)$", re.IGNORECASE)
        lines = raw_text.splitlines()
        diagnosis_indices = [i for i, line in enumerate(lines) if diag_pattern.match(line)]

        symptoms_match = re.search(r"Symptoms:\s*(.+?)(?:\n|$)", prompt_no_conf, re.IGNORECASE)
        original_symptoms = symptoms_match.group(1) if symptoms_match else ""

        for idx in reversed(range(len(diagnosis_indices))):
            diag_idx = diagnosis_indices[idx]
            diagnosis_text = lines[diag_idx].split(":", 1)[1].strip() if ":" in lines[diag_idx] else ""
            
            enhanced_confidence = self._calculate_enhanced_confidence(
                diagnosis_text, idx, temperature, len(diagnosis_indices), original_symptoms
            )
            
            lines.insert(diag_idx + 1, f"- confidence: {enhanced_confidence:.3f}")

        return "\n".join(lines)
    
    # =============================================================================
    # PUBLIC API METHODS (unchanged)
    # =============================================================================
    
    async def generate_diagnosis(self, symptoms: str) -> str: 
        """High-accuracy diagnosis generation"""
        prompt = f"""Symptoms: {symptoms}
List 5 most possible diagnoses in this exact format ONLY:
- diagnosis: <name>
"""
        return await self._generate_with_confidences_async(prompt, 65, 0.1)
    
    async def generate_text_guidance(self, prompt: str, max_tokens: int = 200, temperature: float = 0.2) -> str:
        """Generate short, focused guidance text"""
        return await self._generate_text_async(prompt, max_tokens, temperature)

    async def generate_overall_instance1(self, symptoms: str, diagnosis: str, confidence: float) -> str:
        """Generate enhanced analysis for textual-only workflow (Instance 1)"""
        
        prompt = f"""
        MEDICAL ANALYSIS

        CONFIRMED DIAGNOSIS: {diagnosis} (Confidence: {confidence:.2f})
        Original Symptoms: {symptoms}
        
        Based on the confirmed diagnosis above, provide output in this EXACT format:                
        - Severity: <mild/moderate/severe/critical>
        - User Explanation: <Simple definition of {diagnosis} and its main causes>
        - Clinical Reasoning: <detailed medical justification based on user's original symptom ({symptoms}) & confirmed diagnosis ({diagnosis})>
        - Specialist: <choose MOST appropriate specialist type (separate with " / " if there is more than one)>
        
        Keep User Explanation around 50 words. Keep Clinical Reasoning under 60 words and focused on main symptoms only.
        """
        
        return await self._generate_text_async(prompt, 400, 0.3)

    async def generate_overall_instance2(self, followup_qna: str, image_diagnosis: str, image_confidence_scores: dict, max_confidence, risk_context: str = "") -> str:
        """Generate analysis for textual + image workflow (Instance 2)"""
        
        prompt = f"""
    COMPREHENSIVE SKIN LESION ANALYSIS

    PATIENT SCREENING RESPONSES:
    {followup_qna}

    {risk_context}

    IMAGE ANALYSIS RESULTS:
    - AI Image Diagnosis: {image_diagnosis}
    - Image Confidence: {max_confidence:.1f}%
    - All Image Predictions: {dict(sorted(image_confidence_scores.items(), key=lambda x: x[1], reverse=True))}

    INTEGRATION INSTRUCTIONS:
    Synthesize the ABCDE screening responses, risk assessment, and image analysis to determine the most appropriate diagnosis. Consider:
    1. Do the ABCDE findings support the image diagnosis?
    2. Does patient history/symptoms align with image findings?
    3. Are there any contradictions that need resolution?
    4. What is the most clinically appropriate diagnosis considering all evidence?

    Provide output in this EXACT format:
    - Final Diagnosis: <most appropriate diagnosis considering ALL evidence>
    - Confidence: <0.0-1.0 based on evidence concordance>
    - Severity: <mild/moderate/severe/critical>
    - User Explanation: <Explanation of the diagnosed skin condition>
    - Clinical Reasoning: <detailed justification integrating screening, ABCDE, and image findings>
    - Specialist: <appropriate specialist>

    Keep explanations under 30 words, reasoning under 80 words.
    """
        
        return await self._generate_text_async(prompt, 600, 0.3)

    async def generate_overall_instance3(self, followup_qna: str, enhanced_diagnosis: str, enhanced_confidence: float) -> str:
        """Generate analysis for textual + follow-up workflow (Instance 3)"""
        
        confidence = enhanced_confidence if enhanced_confidence is not None else 0.0
        diagnosis = enhanced_diagnosis if enhanced_diagnosis is not None else "Unknown condition"
        followup = followup_qna if followup_qna is not None else "No follow-up information available"
        
        prompt = f"""
        ENHANCED MEDICAL ANALYSIS

        Follow-up Information:
        {followup}

        CONFIRMED DIAGNOSIS: {diagnosis} (Confidence: {confidence:.2f})

        Based on the confirmed diagnosis above, provide output in this EXACT format:                
        - Severity: <mild/moderate/severe/critical>
        - User Explanation: <Simple definition of {diagnosis} and its main causes>
        - Clinical Reasoning: <detailed medical justification based on user's follow-up information & confirmed diagnosis stated above>
        - Specialist: <choose MOST appropriate specialist type (separate with " / " if there is more than one)>
        
        Keep User Explanation around 50 words. Keep Clinical Reasoning under 60 words and focused on main symptoms only.
        """
        
        return await self._generate_text_async(prompt, 300, 0.3)

    async def generate_medical_report(self, report_prompt: str) -> str:
        """Generate a comprehensive medical report based on analysis data"""
        prompt = (
            "Generate a structured, professional medical report:\n"
            f"{report_prompt}\n"
            "Include sections: Summary, Observations, Recommendations.\n"
            "Use clinical tone and terminology."
        )
        return await self._generate_text_async(prompt, 1024, 0.3)
    
    # =============================================================================
    # PERFORMANCE AND STATUS METHODS
    # =============================================================================
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for Bedrock adapter"""
        return {
            "framework": "AWS Bedrock",
            "model_id": self.model_id,
            "model_type": "Llama" if self.is_llama else "Default",
            "region": self.region_name,
            "client_initialized": self.client is not None,
            "provider": "AWS Bedrock",
            "type": "Cloud API",
            "local_resources": "Not applicable (cloud-based)"
        }

    def add_model_support(self, model_keyword: str, request_formatter: callable, response_extractor: callable):
        """
        Easy way to add support for new models without modifying core code
        
        Usage:
        adapter.add_model_support(
            "titan",
            lambda prompt, max_tokens, temp: {...},  # request format
            lambda response: response.get("results", [{}])[0].get("outputText", "")  # response extraction
        )
        """
        # This would be implemented if you want to add more models dynamically
        # For now, just manually add them to the existing if/else logic
        pass