import { BYPASS } from 'utils/bypass';

export async function fetchPatients(): Promise<any[]> {
  try {
    const r = await fetch('/api/clinician/patients'); // adjust when backend ready
    if (!r.ok) throw new Error('bad response');
    return await r.json();
    } catch (err) {
    if (BYPASS) return demoPatients(); // local mock
    throw err instanceof Error ? err : new Error('Failed to fetch patients');
    }
}

function demoPatients() {
  // derive a few “patients” from existing report shape you used on profile
  return [
    {
      id: 'P-1001',
      name: 'Alex Tan',
      ageGroup: '18–25',
      gender: 'Female',
      lastDiagnosis: {
        title: 'Flu',
        confidence: 0.82,
        createdAt: new Date().toISOString(),
        symptoms: ['cough','fever','sore throat'],
      },
      updatedAt: new Date().toISOString(),
    },
    {
      id: 'P-1002',
      name: 'Jordan Lim',
      ageGroup: '26–35',
      gender: 'Male',
      lastDiagnosis: {
        title: 'Chest pain (unspecified)',
        confidence: 0.48,
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        symptoms: ['chest pain','shortness of breath'],
      },
      updatedAt: new Date(Date.now() - 86400000).toISOString(),
    },
  ].map(p => ({ ...p, risk: computeRisk(p.lastDiagnosis) as any }));
}

export function computeRisk(
  d?: { confidence: number; symptoms: string[] }
): 'High'|'Medium'|'Low' {
  if (!d) return 'Low';
  const redFlags = ['chest pain','shortness of breath','fainting','severe headache','high fever'];
  const hasRedFlag = d.symptoms?.some(s => redFlags.includes(s.toLowerCase()));
  if (d.confidence < 0.55 || hasRedFlag) return 'High';
  if (d.confidence < 0.75) return 'Medium';
  return 'Low';
}
