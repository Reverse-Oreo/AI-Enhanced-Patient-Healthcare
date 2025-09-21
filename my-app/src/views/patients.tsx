import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import { fetchPatients } from 'services/clinician';
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

// Dashboard components
const DashboardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
`;

const DashboardCard = styled.div`
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
`;

const CardTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #374151;
`;

const RiskPanel = styled(DashboardCard)`
  border-left: 4px solid #ef4444;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
`;

const StatItem = styled.div`
  text-align: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: #111827;
`;

const StatLabel = styled.div`
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
`;

// Modal styles for patient details
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
  max-width: 1000px;
  max-height: 80vh;
  overflow-y: auto;
`;

const TabContainer = styled.div`
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 20px;
`;

const Tab = styled.button<{ active: boolean }>`
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid ${props => props.active ? '#3b82f6' : 'transparent'};
  color: ${props => props.active ? '#3b82f6' : '#6b7280'};
  font-weight: ${props => props.active ? '600' : '400'};

  &:hover {
    color: #3b82f6;
  }
`;

const TabContent = styled.div`
  margin-top: 20px;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
`;

const InfoItem = styled.div`
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
`;

const InfoLabel = styled.div`
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
`;

const InfoValue = styled.div`
  font-size: 16px;
  color: #111827;
  font-weight: 500;
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

