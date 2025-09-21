import { supabase } from '../lib/supabase';

type Risk = 'High' | 'Medium' | 'Low' | 'Unknown';

export type PatientRow = {
  id: string;
  name: string;
  ageGroup?: string | null;
  gender?: string | null;
  risk: Risk;
  lastDiagnosis?: { title?: string; confidence?: number; createdAt?: string } | null;
  updatedAt?: string | null;
  source?: 'live' | 'demo';
};

// ---- demo data shown when logged out or live is empty
export const DEMO_PATIENTS: PatientRow[] = [
  {
    id: 'P-1001',
    name: 'Alex Tan',
    ageGroup: '18–25',
    gender: 'Female',
    risk: 'Medium',
    lastDiagnosis: { title: 'Flu', confidence: 0.82, createdAt: new Date().toISOString() },
    updatedAt: new Date().toISOString(),
    source: 'demo',
  },
  {
    id: 'P-1002',
    name: 'Jordan Lim',
    ageGroup: '26–35',
    gender: 'Male',
    risk: 'High',
    lastDiagnosis: { title: 'Chest pain (unspecified)', confidence: 0.48, createdAt: new Date(Date.now()-86400000).toISOString() },
    updatedAt: new Date(Date.now()-86400000).toISOString(),
    source: 'demo',
  },
  {
    id: 'P-1003',
    name: 'Maria Garcia',
    ageGroup: '45–54',
    gender: 'Female',
    risk: 'Low',
    lastDiagnosis: { title: 'Seasonal Allergies', confidence: 0.91, createdAt: new Date(Date.now()-172800000).toISOString() },
    updatedAt: new Date(Date.now()-172800000).toISOString(),
    source: 'demo',
  },
];

const demoDoctorId = process.env.REACT_APP_DEMO_DOCTOR_ID || '';
const showDemoWhenLoggedOut = (process.env.REACT_APP_SHOW_DEMO_WHEN_LOGGED_OUT ?? 'true') === 'true';
const includeDemoWhenLoggedIn = (process.env.REACT_APP_INCLUDE_DEMO_WHEN_LOGGED_IN ?? 'false') === 'true';

function dedupe(rows: PatientRow[]) {
  const m = new Map<string, PatientRow>();
  for (const r of rows) if (!m.has(r.id)) m.set(r.id, r);
  return Array.from(m.values()); // ← instead of [...m.values()]
}


async function resolveDoctorId(): Promise<string | null> {
  // If logged in, map auth email -> doctor_profile.doctor_id
  const { data: auth } = await supabase.auth.getUser();
  const email = auth?.user?.email ?? null;

  if (email) {
    const { data, error } = await supabase
      .from('doctor_profile')
      .select('doctor_id')
      .eq('email', email)
      .maybeSingle();
    if (!error && data?.doctor_id) return data.doctor_id as string;
  }
  // demo fallback
  return demoDoctorId || null;
}

async function fetchLive(): Promise<PatientRow[]> {
  const doctorId = await resolveDoctorId();
  if (!doctorId) return [];

  const { data, error } = await supabase
    .from('patient_doctor_assignment')
    .select(`
      patient:user_profiles (
        id, name, age, gender, updated_at
      )
    `)
    .eq('doctor_id', doctorId)
    .eq('active', true);

  if (error || !data) return [];

  return data.map((row: any) => {
    const p = row.patient;
    return {
      id: p.id,
      name: p.name ?? '—',
      ageGroup: p.age ?? null,
      gender: p.gender ?? null,
      risk: 'Unknown',
      lastDiagnosis: null,
      updatedAt: p.updated_at ?? null,
      source: 'live',
    } as PatientRow;
  });
}

/** Hybrid fetch: live if available; demo for logged-out/empty cases. */
export async function fetchAssignedPatientsHybrid(): Promise<PatientRow[]> {
  const { data: auth } = await supabase.auth.getUser();
  const live = await fetchLive();

  if (auth?.user) {
    // logged in
    return includeDemoWhenLoggedIn ? dedupe([...live, ...DEMO_PATIENTS]) : live;
  }
  // logged out
  if (showDemoWhenLoggedOut) return dedupe([...live, ...DEMO_PATIENTS]);
  return live;
}
