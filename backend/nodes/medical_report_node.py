from adapters.local_model_adapter import LocalModelAdapter
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import re

class MedicalReportNode:
    def __init__(self, adapter: LocalModelAdapter):
        self.adapter = adapter
    
    async def __call__(self, state):
        print("📄 MEDICAL REPORT NODE CALLED!")
        
        # Set stage when node starts
        state["current_workflow_stage"] = "report_generation"
        
        state = await self.generate_medical_report(state)
        
        state["current_workflow_stage"] = "report_complete"
        
        return state
    
    async def generate_medical_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive medical report based on all available analysis data.
        Optimized for the new simplified overall analysis structure.
        """
        try:
            # Gather all analysis data with new structure
            report_data = self._compile_comprehensive_report_data(state)
            
            # Generate structured medical report
            medical_report = await self._generate_enhanced_structured_report(report_data)
            
            # Update state with the final report
            state["medical_report"] = medical_report
            
            print(f"✅ Medical report generated successfully")
            print(f"📄 Report type: {report_data['analysis_summary']['workflow_type']}")
            
        except Exception as e:
            print(f"❌ Medical report generation failed: {e}")
            # Handle report generation error with enhanced fallback
            state["medical_report"] = self._generate_enhanced_error_report(str(e), state)
            state["current_workflow_stage"] = "report_generation_error"
        
        return state
    
    def _compile_comprehensive_report_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Compile all available analysis data for report generation - updated for new structure"""
        
        # Get overall analysis (simplified structure)
        overall_analysis = state.get("overall_analysis", {})
        healthcare_recommendation = state.get("healthcare_recommendation", {})
        workflow_path = state.get("workflow_path", [])
        
        # Determine workflow type from path
        workflow_type = self._determine_workflow_type(workflow_path)
        
        # Get original input data
        original_symptoms = state.get("userInput_symptoms", "") or state.get("latest_user_message", "")
        skin_symptoms = state.get("userInput_skin_symptoms", "")
        
        report_data = {
            "session_id": state.get("session_id", f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "timestamp": datetime.now().isoformat(),
            
            # Enhanced primary diagnosis from overall analysis
            "primary_diagnosis": {
                "diagnosis": overall_analysis.get("final_diagnosis", "No diagnosis available"),
                "confidence": overall_analysis.get("final_confidence", 0.0),
                "severity": overall_analysis.get("final_severity", "unknown"),
                "reasoning": overall_analysis.get("reasoning", "No reasoning provided"),
                "specialist_recommendation": overall_analysis.get("specialist_recommendation", "general practitioner")
            },
            
            # Original symptom information
            "symptom_information": {
                "original_symptoms": original_symptoms,
                "skin_symptoms": skin_symptoms if skin_symptoms else None,
                "symptom_analysis_performed": bool(state.get("textual_analysis"))
            },
            
            # Follow-up information (enhanced)
            "followup_information": {
                "questions_asked": state.get("followup_questions", []),
                "responses_provided": state.get("followup_response", {}),
                "enhanced_symptoms": state.get("followup_qna", {}),
                "enhanced_analysis_performed": bool(state.get("followup_diagnosis")),
                "improved_confidence": self._calculate_confidence_improvement(state)
            },
            
            # Image analysis (if performed)
            "image_analysis": {
                "performed": bool(state.get("skin_lesion_analysis")),
                "results": state.get("skin_lesion_analysis", {}),
                "image_required": state.get("image_required", False)
            },
            
            # Enhanced healthcare recommendations
            "healthcare_recommendation": healthcare_recommendation,
            
            # Analysis summary
            "analysis_summary": {
                "workflow_type": workflow_type,
                "workflow_path": workflow_path,
                "stages_completed": self._get_enhanced_completed_stages(state),
                "total_confidence_final": overall_analysis.get("final_confidence", 0.0),
                "analysis_quality": self._assess_analysis_quality(state)
            },
            
            # Medical context
            "medical_context": {
                "emergency_status": self._assess_emergency_status(overall_analysis, healthcare_recommendation),
                "follow_up_urgency": healthcare_recommendation.get("appointment_urgency", "unknown"),
                "specialist_needed": bool(healthcare_recommendation.get("specialist_type")),
                "self_care_applicable": healthcare_recommendation.get("recommendation_type") == "self_care"
            }
        }
        
        return report_data
    
    def _determine_workflow_type(self, workflow_path: List[str]) -> str:
        """Determine the type of workflow that was completed"""
        
        if not workflow_path:
            return "basic_analysis"
        
        if workflow_path == ["textual_only"]:
            return "textual_analysis_only"
        elif workflow_path == ["textual_to_image"]:
            return "textual_and_image_analysis"
        elif "followup_only" in workflow_path:
            return "enhanced_textual_analysis"
        elif "followup_to_image" in workflow_path:
            return "comprehensive_analysis"
        else:
            return "custom_workflow"
    
    def _calculate_confidence_improvement(self, state: Dict[str, Any]) -> float:
        """Calculate confidence improvement from follow-up"""
        
        initial_analysis = state.get("textual_analysis", [])
        followup_analysis = state.get("followup_diagnosis", [])
        overall_analysis = state.get("overall_analysis", {})
        
        if not initial_analysis:
            return 0.0
        
        initial_confidence = initial_analysis[0].get("diagnosis_confidence", 0.0) if initial_analysis else 0.0
        final_confidence = overall_analysis.get("final_confidence", initial_confidence)
        
        return max(0.0, final_confidence - initial_confidence)
    
    def _assess_analysis_quality(self, state: Dict[str, Any]) -> str:
        """Assess the quality of the analysis performed"""
        
        overall_analysis = state.get("overall_analysis", {})
        confidence = overall_analysis.get("final_confidence", 0.0)
        workflow_path = state.get("workflow_path", [])
        
        # Quality based on confidence and completeness
        if confidence >= 0.8 and len(workflow_path) > 1:
            return "high_quality"
        elif confidence >= 0.6:
            return "good_quality"
        elif confidence >= 0.4:
            return "moderate_quality"
        else:
            return "low_quality"
    
    def _assess_emergency_status(self, overall_analysis: Dict, healthcare_rec: Dict) -> str:
        """Assess if this is an emergency situation"""
        
        severity = overall_analysis.get("final_severity", "").lower()
        recommendation_type = healthcare_rec.get("recommendation_type", "")
        
        if severity in ["critical", "emergency"] or recommendation_type == "emergency_care":
            return "emergency"
        elif severity == "severe":
            return "urgent"
        elif severity == "moderate":
            return "non_urgent"
        else:
            return "routine"
    
    def _get_enhanced_completed_stages(self, state: Dict[str, Any]) -> List[str]:
        """Get enhanced list of completed workflow stages"""
        
        completed = []
        
        if state.get("textual_analysis"):
            completed.append("initial_symptom_analysis")
        
        if state.get("followup_questions"):
            completed.append("follow_up_questioning")
            
        if state.get("followup_diagnosis"):
            completed.append("enhanced_symptom_analysis")
        
        if state.get("skin_lesion_analysis"):
            completed.append("image_analysis")
            
        if state.get("overall_analysis"):  
            completed.append("comprehensive_medical_analysis")
        
        if state.get("healthcare_recommendation"):
            completed.append("healthcare_recommendations")
        
        return completed
    
    async def _generate_enhanced_structured_report(self, report_data: Dict[str, Any]) -> str:
        """Generate an enhanced structured medical report using LLM"""
        
        try:
            # Create comprehensive prompt for report generation
            report_prompt = self._create_enhanced_report_prompt(report_data)
            
            # Generate the report using the LLM adapter
            raw_report = await self.adapter.generate_medical_report(report_prompt)
            
            # Format and structure the report
            structured_report = self._format_enhanced_report(raw_report, report_data)
            
            return structured_report
            
        except Exception as e:
            print(f"❌ LLM report generation failed: {e}")
            # Fallback to enhanced template-based report
            return self._generate_enhanced_template_report(report_data)
    
    def _create_enhanced_report_prompt(self, report_data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for medical report generation"""
        
        primary_dx = report_data["primary_diagnosis"]
        symptom_info = report_data["symptom_information"]
        followup_info = report_data["followup_information"]
        healthcare_rec = report_data["healthcare_recommendation"]
        analysis_summary = report_data["analysis_summary"]
        medical_context = report_data["medical_context"]
        
        prompt = f"""
        Generate a comprehensive, professional medical analysis report based on the following data:

        === PATIENT SESSION ===
        Session ID: {report_data['session_id']}
        Analysis Date: {report_data['timestamp']}
        Workflow Type: {analysis_summary['workflow_type']}
        Analysis Quality: {analysis_summary['analysis_quality']}

        === SYMPTOM PRESENTATION ===
        Primary Symptoms: {symptom_info['original_symptoms']}
        """
        
        if symptom_info.get('skin_symptoms'):
            prompt += f"Skin-Related Symptoms: {symptom_info['skin_symptoms']}\n"
        
        prompt += f"""
        === DIAGNOSTIC FINDINGS ===
        Final Diagnosis: {primary_dx['diagnosis']}
        Clinical Reasoning: {primary_dx['reasoning']}
        Diagnostic Confidence: {primary_dx['confidence']:.1%}
        Severity Assessment: {primary_dx['severity']}
        Recommended Specialist: {primary_dx['specialist_recommendation']}
        """
        
        # Add follow-up information if available
        if followup_info['enhanced_analysis_performed']:
            prompt += f"""
        === ENHANCED ANALYSIS ===
        Follow-up Questions Asked: {len(followup_info['questions_asked'])}
        Additional Information Gathered: Yes
        Confidence Improvement: +{followup_info['improved_confidence']:.1%}
        Enhanced Clinical Picture: Available
        """
        
        # Add image analysis if performed
        if report_data['image_analysis']['performed']:
            image_results = report_data['image_analysis']['results']
            prompt += f"""
        === IMAGE ANALYSIS ===
        Image Analysis Method: EfficientNet-B0 Skin Lesion Classification
        Image Diagnosis: {image_results.get('image_diagnosis', 'No diagnosis')}
        Image Confidence: {max(image_results.get('confidence_score', {}).values()) if image_results.get('confidence_score') else 0:.1%}
        Visual Assessment: Completed
        """
        
        # Add healthcare recommendations
        prompt += f"""
        === CLINICAL RECOMMENDATIONS ===
        Recommendation Type: {healthcare_rec.get('recommendation_type', 'Unknown')}
        Appointment Urgency: {healthcare_rec.get('appointment_urgency', 'Unknown')}
        Specialist Type: {healthcare_rec.get('specialist_type', 'N/A')}
        Emergency Status: {medical_context['emergency_status']}
        """
        
        if healthcare_rec.get('self_care_advice'):
            prompt += f"Self-Care Options: Available ({len(healthcare_rec['self_care_advice'])} recommendations)\n"
        
        if healthcare_rec.get('nearby_facilities'):
            prompt += f"Healthcare Facilities: {len(healthcare_rec['nearby_facilities'])} nearby options identified\n"
        
        prompt += f"""
        === ANALYSIS METADATA ===
        Stages Completed: {', '.join(analysis_summary['stages_completed'])}
        Workflow Path: {' → '.join(analysis_summary['workflow_path'])}
        
        Please generate a professional medical report with these sections:
        
        1. EXECUTIVE SUMMARY
           - Brief overview of case and key findings
           - Primary diagnosis and confidence level
           - Overall assessment and urgency
        
        2. CLINICAL PRESENTATION
           - Detailed symptom analysis
           - Patient-reported concerns
           - Clinical significance
        
        3. DIAGNOSTIC ASSESSMENT
           - Diagnostic reasoning and methodology
           - Confidence analysis and supporting evidence
           - Alternative diagnoses considered
           - Severity assessment and implications
        
        4. ANALYSIS METHODOLOGY
           - Workflow stages completed
           - Analysis techniques used (textual, image, follow-up)
           - Quality and completeness of assessment
        
        5. CLINICAL RECOMMENDATIONS
           - Immediate actions required
           - Specialist referrals and urgency
           - Self-care recommendations (if applicable)
           - Follow-up care plan
        
        6. HEALTHCARE RESOURCES
           - Recommended specialist type and rationale
           - Healthcare facility options (if available)
           - Insurance and cost considerations
        
        7. PATIENT GUIDANCE
           - Next steps and timeline
           - Warning signs to monitor
           - When to seek immediate care
        
        8. MEDICAL DISCLAIMERS
           - AI analysis limitations
           - Professional consultation requirements
           - Emergency care instructions
        
        Format the report professionally with clear headings and comprehensive medical language.
        Ensure all recommendations are evidence-based and clinically appropriate.
        """
        
        return prompt
    
    def _format_enhanced_report(self, raw_report: str, report_data: Dict[str, Any]) -> str:
        """Format the raw LLM output into a structured report with enhanced headers"""
        
        analysis_summary = report_data["analysis_summary"]
        medical_context = report_data["medical_context"]
        
        # Enhanced header with more metadata
        header = f"""
╔══════════════════════════════════════════════════════════════════╗
║                     MEDICAL ANALYSIS REPORT                     ║
╚══════════════════════════════════════════════════════════════════╝

Session ID: {report_data['session_id']}
Generated: {datetime.fromisoformat(report_data['timestamp']).strftime('%B %d, %Y at %I:%M %p')}
Analysis Type: {analysis_summary['workflow_type'].replace('_', ' ').title()}
Analysis Quality: {analysis_summary['analysis_quality'].replace('_', ' ').title()}
Emergency Status: {medical_context['emergency_status'].upper()}

Analysis Stages Completed:
{chr(10).join([f"  ✓ {stage.replace('_', ' ').title()}" for stage in analysis_summary['stages_completed']])}

"""
        
        # Clean and format the LLM output
        formatted_content = raw_report.strip()
        
        # Add enhanced footer with comprehensive disclaimers
        footer = f"""

╔══════════════════════════════════════════════════════════════════╗
║                       IMPORTANT DISCLAIMERS                     ║
╚══════════════════════════════════════════════════════════════════╝

🤖 AI-GENERATED ANALYSIS:
   • This report is generated by an AI medical analysis system
   • Confidence Level: {report_data['primary_diagnosis']['confidence']:.1%}
   • Analysis Quality: {analysis_summary['analysis_quality'].replace('_', ' ').title()}

⚕️  MEDICAL DISCLAIMERS:
   • This analysis is for informational and educational purposes only
   • NOT a substitute for professional medical advice, diagnosis, or treatment
   • Always consult qualified healthcare professionals for medical decisions
   • Individual cases may vary from AI analysis predictions

🚨 EMERGENCY GUIDANCE:
   • Emergency Status: {medical_context['emergency_status'].upper()}
   • If symptoms worsen or new concerning symptoms develop, seek immediate care
   • Call 911 for life-threatening emergencies
   • Contact your healthcare provider for urgent concerns

📋 ACCURACY CONSIDERATIONS:
   • Analysis accuracy depends on completeness of provided information
   • Some conditions may require physical examination for proper diagnosis
   • Follow-up testing may be necessary for definitive diagnosis
   • Second opinions are recommended for complex cases

📞 FOLLOW-UP REQUIREMENTS:
   • Urgency Level: {report_data['healthcare_recommendation'].get('appointment_urgency', 'unknown').replace('_', ' ').title()}
   • Specialist Recommendation: {report_data['primary_diagnosis']['specialist_recommendation']}
   • Continue monitoring symptoms as advised in recommendations

═══════════════════════════════════════════════════════════════════
Generated by Medical Analysis AI System | Version 2.0
Report ID: {report_data['session_id']} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════════
"""
        
        return header + formatted_content + footer
    
    def _generate_enhanced_template_report(self, report_data: Dict[str, Any]) -> str:
        """Generate an enhanced template-based report as fallback"""
        
        primary_dx = report_data["primary_diagnosis"]
        healthcare_rec = report_data["healthcare_recommendation"]
        analysis_summary = report_data["analysis_summary"]
        medical_context = report_data["medical_context"]
        
        template_report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                     MEDICAL ANALYSIS REPORT                     ║
╚══════════════════════════════════════════════════════════════════╝

Session ID: {report_data['session_id']}
Generated: {datetime.fromisoformat(report_data['timestamp']).strftime('%B %d, %Y at %I:%M %p')}
Analysis Type: {analysis_summary['workflow_type'].replace('_', ' ').title()}

═══════════════════════════════════════════════════════════════════
                           EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════════

Based on the comprehensive analysis of symptoms: "{report_data['symptom_information']['original_symptoms']}", 
our medical AI system has identified: {primary_dx['diagnosis']}

Emergency Status: {medical_context['emergency_status'].upper()}
Recommended Action: {healthcare_rec.get('recommendation_type', 'Consult healthcare provider').replace('_', ' ').title()}

═══════════════════════════════════════════════════════════════════
                         DIAGNOSTIC FINDINGS
═══════════════════════════════════════════════════════════════════

🔍 Primary Diagnosis: {primary_dx['diagnosis']}
📊 Confidence Level: {primary_dx['confidence']:.1%}
⚠️  Severity Assessment: {primary_dx['severity'].title()}
🧠 Clinical Reasoning: {primary_dx['reasoning']}
👨‍⚕️ Specialist Recommendation: {primary_dx['specialist_recommendation']}

═══════════════════════════════════════════════════════════════════
                        ANALYSIS PERFORMED
═══════════════════════════════════════════════════════════════════

Workflow Completed: {analysis_summary['workflow_type'].replace('_', ' ').title()}
Analysis Quality: {analysis_summary['analysis_quality'].replace('_', ' ').title()}

Stages Completed:
"""
        
        for stage in analysis_summary['stages_completed']:
            template_report += f"  ✓ {stage.replace('_', ' ').title()}\n"
        
        # Add follow-up details if available
        if report_data['followup_information']['enhanced_analysis_performed']:
            template_report += f"""
Enhanced Analysis Details:
  • Follow-up questions asked: {len(report_data['followup_information']['questions_asked'])}
  • Confidence improvement: +{report_data['followup_information']['improved_confidence']:.1%}
  • Additional clinical information gathered
"""
        
        # Add image analysis if available
        if report_data['image_analysis']['performed']:
            image_data = report_data['image_analysis']['results']
            template_report += f"""
Image Analysis Results:
  • Method: EfficientNet-B0 Skin Lesion Classification  
  • Image Diagnosis: {image_data.get('image_diagnosis', 'No diagnosis available')}
  • Visual assessment completed successfully
"""
        
        # Add recommendations
        template_report += f"""
═══════════════════════════════════════════════════════════════════
                       CLINICAL RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════

🎯 Recommended Action: {healthcare_rec.get('recommendation_type', 'Consult healthcare provider').replace('_', ' ').title()}
⏰ Appointment Urgency: {healthcare_rec.get('appointment_urgency', 'As needed').replace('_', ' ').title()}
"""
        
        if healthcare_rec.get('specialist_type'):
            template_report += f"🏥 Recommended Specialist: {healthcare_rec['specialist_type']}\n"
        
        if healthcare_rec.get('nearby_facilities'):
            template_report += f"📍 Nearby Healthcare Facilities: {len(healthcare_rec['nearby_facilities'])} options identified\n"
        
        if healthcare_rec.get('self_care_advice'):
            template_report += "\n💊 SELF-CARE RECOMMENDATIONS:\n"
            for advice in healthcare_rec['self_care_advice'][:5]:  # Limit to 5
                template_report += f"  • {advice}\n"
        
        if healthcare_rec.get('insurance_guidance'):
            template_report += "\n💳 INSURANCE GUIDANCE:\n"
            for guidance in healthcare_rec['insurance_guidance'][:3]:  # Limit to 3
                template_report += f"  • {guidance}\n"
        
        # Add enhanced footer
        template_report += f"""
═══════════════════════════════════════════════════════════════════
                           PATIENT GUIDANCE
═══════════════════════════════════════════════════════════════════

Next Steps:
  • Follow urgency timeline: {healthcare_rec.get('appointment_urgency', 'as advised').replace('_', ' ')}
  • Consult with recommended specialist: {primary_dx['specialist_recommendation']}
  • Monitor symptoms for any changes or worsening
  • Keep this report for healthcare provider reference

Warning Signs (seek immediate care if you experience):
  • Sudden worsening of symptoms
  • New concerning symptoms develop
  • Any emergency warning signs for your condition

╔══════════════════════════════════════════════════════════════════╗
║                       IMPORTANT DISCLAIMERS                     ║
╚══════════════════════════════════════════════════════════════════╝

• This is an AI-generated analysis for informational purposes only
• Not a substitute for professional medical advice, diagnosis, or treatment
• Consult qualified healthcare professionals for all medical decisions
• Seek immediate medical attention for emergency situations
• Analysis accuracy depends on completeness of provided information

═══════════════════════════════════════════════════════════════════
Generated by Medical Analysis AI System | Report ID: {report_data['session_id']}
═══════════════════════════════════════════════════════════════════
"""
        
        return template_report
    
    def _generate_enhanced_error_report(self, error_message: str, state: Dict[str, Any]) -> str:
        """Generate an enhanced error report when report generation fails"""
        
        # Try to extract any available information
        overall_analysis = state.get("overall_analysis", {})
        healthcare_rec = state.get("healthcare_recommendation", {})
        
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║                 MEDICAL ANALYSIS REPORT - ERROR                 ║
╚══════════════════════════════════════════════════════════════════╝

Session ID: {state.get('session_id', 'Unknown')}
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Status: Report Generation Error

═══════════════════════════════════════════════════════════════════
                         ERROR INFORMATION
═══════════════════════════════════════════════════════════════════

🚨 REPORT GENERATION ERROR:
   An error occurred while generating the comprehensive medical report.
   
   Error Details: {error_message}

═══════════════════════════════════════════════════════════════════
                      AVAILABLE INFORMATION
═══════════════════════════════════════════════════════════════════

{f'''
🔍 Diagnosis Information Available:
   • Diagnosis: {overall_analysis.get("final_diagnosis", "Not available")}
   • Confidence: {overall_analysis.get("final_confidence", 0.0):.1%}
   • Severity: {overall_analysis.get("final_severity", "Unknown")}
   • Specialist: {overall_analysis.get("specialist_recommendation", "Unknown")}
''' if overall_analysis else "No diagnostic information available"}

{f'''
🏥 Recommendation Information:
   • Action: {healthcare_rec.get("recommendation_type", "Unknown")}
   • Urgency: {healthcare_rec.get("appointment_urgency", "Unknown")}
   • Specialist: {healthcare_rec.get("specialist_type", "Unknown")}
''' if healthcare_rec else "No recommendation information available"}

═══════════════════════════════════════════════════════════════════
                           RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════

Due to the system error, we strongly recommend:

🎯 IMMEDIATE ACTIONS:
   • Consult with a healthcare professional for proper medical analysis
   • Provide them with your original symptoms and concerns
   • Do not rely on this incomplete analysis for medical decisions

⚕️  MEDICAL CONSULTATION:
   • Schedule an appointment with your primary care physician
   • Consider urgent care if symptoms are concerning
   • Seek emergency care if experiencing severe symptoms

╔══════════════════════════════════════════════════════════════════╗
║                       IMPORTANT DISCLAIMERS                     ║
╚══════════════════════════════════════════════════════════════════╝

• This system encountered an error during analysis
• No medical conclusions should be drawn from incomplete analysis
• Always consult qualified healthcare professionals for medical concerns
• Seek immediate medical attention for emergency situations
• This error report does not constitute medical advice

═══════════════════════════════════════════════════════════════════
System Error Report | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════════
"""