const SecondaryButton = styled(Button)`
  background-color: #6b7280;
  
  &:hover {
    background-color: #4b5563;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 20px;
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

// Mock data for demonstration
const mockHighRiskPatients = [
  { id: 'P001', name: 'John Doe', risk: 'High', condition: 'Hypertension Crisis', lastUpdate: '2 hours ago' },
  { id: 'P004', name: 'Sarah Wilson', risk: 'High', condition: 'Uncontrolled Diabetes', lastUpdate: '1 hour ago' }
];

const mockStats = {
  totalPatients: 124,
  highRisk: 8,
  mediumRisk: 23,
  lowRisk: 93
};

export default function DoctorPatients() {
  const { loggedIn, user } = useAuth();
  const [rows, setRows] = useState<any[]>([]);
  const [q, setQ] = useState('');
  const [risk, setRisk] = useState<'All'|'High'|'Medium'|'Low'>('All');
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [showPatientModal, setShowPatientModal] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => { 
    const loadPatients = async () => {
      try {
        setLoading(true);
        const patients = await fetchPatients();
        setRows(patients);
      } catch (error) {
        console.error('Failed to load patients:', error);
        // Fallback to demo data if API fails
        setRows([
          {
            id: 'P-1001',
            name: 'Alex Tan',
            ageGroup: '18–25',
            gender: 'Female',
            risk: 'Medium',
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
            risk: 'High',
            lastDiagnosis: {
              title: 'Chest pain (unspecified)',
              confidence: 0.48,
              createdAt: new Date(Date.now() - 86400000).toISOString(),
              symptoms: ['chest pain','shortness of breath'],
            },
            updatedAt: new Date(Date.now() - 86400000).toISOString(),
          },
          {
            id: 'P-1003',
            name: 'Maria Garcia',
            ageGroup: '45–54',
            gender: 'Female',
            risk: 'Low',
            lastDiagnosis: {
              title: 'Seasonal Allergies',
              confidence: 0.91,
              createdAt: new Date(Date.now() - 172800000).toISOString(),
              symptoms: ['sneezing','runny nose','itchy eyes'],
            },
            updatedAt: new Date(Date.now() - 172800000).toISOString(),
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadPatients();
  }, []);

  const filtered = rows.filter(r =>
    (risk==='All' || r.risk===risk) &&
    (r.name.toLowerCase().includes(q.toLowerCase()) || r.id.toLowerCase().includes(q.toLowerCase()))
  );

  const highRiskPatients = filtered.filter(p => p.risk === 'High');

  const handleOpenPatientChart = (patient: any) => {
    setSelectedPatient(patient);
    setShowPatientModal(true);
    setActiveTab('overview');
  };

  const renderPatientModal = () => {
    if (!selectedPatient) return null;

    return (
      <ModalOverlay onClick={() => setShowPatientModal(false)}>
        <ModalContent onClick={e => e.stopPropagation()}>
          <h2>{selectedPatient.name} - Patient Chart</h2>
          <p style={{ color: '#6b7280', marginBottom: '20px' }}>
            ID: {selectedPatient.id} • {selectedPatient.ageGroup} • {selectedPatient.gender}
          </p>

          <TabContainer>
            <Tab active={activeTab === 'overview'} onClick={() => setActiveTab('overview')}>
              Overview
            </Tab>
            <Tab active={activeTab === 'clinical'} onClick={() => setActiveTab('clinical')}>
              Clinical Data
            </Tab>
            <Tab active={activeTab === 'lab'} onClick={() => setActiveTab('lab')}>
              Lab Results
            </Tab>
            <Tab active={activeTab === 'treatment'} onClick={() => setActiveTab('treatment')}>
              Treatment Plan
            </Tab>
            <Tab active={activeTab === 'ai'} onClick={() => setActiveTab('ai')}>
              AI Insights
            </Tab>
          </TabContainer>

          <TabContent>
            {activeTab === 'overview' && (
              <div>
                <InfoGrid>
                  <InfoItem>
                    <InfoLabel>Risk Level</InfoLabel>
                    <InfoValue>
                      <Risk level={selectedPatient.risk}>{selectedPatient.risk}</Risk>
                    </InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>Last Diagnosis</InfoLabel>
                    <InfoValue>{selectedPatient.lastDiagnosis?.title || 'No diagnosis'}</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>Last Updated</InfoLabel>
                    <InfoValue>{new Date(selectedPatient.updatedAt).toLocaleDateString()}</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>Assigned Doctor</InfoLabel>
                    <InfoValue>Dr. {user?.name?.split(' ')[0] || 'Smith'}</InfoValue>
                  </InfoItem>
                </InfoGrid>

                <h4>Recent Vital Signs</h4>
                <InfoGrid>
                  <InfoItem>
                    <InfoLabel>Blood Pressure</InfoLabel>
                    <InfoValue>142/88 mmHg</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>Heart Rate</InfoLabel>
                    <InfoValue>78 bpm</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>Temperature</InfoLabel>
                    <InfoValue>37.1°C</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>Oxygen Saturation</InfoLabel>
                    <InfoValue>97%</InfoValue>
                  </InfoItem>
                </InfoGrid>
              </div>
            )}

            {activeTab === 'clinical' && (
              <div>
                <h4>Clinical Notes</h4>
                <p>Patient presents with elevated blood pressure and reports occasional chest discomfort. Lifestyle factors include sedentary behavior and high-sodium diet.</p>
                
                <h4 style={{ marginTop: '20px' }}>Medical History</h4>
                <ul>
                  <li>Hypertension (diagnosed 2018)</li>
                  <li>Type 2 Diabetes (diagnosed 2020)</li>
                  <li>Hyperlipidemia</li>
                </ul>
              </div>
            )}

            {activeTab === 'lab' && (
              <div>
                <h4>Recent Lab Results</h4>
                <InfoGrid>
                  <InfoItem>
                    <InfoLabel>Cholesterol</InfoLabel>
                    <InfoValue>230 mg/dL (High)</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>HbA1c</InfoLabel>
                    <InfoValue>7.8% (Elevated)</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>Creatinine</InfoLabel>
                    <InfoValue>1.1 mg/dL (Normal)</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>eGFR</InfoLabel>
                    <InfoValue>75 mL/min/1.73m²</InfoValue>
                  </InfoItem>
                </InfoGrid>
              </div>
            )}

            {activeTab === 'treatment' && (
              <div>
                <h4>Current Medications</h4>
                <ul>
                  <li>Lisinopril 10mg daily</li>
                  <li>Metformin 500mg twice daily</li>
                  <li>Atorvastatin 20mg daily</li>
                </ul>

                <h4 style={{ marginTop: '20px' }}>Recommended Treatment Pathway</h4>
                <p>Based on similar cases and clinical guidelines, consider:</p>
                <ol>
                  <li>Increase Lisinopril to 20mg daily</li>
                  <li>Add low-dose aspirin therapy</li>
                  <li>Refer to nutritionist for dietary counseling</li>
                  <li>Schedule follow-up in 2 weeks</li>
                </ol>
              </div>
            )}

            {activeTab === 'ai' && (
              <div>
                <h4>AI-Powered Insights</h4>
                <InfoItem style={{ marginBottom: '16px', background: '#eff6ff' }}>
                  <InfoLabel>Risk Prediction</InfoLabel>
                  <InfoValue>68% probability of cardiovascular event within 5 years</InfoValue>
                </InfoItem>

                <InfoItem style={{ marginBottom: '16px', background: '#f0fdf4' }}>
                  <InfoLabel>Recommended Monitoring</InfoLabel>
                  <InfoValue>Weekly blood pressure checks, quarterly HbA1c testing</InfoValue>
                </InfoItem>

                <h4 style={{ marginTop: '20px' }}>Similar Case Outcomes</h4>
                <p>Patients with similar profiles showed 45% improvement with intensified medication regimen and lifestyle modifications.</p>
              </div>
            )}
          </TabContent>

          <ButtonGroup>
            <Button>Generate Treatment Plan</Button>
            <Button>Request Additional Tests</Button>
            <SecondaryButton onClick={() => setShowPatientModal(false)}>
              Close
            </SecondaryButton>
          </ButtonGroup>
        </ModalContent>
      </ModalOverlay>
    );
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <Wrap>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>Loading patients...</p>
          </div>
        </Wrap>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <Wrap>
        <h1 style={{margin:'0 0 20px'}}>Patient Dashboard - Doctor View</h1>

        {/* Dashboard Overview */}
        <DashboardGrid>
          <DashboardCard>
            <CardTitle>Patient Statistics</CardTitle>
            <StatsGrid>
              <StatItem>
                <StatValue>{filtered.length}</StatValue>
                <StatLabel>Total Patients</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{highRiskPatients.length}</StatValue>
                <StatLabel>High Risk</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{filtered.filter(p => p.risk === 'Medium').length}</StatValue>
                <StatLabel>Medium Risk</StatLabel>
              </StatItem>
            </StatsGrid>
          </DashboardCard>

          <RiskPanel>
            <CardTitle>High-Risk Patients Alert</CardTitle>
            {highRiskPatients.length > 0 ? (
              highRiskPatients.slice(0, 3).map(patient => (
                <div key={patient.id} style={{ marginBottom: '12px', padding: '8px', background: '#fef2f2', borderRadius: '6px' }}>
                  <strong>{patient.name}</strong> - {patient.lastDiagnosis?.title}
                  <div style={{ fontSize: '12px', color: '#6b7280' }}>
                    Last update: {new Date(patient.updatedAt).toLocaleDateString()}
                  </div>
                </div>
              ))
            ) : (
              <p>No high-risk patients at this time</p>
            )}
          </RiskPanel>
        </DashboardGrid>

        {/* Patient List */}
        <Controls>
          <input 
            placeholder="Search name or ID…" 
            value={q} 
            onChange={e=>setQ(e.target.value)}
            style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px' }}
          />
          <select 
            value={risk} 
            onChange={e=>setRisk(e.target.value as any)}
            style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px' }}
          >
            <option>All</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </Controls>

        <Table>
            <colgroup>
            <col style={{ width: '25%' }} />  {/* Patient */}
            <col style={{ width: '20%' }} />  {/* Last Diagnosis */}
            <col style={{ width: '10%' }} />  {/* Confidence */}
            <col style={{ width: '10%' }} />  {/* Risk */}
            <col style={{ width: '12%' }} />  {/* Updated */}
            <col style={{ width: '23%'  }} />  {/* Actions */}
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
                      <Button onClick={() => handleOpenPatientChart(p)} style={{marginRight: '8px'}}>
                        View Chart
                      </Button>
                      <Button onClick={() => handleOpenPatientChart(p)}>
                        AI Analysis
                      </Button>
                    </td>
                </tr>
                ))}
            </tbody>
        </Table>

        {showPatientModal && renderPatientModal()}
      </Wrap>
    </>
  );
}