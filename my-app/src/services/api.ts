if (!process.env.REACT_APP_API_URL) {
  throw new Error('REACT_APP_API_URL environment variable is required but not set during build');
}

const API_BASE_URL = process.env.REACT_APP_API_URL;
console.log('🔗 API Service using:', API_BASE_URL);

export interface DiagnosisRequest {
  symptoms: string;
  image?: File;
  location?: { lat: number; lng: number };
}

// Nurse-specific interfaces
export interface ClinicalData {
  bloodPressure: string;
  heartRate: number;
  temperature: number;
  respiratoryRate: number;
  oxygenSaturation: number;
  symptoms: string;
  notes: string;
}

export interface LabData {
  testType: string;
  result: string;
  units: string;
  referenceRange: string;
}

export interface LifestyleData {
  diet: string;
  exercise: string;
  sleep: string;
  alcohol: string;
  smoking: string;
}

export interface PatientDataSubmission {
  clinicalData: ClinicalData;
  labData: LabData;
  lifestyleData: LifestyleData;
}

export interface DoctorAssignment {
  patientId: string;
  doctorId: string;
}

export class ApiService {
  
  // Test backend connection
  static async testConnection(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
      throw new Error(`Backend connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  // NURSE ENDPOINTS

  // Get patients list for nurse view
  static async getNursePatients(): Promise<any> {
    try {
      console.log('👥 Fetching nurse patients list');
      
      const response = await fetch(`${API_BASE_URL}/nurse/patients`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch patients: HTTP ${response.status} - ${errorText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('❌ Failed to fetch nurse patients:', error);
      throw error;
    }
  }

  // Get available doctors for assignment
  static async getAvailableDoctors(): Promise<any> {
    try {
      console.log('👨‍⚕️ Fetching available doctors');
      
      const response = await fetch(`${API_BASE_URL}/nurse/doctors`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch doctors: HTTP ${response.status} - ${errorText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('❌ Failed to fetch available doctors:', error);
      throw error;
    }
  }

  // Assign patient to doctor
  static async assignPatientToDoctor(assignment: DoctorAssignment): Promise<any> {
    try {
      console.log('📋 Assigning patient to doctor:', assignment);
      
      const response = await fetch(`${API_BASE_URL}/nurse/assign-doctor`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assignment),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Assignment failed: HTTP ${response.status} - ${errorText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('❌ Failed to assign patient to doctor:', error);
      throw error;
    }
  }

  // Submit patient data (clinical, lab, lifestyle)
  static async submitPatientData(patientId: string, data: PatientDataSubmission): Promise<any> {
    try {
      console.log('📊 Submitting patient data for:', patientId);
      
      const formData = new FormData();
      formData.append('patient_id', patientId);
      formData.append('clinical_data', JSON.stringify(data.clinicalData));
      formData.append('lab_data', JSON.stringify(data.labData));
      formData.append('lifestyle_data', JSON.stringify(data.lifestyleData));

      const response = await fetch(`${API_BASE_URL}/nurse/patient-data`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Data submission failed: HTTP ${response.status} - ${errorText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('❌ Failed to submit patient data:', error);
      throw error;
    }
  }

  // Get patient details for data input
  static async getPatientDetails(patientId: string): Promise<any> {
    try {
      console.log('📋 Fetching patient details:', patientId);
      
      const response = await fetch(`${API_BASE_URL}/nurse/patient/${patientId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch patient details: HTTP ${response.status} - ${errorText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('❌ Failed to fetch patient details:', error);
      throw error;
    }
  }

  // EXISTING PATIENT DIAGNOSIS ENDPOINTS (keep your original code)

  //NODE 1: textual analysis
  static async startTextualAnalysis(request: DiagnosisRequest): Promise<any> {
    try {
      const formData = new FormData();
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      formData.append('user_symptoms', request.symptoms);
      formData.append('session_id', sessionId);
      
      // Comprehensive debug logging
      const fullUrl = `${API_BASE_URL}/patient/textual_analysis`;
      console.log('🔍 DETAILED API CALL DEBUG:');
      console.log('  Full URL:', fullUrl);
      console.log('  API_BASE_URL:', API_BASE_URL);
      console.log('  Method: POST');
      console.log('  Symptoms (first 100 chars):', request.symptoms.substring(0, 100) + '...');
      console.log('  Session ID:', sessionId);
      console.log('  FormData entries:', Array.from(formData.entries()).map(([key, value]) => 
        [key, typeof value === 'string' ? value.substring(0, 50) + '...' : 'FILE']
      ));

      const response = await fetch(`${API_BASE_URL}/patient/textual_analysis`, {
        method: 'POST',
        body: formData
      });

      console.log('🔍 RESPONSE DEBUG:');
      console.log('  Status Code:', response.status);
      console.log('  Status Text:', response.statusText);
      console.log('  Response OK:', response.ok);
      console.log('  Response URL:', response.url);
      console.log('  Response Type:', response.type);
      console.log('  Response Headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Textual analysis failed: HTTP ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ Textual analysis completed:', result);
      
      return result;

    } catch (error) {
      console.error('❌ Textual analysis failed:', error);
      throw error;
    }
  }

  //NODE 2: Follow-up questions
  static async runFollowupQuestions(sessionId: string, previousState: any, responses?: Record<string, string>): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('previous_state', JSON.stringify(previousState));
      
      if (responses) {
        formData.append('followup_responses', JSON.stringify(responses));
      }

      console.log('📝 Running follow-up questions:', { sessionId, hasResponses: !!responses });

      const response = await fetch(`${API_BASE_URL}/patient/followup_questions`, {
        method: 'POST',
        body: formData
      });

      return await response.json();

    } catch (error) {
      console.error('❌ Follow-up questions failed:', error);
      throw error;
    }
  }

