// src/services/nurse.ts
import { supabase } from '../lib/supabase'

export async function fetchPatients() {
  const { data, error } = await supabase
    .from('user_profiles')
    .select('id, name, age, gender, updated_at')
    .order('updated_at', { ascending: false })
  if (error) throw error

  return (data ?? []).map(p => ({
    id: p.id,
    name: p.name ?? '—',
    ageGroup: p.age ?? '—',
    gender: p.gender ?? '—',
    risk: 'Unknown',           // can be enriched later from medical_reports
    lastDiagnosis: null,       // ^ same
    updatedAt: p.updated_at ?? new Date().toISOString(),
  }))
}

export async function listDoctors() {
  const { data, error } = await supabase
    .from('doctor_profile')
    .select('doctor_id, full_name')
    .order('full_name', { ascending: true })
  if (error) throw error
  return (data ?? []).map(d => ({ id: d.doctor_id, name: d.full_name }))
}

export async function assignPatientToDoctor(patientId: string, doctorId: string) {
  // make previous links inactive
  const { error: deactErr } = await supabase
    .from('patient_doctor_assignment')
    .update({ active: false })
    .eq('patient_id', patientId)
    .eq('active', true)
  if (deactErr) throw deactErr

  // create new active link
  const { error } = await supabase.from('patient_doctor_assignment').insert({
    patient_id: patientId,
    doctor_id: doctorId,
    assignment_type: 'primary',
    assigned_at: new Date().toISOString(),
    active: true,
  })
  if (error) throw error
}

// optional: store nurse-entered data
export async function submitPatientData(
  patientId: string,
  { clinicalData, labData, lifestyleData }: { clinicalData?: any; labData?: any; lifestyleData?: any }
) {
  if (clinicalData) {
    const { error } = await supabase.from('clinical_data').insert({
      user_id: patientId,
      blood_pressure: clinicalData.bloodPressure ?? null,
      heart_rate: clinicalData.heartRate ?? null,
      temperature: clinicalData.temperature ?? null,
      // map more fields as you like (bmi, symptoms, etc.)
    })
    if (error) throw error
  }
  if (labData) {
    const { error } = await supabase.from('lab_data').insert({
      user_id: patientId,
      // e.g. hba1c, fasting_blood_sugar, etc.
    })
    if (error) throw error
  }
  if (lifestyleData) {
    const { error } = await supabase.from('lifestyle_data').insert({
      user_id: patientId,
      // e.g. smoking_status, exercise_frequency, sleep_hours, etc.
    })
    if (error) throw error
  }
}
