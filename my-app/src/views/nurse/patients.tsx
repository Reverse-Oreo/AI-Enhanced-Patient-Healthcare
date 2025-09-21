import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import { fetchPatients, assignPatientToDoctor, submitPatientData } from 'services/nurse';
import { useAuth } from 'contexts/AuthContext';

const Wrap = styled.div`max-width:1320px; margin:0 auto; padding:24px;`;
const Controls = styled.div`display:flex; gap:12px; margin:8px 0 16px; flex-wrap:wrap;`;
const Table = styled.table`
  width:100%;
  border-collapse:separate;
  border-spacing:0 10px;
  table-layout: fixed;

  th, td { padding:14px 16px; background:#fff; }
  th { font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
  tr td:first-child, tr th:first-child { border-top-left-radius:12px; border-bottom-left-radius:12px; }
  tr td:last-child,  tr th:last-child  { border-top-right-radius:12px; border-bottom-right-radius:12px; }

  .right  { text-align:right;  font-variant-numeric: tabular-nums; }
  .center { text-align:center; }
  .nowrap { white-space:nowrap; }
`;

// Modal styles for data input
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  min-height: 80px;
`;

const Button = styled.button`
  padding: 8px 16px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  
  &:hover {
    background-color: #2563eb;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 16px;
`;

type RiskLevel = 'High' | 'Medium' | 'Low' | 'Unknown';

const Risk = styled.span<{ level?: RiskLevel }>`
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1.2;
  ${({ level }) => {
    switch (level) {
      case 'High':
        return 'background:#fee2e2;color:#b91c1c;';
      case 'Medium':
        return 'background:#fff7ed;color:#9a3412;';
      case 'Low':
        return 'background:#e6f4ff;color:#1d4ed8;';
      default:
        return 'background:#e5e7eb;color:#374151;';
    }
  }}
`;

// Data input types
interface ClinicalData {
  bloodPressure: string;
  heartRate: number;
  temperature: number;
  respiratoryRate: number;
  oxygenSaturation: number;
  symptoms: string;
  notes: string;
}

interface LabData {
  testType: string;
  result: string;
  units: string;
  referenceRange: string;
}

interface LifestyleData {
  diet: string;
  exercise: string;
  sleep: string;
  alcohol: string;
  smoking: string;
}

export default function NursePatients() {
  const { loggedIn } = useAuth();
  const [rows, setRows] = useState<any[]>([]);
  const [q, setQ] = useState('');
  const [risk, setRisk] = useState<'All'|'High'|'Medium'|'Low'>('All');
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [showDataModal, setShowDataModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [clinicalData, setClinicalData] = useState<ClinicalData>({
    bloodPressure: '',
    heartRate: 0,
    temperature: 0,
    respiratoryRate: 0,
    oxygenSaturation: 0,
    symptoms: '',
    notes: ''
  });
  const [labData, setLabData] = useState<LabData>({
    testType: '',
    result: '',
    units: '',
    referenceRange: ''
  });
  const [lifestyleData, setLifestyleData] = useState<LifestyleData>({
    diet: '',
    exercise: '',
    sleep: '',
    alcohol: '',
    smoking: ''
  });

  useEffect(() => { 
    fetchPatients().then(setRows).catch(console.error);
    // In a real app, we would fetch the list of available doctors
    setDoctors([
      { id: 'doc1', name: 'Dr. Smith' },
      { id: 'doc2', name: 'Dr. Johnson' },
      { id: 'doc3', name: 'Dr. Williams' }
    ]);
  }, []);

  const filtered = rows.filter(r =>
    (risk==='All' || r.risk===risk) &&
    (r.name.toLowerCase().includes(q.toLowerCase()) || r.id.toLowerCase().includes(q.toLowerCase()))
  );

  const handleOpenDataInput = (patient: any) => {
    setSelectedPatient(patient);
    setShowDataModal(true);
  };

  const handleOpenAssignDoctor = (patient: any) => {
    setSelectedPatient(patient);
    setShowAssignModal(true);
  };

  const handleSubmitData = async () => {
    try {
      await submitPatientData(selectedPatient.id, {
        clinicalData,
        labData,
        lifestyleData
      });
      setShowDataModal(false);
      // Reset form
      setClinicalData({
        bloodPressure: '',
        heartRate: 0,
        temperature: 0,
        respiratoryRate: 0,
        oxygenSaturation: 0,
        symptoms: '',
        notes: ''
      });
      setLabData({
        testType: '',
        result: '',
        units: '',
        referenceRange: ''
      });
      setLifestyleData({
        diet: '',
        exercise: '',
        sleep: '',
        alcohol: '',
        smoking: ''
      });
      alert('Data submitted successfully!');
    } catch (error) {
      console.error('Failed to submit data:', error);
      alert('Failed to submit data. Please try again.');
    }
  };

  const handleAssignDoctor = async () => {
    try {
      await assignPatientToDoctor(selectedPatient.id, selectedDoctor);
      setShowAssignModal(false);
      setSelectedDoctor('');
      alert('Patient assigned successfully!');
    } catch (error) {
      console.error('Failed to assign doctor:', error);
      alert('Failed to assign doctor. Please try again.');
    }
  };

  return (
    <>
      <Navbar />
      <Wrap>
        <h1 style={{margin:'0 0 10px'}}>Patients - Nurse View</h1>

        <Controls>
          <input placeholder="Search name or ID…" value={q} onChange={e=>setQ(e.target.value)} />
          <select value={risk} onChange={e=>setRisk(e.target.value as any)}>
            <option>All</option><option>High</option><option>Medium</option><option>Low</option>
          </select>
        </Controls>

        <Table>
            <colgroup>
            <col style={{ width: '25%' }} />  {/* Patient */}
            <col style={{ width: '20%' }} />  {/* Last Diagnosis */}
            <col style={{ width: '10%' }} />  {/* Confidence */}
            <col style={{ width: '10%' }} />  {/* Risk */}
            <col style={{ width: '12%' }} />  {/* Updated */}
            <col style={{ width: '23%'  }} />  {/* Actions - wider for nurse */}
            </colgroup>

            <thead>
                <tr>
                <th>Patient</th>
                <th>Last Diagnosis</th>
                <th className="right">Confidence</th>
                <th className="center">Risk</th>
                <th className="right">Updated</th>
                <th className="nowrap">Actions</th>
                </tr>
            </thead>

            <tbody>
                {filtered.map(p => (
                <tr key={p.id}>
                    <td>
                    <strong>{p.name}</strong>
                    <div style={{color:'#6b7280',fontSize:12}}>
                        ID: {p.id} • {p.ageGroup} • {p.gender}
                    </div>
                    </td>
                    <td>{p.lastDiagnosis?.title || '—'}</td>
                    <td className="right">
                    {p.lastDiagnosis ? Math.round(p.lastDiagnosis.confidence*100)+'%' : '—'}
                    </td>
                    <td className="center"><Risk level={p.risk}>{p.risk}</Risk></td>
                    <td className="right">{new Date(p.updatedAt).toLocaleDateString()}</td>
                    <td className="nowrap">
                      <Button onClick={() => handleOpenDataInput(p)} style={{marginRight: '8px'}}>
                        Input Data
                      </Button>
                      <Button onClick={() => handleOpenAssignDoctor(p)}>
                        Assign Doctor
                      </Button>
                    </td>
                </tr>
                ))}
            </tbody>
        </Table>

        {/* Data Input Modal */}
        {showDataModal && (
          <ModalOverlay onClick={() => setShowDataModal(false)}>
            <ModalContent onClick={e => e.stopPropagation()}>
              <h2>Input Data for {selectedPatient?.name}</h2>
              
              <h3>Clinical Data</h3>
              <FormGroup>
                <Label>Blood Pressure</Label>
                <Input 
                  type="text" 
                  placeholder="120/80" 
                  value={clinicalData.bloodPressure}
                  onChange={e => setClinicalData({...clinicalData, bloodPressure: e.target.value})}
                />
              </FormGroup>
              <FormGroup>
                <Label>Heart Rate (bpm)</Label>
                <Input 
                  type="number" 
                  value={clinicalData.heartRate}
                  onChange={e => setClinicalData({...clinicalData, heartRate: Number(e.target.value)})}
                />
              </FormGroup>
              <FormGroup>
                <Label>Temperature (°C)</Label>
                <Input 
                  type="number" 
                  step="0.1"
                  value={clinicalData.temperature}
                  onChange={e => setClinicalData({...clinicalData, temperature: Number(e.target.value)})}
                />
              </FormGroup>
              <FormGroup>
                <Label>Respiratory Rate (breaths/min)</Label>
                <Input 
                  type="number" 
                  value={clinicalData.respiratoryRate}
                  onChange={e => setClinicalData({...clinicalData, respiratoryRate: Number(e.target.value)})}
                />
              </FormGroup>
              <FormGroup>
                <Label>Oxygen Saturation (%)</Label>
                <Input 
                  type="number" 
                  value={clinicalData.oxygenSaturation}
                  onChange={e => setClinicalData({...clinicalData, oxygenSaturation: Number(e.target.value)})}
                />
              </FormGroup>
              <FormGroup>
                <Label>Symptoms</Label>
                <TextArea 
                  value={clinicalData.symptoms}
                  onChange={e => setClinicalData({...clinicalData, symptoms: e.target.value})}
                  placeholder="Describe patient symptoms"
                />
              </FormGroup>
              <FormGroup>
                <Label>Notes</Label>
                <TextArea 
                  value={clinicalData.notes}
                  onChange={e => setClinicalData({...clinicalData, notes: e.target.value})}
                  placeholder="Additional clinical notes"
                />
              </FormGroup>

              <h3>Lab Data</h3>
              <FormGroup>
                <Label>Test Type</Label>
                <Input 
                  type="text" 
                  value={labData.testType}
                  onChange={e => setLabData({...labData, testType: e.target.value})}
                  placeholder="e.g., Blood Glucose, Cholesterol"
                />
              </FormGroup>
              <FormGroup>
                <Label>Result</Label>
                <Input 
                  type="text" 
                  value={labData.result}
                  onChange={e => setLabData({...labData, result: e.target.value})}
                />
              </FormGroup>
              <FormGroup>
                <Label>Units</Label>
                <Input 
                  type="text" 
                  value={labData.units}
                  onChange={e => setLabData({...labData, units: e.target.value})}
                  placeholder="e.g., mg/dL, mmol/L"
                />
              </FormGroup>
              <FormGroup>
                <Label>Reference Range</Label>
                <Input 
                  type="text" 
                  value={labData.referenceRange}
                  onChange={e => setLabData({...labData, referenceRange: e.target.value})}
                  placeholder="e.g., 70-100 mg/dL"
                />
              </FormGroup>

              <h3>Lifestyle Data</h3>
              <FormGroup>
                <Label>Diet</Label>
                <TextArea 
                  value={lifestyleData.diet}
                  onChange={e => setLifestyleData({...lifestyleData, diet: e.target.value})}
                  placeholder="Describe patient's diet habits"
                />
              </FormGroup>
              <FormGroup>
                <Label>Exercise</Label>
                <TextArea 
                  value={lifestyleData.exercise}
                  onChange={e => setLifestyleData({...lifestyleData, exercise: e.target.value})}
                  placeholder="Describe patient's exercise routine"
                />
              </FormGroup>
              <FormGroup>
                <Label>Sleep</Label>
                <TextArea 
                  value={lifestyleData.sleep}
                  onChange={e => setLifestyleData({...lifestyleData, sleep: e.target.value})}
                  placeholder="Describe patient's sleep patterns"
                />
              </FormGroup>
              <FormGroup>
                <Label>Alcohol Consumption</Label>
                <TextArea 
                  value={lifestyleData.alcohol}
                  onChange={e => setLifestyleData({...lifestyleData, alcohol: e.target.value})}
                  placeholder="Describe patient's alcohol consumption"
                />
              </FormGroup>
              <FormGroup>
                <Label>Smoking</Label>
                <TextArea 
                  value={lifestyleData.smoking}
                  onChange={e => setLifestyleData({...lifestyleData, smoking: e.target.value})}
                  placeholder="Describe patient's smoking habits"
                />
              </FormGroup>

              <ButtonGroup>
                <Button onClick={handleSubmitData}>Submit Data</Button>
                <Button onClick={() => setShowDataModal(false)} style={{backgroundColor: '#6b7280'}}>
                  Cancel
                </Button>
              </ButtonGroup>
            </ModalContent>
          </ModalOverlay>
        )}

        {/* Assign Doctor Modal */}
        {showAssignModal && (
          <ModalOverlay onClick={() => setShowAssignModal(false)}>
            <ModalContent onClick={e => e.stopPropagation()}>
              <h2>Assign Doctor to {selectedPatient?.name}</h2>
              <FormGroup>
                <Label>Select Doctor</Label>
                <Select 
                  value={selectedDoctor} 
                  onChange={e => setSelectedDoctor(e.target.value)}
                >
                  <option value="">Select a doctor</option>
                  {doctors.map(doctor => (
                    <option key={doctor.id} value={doctor.id}>
                      {doctor.name}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              <ButtonGroup>
                <Button onClick={handleAssignDoctor} disabled={!selectedDoctor}>
                  Assign Doctor
                </Button>
                <Button onClick={() => setShowAssignModal(false)} style={{backgroundColor: '#6b7280'}}>
                  Cancel
                </Button>
              </ButtonGroup>
            </ModalContent>
          </ModalOverlay>
        )}
      </Wrap>
    </>
  );
}