  //NODE 3: Image analysis
  static async runImageAnalysis(sessionId: string, previousState: any, image?: File): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('previous_state', JSON.stringify(previousState));
      
      if (image) {
        formData.append('image_file', image);
      }

      console.log('📸 Running image analysis:', { sessionId, hasImage: !!image });

      const response = await fetch(`${API_BASE_URL}/patient/image_analysis`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Image analysis failed: HTTP ${response.status} - ${errorText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('❌ Image analysis failed:', error);
      throw error;
    }
  }

  //NODE 4: Overall analysis
  static async runOverallAnalysis(sessionId: string, previousState: any): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('previous_state', JSON.stringify(previousState));

      console.log('🎯 Running overall analysis:', { sessionId });

      const response = await fetch(`${API_BASE_URL}/patient/overall_analysis`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Overall analysis failed: HTTP ${response.status} - ${errorText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('❌ Overall analysis failed:', error);
      throw error;
    }
  }

  //NODE Final: Medical report
  static async runMedicalReport(sessionId: string, previousState: any): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('previous_state', JSON.stringify(previousState));

      console.log('📄 Running medical report:', { sessionId });

      const response = await fetch(`${API_BASE_URL}/patient/medical_report`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Medical report failed: HTTP ${response.status} - ${errorText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('❌ Medical report failed:', error);
      throw error;
    }
  }
  
  //PDF/Word generation 
  static async exportMedicalReport(
    sessionId: string, 
    format: 'pdf' | 'word', 
    reportData: any,
    includeDetails: boolean = true
  ): Promise<Blob> {
    try {
      console.log(`📄 Exporting medical report as ${format.toUpperCase()}:`, { sessionId, format });

      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('format', format);
      formData.append('include_details', includeDetails.toString());
      formData.append('report_data', JSON.stringify(reportData));

      const response = await fetch(`${API_BASE_URL}/patient/export_report`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Export failed: HTTP ${response.status} - ${errorText}`);
      }

      return await response.blob();

    } catch (error) {
      console.error(`❌ ${format.toUpperCase()} export failed:`, error);
      throw error;
    }
  }
}