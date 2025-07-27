# In medical_report_node.py - Fix the main workflow method
from adapters.local_model_adapter import LocalModelAdapter
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import re
import logging

# PDF/Word imports 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from io import BytesIO

logger = logging.getLogger(__name__)

class MedicalReportNode:
    def __init__(self, adapter: LocalModelAdapter):
        self.adapter = adapter
    
    async def __call__(self, state: dict) -> dict:
        """Generate medical report content, NOT export file"""
        print("📄 MEDICAL REPORT NODE CALLED!")
        
        # Set stage when node starts
        state["current_workflow_stage"] = "generating_medical_report"
        
        # 🔧 FIX: Generate the actual medical report content
        state = await self.generate_medical_report_content(state)
        
        # Mark as complete
        state["current_workflow_stage"] = "workflow_complete"
        
        return state
    
    async def generate_medical_report_content(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive medical report content using LLM"""
        
        try:
            print("🔄 Generating medical report content...")
            
            # Create comprehensive report prompt
            report_prompt = self._create_comprehensive_report_prompt(state)
            
            # Generate report content using LLM
            medical_report = await self.adapter.generate_medical_report(report_prompt)
            
            # Store in state
            state["medical_report"] = medical_report
            
            print("✅ Medical report content generated successfully")
            return state
            
        except Exception as e:
            print(f"❌ Medical report generation failed: {e}")
            # Generate fallback report
            state["medical_report"] = self._generate_fallback_report(state)
            return state
    
    def _create_comprehensive_report_prompt(self, state: Dict[str, Any]) -> str:
        """Create a detailed prompt for medical report generation"""
        
        overall_analysis = state.get("overall_analysis", {})
        workflow_path = state.get("workflow_path", [])
        
        # Get original inputs
        original_symptoms = state.get("userInput_symptoms", "") or state.get("userInput_skin_symptoms", "")
        followup_data = state.get("followup_response", {})
        image_analysis = state.get("skin_lesion_analysis", {})
        
        # Determine analysis type
        has_followup = bool(followup_data)
        has_image = bool(image_analysis.get("image_diagnosis"))
        
        prompt = f"""
Generate a comprehensive medical analysis report based on the following information:

=== PATIENT CASE SUMMARY ===
Session ID: {state.get('session_id', 'Unknown')}
Analysis Date: {datetime.now().strftime('%B %d, %Y')}
Analysis Type: {"Comprehensive" if has_followup and has_image else "Enhanced" if has_followup or has_image else "Standard"}

=== PRIMARY FINDINGS ===
Final Diagnosis: {overall_analysis.get('final_diagnosis', 'Not available')}
Diagnostic Confidence: {(overall_analysis.get('final_confidence', 0) * 100):.1f}%
Severity Assessment: {overall_analysis.get('final_severity', 'unknown').title()}
Recommended Specialist: {overall_analysis.get('specialist_recommendation', 'general_practitioner').replace('_', ' ').title()}

=== PATIENT PRESENTATION ===
Primary Symptoms: {original_symptoms}
"""

        # Add follow-up information if available
        if has_followup:
            prompt += f"""
=== ENHANCED SYMPTOM ANALYSIS ===
Follow-up Information Provided: Yes
Additional Clinical Details: Enhanced through structured questioning
"""
            # Add a few key follow-up responses
            if followup_data:
                prompt += "Key Follow-up Responses:\n"
                for i, (question, response) in enumerate(list(followup_data.items())[:3]):
                    prompt += f"  • Q: {question}\n    A: {response}\n"

        # Add image analysis if available
        if has_image:
            prompt += f"""
=== VISUAL ASSESSMENT ===
Image Analysis Performed: Yes
Image-Based Findings: {image_analysis.get('image_diagnosis', 'No specific findings')}
Visual Assessment Method: AI-powered dermatological analysis
"""

        prompt += f"""
=== CLINICAL ASSESSMENT ===
Patient Explanation: {overall_analysis.get('user_explanation', 'Not available')}
Clinical Reasoning: {overall_analysis.get('clinical_reasoning', 'Not available')}

=== WORKFLOW ANALYSIS ===
Analysis Pathway: {' → '.join(workflow_path) if workflow_path else 'Standard workflow'}
Data Sources Used: {"Symptoms, Follow-up Questions, Medical Images" if has_followup and has_image else "Symptoms, Follow-up Questions" if has_followup else "Symptoms, Medical Images" if has_image else "Symptoms"}

Please generate a comprehensive medical report with the following sections:

1. EXECUTIVE SUMMARY
   - Brief case overview and key findings
   - Primary diagnosis and confidence assessment
   - Urgency level and recommended actions

2. CLINICAL PRESENTATION
   - Detailed symptom analysis
   - Patient-reported concerns and history
   - Clinical significance of findings

3. DIAGNOSTIC ASSESSMENT
   - Diagnostic reasoning and methodology
   - Confidence analysis and supporting evidence
   - Alternative diagnoses considered (if applicable)
   - Severity assessment and clinical implications

4. ANALYSIS METHODOLOGY
   - Workflow stages completed
   - Types of analysis performed (textual, image, enhanced questioning)
   - Data quality and completeness assessment

5. CLINICAL RECOMMENDATIONS
   - Immediate care recommendations
   - Specialist referral guidance
   - Follow-up care instructions
   - Monitoring recommendations

6. PATIENT GUIDANCE
   - Next steps and timeline
   - Warning signs to monitor
   - When to seek immediate medical attention
   - General health maintenance advice

7. MEDICAL DISCLAIMERS
   - AI analysis limitations and scope
   - Professional consultation requirements
   - Emergency care guidance

Format the report professionally with clear medical language appropriate for both healthcare providers and informed patients. Ensure all recommendations are evidence-based and clinically sound.
"""
        
        return prompt
    
    def _generate_fallback_report(self, state: Dict[str, Any]) -> str:
        """Generate a fallback report if LLM generation fails"""
        
        overall_analysis = state.get("overall_analysis", {})
        session_id = state.get("session_id", "Unknown")
        
        return f"""
MEDICAL ANALYSIS REPORT
Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Session ID: {session_id}

═══════════════════════════════════════════════════════════════════
                    EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════════

Primary Diagnosis: {overall_analysis.get('final_diagnosis', 'Analysis incomplete')}

Based on the comprehensive analysis of provided symptoms, our AI medical assistant has completed the diagnostic assessment with the findings detailed below.

═══════════════════════════════════════════════════════════════════
                    CLINICAL FINDINGS
═══════════════════════════════════════════════════════════════════

DIAGNOSTIC ASSESSMENT:
• Primary Diagnosis: {overall_analysis.get('final_diagnosis', 'Not determined')}
• Confidence Level: {(overall_analysis.get('final_confidence', 0) * 100):.1f}%
• Severity Assessment: {overall_analysis.get('final_severity', 'unknown').title()}

CLINICAL EXPLANATION:
{overall_analysis.get('user_explanation', 'Comprehensive analysis was performed based on the provided symptom information.')}

CLINICAL REASONING:
{overall_analysis.get('clinical_reasoning', 'Diagnosis determined through systematic analysis of symptoms and clinical indicators.')}

═══════════════════════════════════════════════════════════════════
                    RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════

SPECIALIST CONSULTATION:
Recommended Specialist: {overall_analysis.get('specialist_recommendation', 'general_practitioner').replace('_', ' ').title()}

NEXT STEPS:
1. Schedule consultation with recommended specialist
2. Continue monitoring symptoms as described
3. Seek immediate medical attention if symptoms worsen
4. Follow up as directed by healthcare provider

═══════════════════════════════════════════════════════════════════
                    IMPORTANT DISCLAIMERS
═══════════════════════════════════════════════════════════════════

MEDICAL DISCLAIMER:
This AI-generated report is for informational and educational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical decisions and concerns.

EMERGENCY GUIDANCE:
If you experience severe symptoms, difficulty breathing, chest pain, or other emergency conditions, seek immediate medical attention by calling emergency services.

ACCURACY CONSIDERATIONS:
• Analysis accuracy depends on completeness of provided information
• Some conditions may require physical examination for proper diagnosis
• Follow-up testing may be necessary for definitive diagnosis
• Second opinions are recommended for complex medical cases

═══════════════════════════════════════════════════════════════════
Report generated by AI Medical Analysis System
Session: {session_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════════
"""

    # Export functionality (only called from API endpoint)
    async def generate_export_file(self, state: dict, format: str, include_details: bool = True) -> bytes:
        """Generate PDF or Word export file (separate from main workflow)"""
        
        if format == 'pdf':
            return await self._generate_pdf_export(state, include_details)
        elif format == 'word':
            return await self._generate_word_export(state, include_details)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def _generate_pdf_export(self, state: dict, include_details: bool) -> bytes:
        """Generate PDF using reportlab (simplified version)"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, 
                               topMargin=72, bottomMargin=18)
            styles = getSampleStyleSheet()
            story = []
            
            # Add content
            overall_analysis = state.get('overall_analysis', {})
            medical_report = state.get('medical_report', '')
            
            # Title
            story.append(Paragraph("Medical Analysis Report", styles['Title']))
            story.append(Spacer(1, 12))
            
            # Diagnosis
            story.append(Paragraph("Primary Diagnosis", styles['Heading2']))
            story.append(Paragraph(f"<b>Condition:</b> {overall_analysis.get('final_diagnosis', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"<b>Confidence Level:</b> {(overall_analysis.get('final_confidence', 0) * 100):.1f}%", styles['Normal']))
            story.append(Paragraph(f"<b>Severity:</b> {overall_analysis.get('final_severity', 'N/A').title()}", styles['Normal']))
            story.append(Paragraph(f"<b>Recommended Specialist:</b> {overall_analysis.get('specialist_recommendation', 'General Practitioner').replace('_', ' ').title()}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # User explanation
            if overall_analysis.get('user_explanation'):
                story.append(Paragraph("What is it?", styles['Heading2']))
                story.append(Paragraph(overall_analysis.get('user_explanation'), styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Clinical reasoning if details included
            if include_details and overall_analysis.get('clinical_reasoning'):
                story.append(Paragraph("Clinical Reasoning", styles['Heading2']))
                story.append(Paragraph(overall_analysis.get('clinical_reasoning'), styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Full report if available and details included
            if include_details and medical_report:
                story.append(Paragraph("Detailed Medical Report", styles['Heading2']))
                # Split long text into paragraphs
                for paragraph in medical_report.split('\n\n'):
                    if paragraph.strip():
                        story.append(Paragraph(paragraph.strip(), styles['Normal']))
                        story.append(Spacer(1, 6))
            
            # Disclaimer
            story.append(Spacer(1, 24))
            story.append(Paragraph("Medical Disclaimer", styles['Heading3']))
            disclaimer_text = ("This AI-generated report is for informational purposes only and should not replace "
                            "professional medical advice, diagnosis, or treatment. Always consult with qualified "
                            "healthcare professionals for medical concerns.")
            story.append(Paragraph(disclaimer_text, styles['Normal']))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}")
            # Fallback to text
            return self._generate_text_export(state, include_details).encode('utf-8')
    
    async def _generate_word_export(self, state: Dict[str, Any], include_details: bool) -> bytes:
        """Generate Word document using python-docx (simplified version)"""
        try:
            doc = Document()
        
            # Add content
            overall_analysis = state.get('overall_analysis', {})
            medical_report = state.get('medical_report', '')
            
            # Title
            title = doc.add_heading('Medical Analysis Report', 0)
            title.alignment = 1  # Center alignment
            
            # Header info
            doc.add_paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
            doc.add_paragraph("")  # Empty line
            
            # Diagnosis section
            doc.add_heading('Primary Diagnosis', level=1)
            
            # Create a table for diagnosis info
            table = doc.add_table(rows=4, cols=2)
            table.style = 'Table Grid'
            
            # Fill table
            cells = table.rows[0].cells
            cells[0].text = 'Condition'
            cells[1].text = overall_analysis.get('final_diagnosis', 'N/A')
            
            cells = table.rows[1].cells
            cells[0].text = 'Confidence Level'
            cells[1].text = f"{(overall_analysis.get('final_confidence', 0) * 100):.1f}%"
            
            cells = table.rows[2].cells
            cells[0].text = 'Severity'
            cells[1].text = overall_analysis.get('final_severity', 'N/A').title()
            
            cells = table.rows[3].cells
            cells[0].text = 'Recommended Specialist'
            cells[1].text = overall_analysis.get('specialist_recommendation', 'General Practitioner').replace('_', ' ').title()
            
            doc.add_paragraph("")  # Empty line
            
            # User explanation
            if overall_analysis.get('user_explanation'):
                doc.add_heading('What is it?', level=1)
                doc.add_paragraph(overall_analysis.get('user_explanation'))
            
            # Clinical reasoning if details included
            if include_details and overall_analysis.get('clinical_reasoning'):
                doc.add_heading('Clinical Reasoning', level=1)
                doc.add_paragraph(overall_analysis.get('clinical_reasoning'))
            
            # Full report if available and details included
            if include_details and medical_report:
                doc.add_heading('Detailed Medical Report', level=1)
                doc.add_paragraph(medical_report)
            
            # Disclaimer
            doc.add_heading('Medical Disclaimer', level=2)
            disclaimer_text = ("This AI-generated report is for informational purposes only and should not replace "
                            "professional medical advice, diagnosis, or treatment. Always consult with qualified "
                            "healthcare professionals for medical concerns.")
            doc.add_paragraph(disclaimer_text)
            
            # Save to buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Word generation failed: {e}")
            # Fallback to text
            return self._generate_text_export(state, include_details).encode('utf-8')