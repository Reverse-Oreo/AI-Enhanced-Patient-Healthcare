import { supabase } from '../lib/supabase';

export type PatientSummary = {
  id: string;
  name: string | null;
  age: string | null;
  gender: string | null;
  risk: 'High'|'Medium'|'Low'|'Unknown';
  lastReport?: { title?: string|null; date?: string|null; confidence?: number|null } | null;
  clinical?: {
    blood_pressure?: string|null;
    heart_rate?: number|null;
    temperature?: number|null;
    bmi?: number|null;
    diabetes?: boolean|null;
    hypertension?: boolean|null;
    heart_disease?: boolean|null;
    medications?: string|null;
    symptoms?: string|null;
    recorded_at?: string|null;
  } | null;
  labs?: {
    hba1c?: number|null;
    fasting_blood_sugar?: number|null;
    ldl?: number|null;
    hdl?: number|null;
    total_cholesterol?: number|null;
    hemoglobin?: number|null;
    creatinine?: number|null;
    alt?: number|null; ast?: number|null;
    recorded_at?: string|null;
  } | null;
  source: 'live'|'demo';
};

// ---- demo fallback (used when logged out or live fetch returns nothing)
const DEMO_PATIENT: PatientSummary = {
  id: 'P-1002',
  name: 'Jordan Lim',
  age: '26–35',
  gender: 'Male',
  risk: 'High',
  lastReport: { title: 'Chest pain (unspecified)', date: new Date().toISOString(), confidence: 0.48 },
  clinical: {
    blood_pressure: '165/102',
    heart_rate: 104,
    temperature: 38.4,
    bmi: 29.1,
    hypertension: true,
    medications: 'Amlodipine 5mg OD',
    symptoms: 'Intermittent chest pain on exertion',
    recorded_at: new Date().toISOString(),
    diabetes: null, heart_disease: null,
  },
  labs: {
    hba1c: 6.2,
    fasting_blood_sugar: 6.9,
    ldl: 165, hdl: 38, total_cholesterol: 240,
    hemoglobin: 13.9, creatinine: 1.1, alt: 21, ast: 22,
    recorded_at: new Date().toISOString(),
  },
  source: 'demo',
};

function scoreRisk(s: Partial<PatientSummary>): 'High'|'Medium'|'Low'|'Unknown' {
  const bp = s.clinical?.blood_pressure ?? '';
  const [sysStr, diaStr] = bp.split('/');
  const sys = parseInt(sysStr || '0', 10);
  const dia = parseInt(diaStr || '0', 10);
  const temp = s.clinical?.temperature ?? 0;
  const hba1c = s.labs?.hba1c ?? 0;

  if ((sys >= 180 || dia >= 120) || temp >= 39 || hba1c >= 9) return 'High';
  if ((sys >= 140 || dia >= 90)  || temp >= 38 || hba1c >= 7) return 'Medium';
  if (sys || dia || temp || hba1c) return 'Low';
  return 'Unknown';
}

/** Live fetch for one patient by `user_profiles.id` */
export async function fetchPatientSummaryLive(patientId: string): Promise<PatientSummary | null> {
  if (!patientId) return null;

  const { data: profile, error: pErr } = await supabase
    .from('user_profiles')
    .select('id,name,age,gender,updated_at')
    .eq('id', patientId)
    .maybeSingle();
  if (pErr || !profile) return null;

  const { data: clinical } = await supabase
    .from('clinical_data')
    .select('blood_pressure,heart_rate,temperature,bmi,diabetes,hypertension,heart_disease,medications,symptoms,recorded_at')
    .eq('user_id', patientId)
    .order('recorded_at', { ascending: false })
    .limit(1)
    .maybeSingle();

  const { data: labs } = await supabase
    .from('lab_data')
    .select('hba1c,fasting_blood_sugar,ldl,hdl,total_cholesterol,hemoglobin,creatinine,alt,ast,recorded_at')
    .eq('user_id', patientId)
    .order('recorded_at', { ascending: false })
    .limit(1)
    .maybeSingle();

  const { data: report } = await supabase
    .from('medical_reports')
    .select('report_title, report_date, confidence_scores')
    .eq('user_id', patientId)
    .order('report_date', { ascending: false })
    .limit(1)
    .maybeSingle();

  const summary: PatientSummary = {
    id: profile.id,
    name: profile.name ?? null,
    age: profile.age ?? null,
    gender: profile.gender ?? null,
    lastReport: report ? {
      title: report.report_title,
      date: report.report_date,
      confidence: report.confidence_scores?.overall ?? null
    } : null,
    clinical: clinical ?? null,
    labs: labs ?? null,
    risk: 'Unknown',
    source: 'live',
  };

  summary.risk = scoreRisk(summary);
  return summary;
}

/** Hybrid: live when possible, demo otherwise (useful when signed out). */
export async function fetchPatientSummaryHybrid(patientId?: string): Promise<PatientSummary> {
  if (patientId) {
    const live = await fetchPatientSummaryLive(patientId);
    if (live) return live;
  }
  return DEMO_PATIENT;
}
