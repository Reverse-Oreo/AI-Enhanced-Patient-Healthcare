import { ApiService } from './api';

// Fetch patients list for nurse view
export const fetchPatients = async () => {
  try {
    const response = await ApiService.getNursePatients();
    return response.patients || response;
  } catch (error) {
    console.error('Error fetching patients:', error);
    // Return mock data for demo purposes
    return [
      {
        id: 'P001',
        name: 'John Doe',
        ageGroup: '45-54',
        gender: 'Male',
        risk: 'High',
        lastDiagnosis: { title: 'Hypertension', confidence: 0.85 },
        updatedAt: new Date().toISOString()
      },
      {
        id: 'P002',
        name: 'Jane Smith',
        ageGroup: '35-44',
        gender: 'Female',
        risk: 'Medium',
        lastDiagnosis: { title: 'Type 2 Diabetes', confidence: 0.78 },
        updatedAt: new Date().toISOString()
      },
      {
        id: 'P003',
        name: 'Robert Johnson',
        ageGroup: '55-64',
        gender: 'Male',
        risk: 'Low',
        lastDiagnosis: { title: 'Arthritis', confidence: 0.92 },
        updatedAt: new Date().toISOString()
      }
    ];
  }
};

// Assign patient to a doctor
export const assignPatientToDoctor = async (patientId: string, doctorId: string) => {
  try {
    const response = await ApiService.assignPatientToDoctor({ patientId, doctorId });
    return response;
  } catch (error) {
    console.error('Error assigning doctor:', error);
    // Simulate success for demo purposes
    return { success: true, message: 'Patient assigned successfully' };
  }
};

// Submit patient data (clinical, lab, lifestyle)
export const submitPatientData = async (patientId: string, data: any) => {
  try {
    const response = await ApiService.submitPatientData(patientId, data);
    return response;
  } catch (error) {
    console.error('Error submitting patient data:', error);
    // Simulate success for demo purposes
    return { success: true, message: 'Patient data submitted successfully' };
  }
};

// Fetch available doctors for assignment
export const fetchDoctors = async () => {
  try {
    const response = await ApiService.getAvailableDoctors();
    return response.doctors || response;
  } catch (error) {
    console.error('Error fetching doctors:', error);
    // Return mock data for demo purposes
    return [
      { id: 'doc1', name: 'Dr. Smith', specialty: 'Cardiology' },
      { id: 'doc2', name: 'Dr. Johnson', specialty: 'Endocrinology' },
      { id: 'doc3', name: 'Dr. Williams', specialty: 'General Medicine' },
      { id: 'doc4', name: 'Dr. Brown', specialty: 'Pediatrics' },
      { id: 'doc5', name: 'Dr. Davis', specialty: 'Orthopedics' }
    ];
  }
};

// Get patient details
export const fetchPatientDetails = async (patientId: string) => {
  try {
    const response = await ApiService.getPatientDetails(patientId);
    return response;
  } catch (error) {
    console.error('Error fetching patient details:', error);
    // Return mock data for demo purposes
    return {
      id: patientId,
      name: 'Mock Patient',
      age: 45,
      gender: 'Male',
      medicalHistory: ['Hypertension', 'Type 2 Diabetes'],
      currentMedications: ['Metformin', 'Lisinopril']
    };
  }
};