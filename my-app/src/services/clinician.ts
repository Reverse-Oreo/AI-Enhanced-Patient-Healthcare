// src/services/clinician.ts
import { supabase } from '../lib/supabase';

export type PatientRow = {
  id: string;
  name: string;
  gender?: string | null;
  ageGroup?: string | null;
  risk: 'High' | 'Medium' | 'Low' | 'Unknown';
  lastDiagnosis?: { title?: string | null; confidence?: number | null } | null;
  updatedAt?: string | null;
};

export const DEMO_PATIENTS: PatientRow[] = [
  {
    id: 'P-1001',
    name: 'Alex Tan',
    gender: 'Female',
    ageGroup: '18–25',
    risk: 'Medium',
    lastDiagnosis: { title: 'Flu', confidence: 0.82 },
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'P-1002',
    name: 'Jordan Lim',
    gender: 'Male',
    ageGroup: '26–35',
    risk: 'High',
    lastDiagnosis: { title: 'Chest pain (unspecified)', confidence: 0.48 },
    updatedAt: new Date(Date.now() - 864e5).toISOString(),
  },
  {
    id: 'P-1003',
    name: 'Maria Garcia',
    gender: 'Female',
    ageGroup: '45–54',
    risk: 'Low',
    lastDiagnosis: { title: 'Seasonal Allergies', confidence: 0.91 },
    updatedAt: new Date(Date.now() - 2 * 864e5).toISOString(),
  },
];

async function resolveDoctorId(): Promise<string | null> {
  const { data: auth } = await supabase.auth.getUser();
  const email = auth?.user?.email;
  if (!email) return null;

  const { data } = await supabase
    .from('doctor_profile')
    .select('doctor_id')
    .eq('email', email)
    .maybeSingle();

  return data?.doctor_id ?? null;
}

export async function fetchAssignedPatientsHybrid(): Promise<PatientRow[]> {
  // Try live, fall back to demo if anything goes wrong or nothing is found
  const doctorId = await resolveDoctorId();
  if (!doctorId) return DEMO_PATIENTS;

  const { data, error } = await supabase
    .from('patient_doctor_assignment')
    .select(`
      assignment_id,
      assigned_at,
      active,
      patient:user_profiles!patient_doctor_assignment_patient_id_fkey (
        id, name, age, gender, updated_at
      )
    `)
    .eq('doctor_id', doctorId)
    .eq('active', true);

  if (error) {
    console.error('fetchAssignedPatientsLive error', error);
    return DEMO_PATIENTS;
  }

  const rows: PatientRow[] = (data ?? [])
    .filter((r: any) => r.patient?.id)
    .map((r: any) => ({
      id: r.patient.id,
      name: r.patient.name ?? '—',
      gender: r.patient.gender ?? null,
      ageGroup: r.patient.age ?? null,
      risk: 'Unknown',                 // compute from vitals/labs if you want
      lastDiagnosis: null,
      updatedAt: r.patient.updated_at ?? null,
    }));

  return rows.length ? rows : DEMO_PATIENTS;
}
