import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import Navbar from 'components/homepage/Navbar';
import { fetchAssignedPatientsHybrid, PatientRow } from 'services/clinician';
import SectionTabs from 'components/common/SectionTabs';

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

const DashboardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
`;
const DashboardCard = styled.div`background:#fff; padding:20px; border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,.1);`;
const CardTitle = styled.h3`margin:0 0 16px 0; font-size:16px; color:#374151;`;
const RiskPanel = styled(DashboardCard)`border-left:4px solid #ef4444;`;
const StatsGrid = styled.div`display:grid; grid-template-columns:repeat(3,1fr); gap:12px;`;
const StatItem = styled.div`text-align:center; padding:12px; background:#f9fafb; border-radius:8px;`;
const StatValue = styled.div`font-size:24px; font-weight:bold; color:#111827;`;
const StatLabel = styled.div`font-size:12px; color:#6b7280; margin-top:4px;`;

type RiskLevel = 'High'|'Medium'|'Low'|'Unknown';
const Risk = styled.span<{level?:RiskLevel}>`
  display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; line-height:1.2;
  ${({ level }) => {
    switch (level) {
      case 'High': return 'background:#fee2e2;color:#b91c1c;';
      case 'Medium': return 'background:#fff7ed;color:#9a3412;';
      case 'Low': return 'background:#e6f4ff;color:#1d4ed8;';
      default: return 'background:#e5e7eb;color:#374151;';
    }
  }}
`;

const Button = styled.button`
  padding:8px 16px; background:#3b82f6; color:#fff; border:none; border-radius:6px; cursor:pointer;
  &:hover{background:#2563eb;}
`;

export default function DoctorPatients() {
  const navigate = useNavigate();
  const [rows, setRows] = useState<PatientRow[]>([]);
  const [q, setQ] = useState('');
  const [risk, setRisk] = useState<'All'|'High'|'Medium'|'Low'>('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const data = await fetchAssignedPatientsHybrid(); // live when logged-in, demo otherwise
        if (mounted) setRows(data);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const filtered = rows.filter(r =>
    (risk === 'All' || r.risk === risk) &&
    (r.name.toLowerCase().includes(q.toLowerCase()) || r.id.toLowerCase().includes(q.toLowerCase()))
  );
  const highRiskPatients = filtered.filter(p => p.risk === 'High');

  if (loading) {
    return (
      <>
        <Navbar />
        <Wrap><div style={{ textAlign:'center', padding:40 }}>Loading patients…</div></Wrap>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <SectionTabs />
      <Wrap>
        <h1 style={{margin:'0 0 20px'}}>Assigned Patients – Doctor View</h1>

        <DashboardGrid>
          <DashboardCard>
            <CardTitle>Assigned Patients</CardTitle>
            <StatsGrid>
              <StatItem><StatValue>{filtered.length}</StatValue><StatLabel>Total Patients</StatLabel></StatItem>
              <StatItem><StatValue>{highRiskPatients.length}</StatValue><StatLabel>High Risk</StatLabel></StatItem>
              <StatItem><StatValue>{filtered.filter(p=>p.risk==='Medium').length}</StatValue><StatLabel>Medium Risk</StatLabel></StatItem>
            </StatsGrid>
          </DashboardCard>
          <RiskPanel>
            <CardTitle>High-Risk Patients Alert</CardTitle>
            {highRiskPatients.length ? (
              highRiskPatients.slice(0,3).map(p => (
                <div key={p.id} style={{ marginBottom:12, padding:8, background:'#fef2f2', borderRadius:6 }}>
                  <strong>{p.name}</strong> — {p.lastDiagnosis?.title ?? '—'}
                  <div style={{ fontSize:12, color:'#6b7280' }}>
                    Last update: {p.updatedAt ? new Date(p.updatedAt).toLocaleDateString() : '—'}
                  </div>
                </div>
              ))
            ) : <p>No high-risk patients at this time</p>}
          </RiskPanel>
        </DashboardGrid>

        <Controls>
          <input
            placeholder="Search name or ID…"
            value={q}
            onChange={e=>setQ(e.target.value)}
            style={{ padding:'8px 12px', border:'1px solid #d1d5db', borderRadius:6 }}
          />
          <select
            value={risk}
            onChange={e=>setRisk(e.target.value as any)}
            style={{ padding:'8px 12px', border:'1px solid #d1d5db', borderRadius:6 }}
          >
            <option>All</option><option>High</option><option>Medium</option><option>Low</option>
          </select>
        </Controls>

        <Table>
          <colgroup>
            <col style={{ width:'25%' }}/><col style={{ width:'20%' }}/><col style={{ width:'10%' }}/>
            <col style={{ width:'10%' }}/><col style={{ width:'12%' }}/><col style={{ width:'23%' }}/>
          </colgroup>
          <thead>
            <tr>
              <th>Patient</th><th>Last Diagnosis</th><th className="right">Confidence</th>
              <th className="center">Risk</th><th className="right">Updated</th><th className="nowrap">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(p => (
              <tr key={p.id}>
                <td>
                  <strong>{p.name}</strong>
                  <div style={{color:'#6b7280', fontSize:12}}>ID: {p.id} • {p.ageGroup ?? '—'} • {p.gender ?? '—'}</div>
                </td>
                <td>{p.lastDiagnosis?.title ?? '—'}</td>
                <td className="right">{p.lastDiagnosis?.confidence != null ? Math.round(p.lastDiagnosis.confidence*100)+'%' : '—'}</td>
                <td className="center"><Risk level={p.risk as RiskLevel}>{p.risk}</Risk></td>
                <td className="right">{p.updatedAt ? new Date(p.updatedAt).toLocaleDateString() : '—'}</td>
                <td className="nowrap">
                  <Button
                    onClick={() => navigate(`/patient/${encodeURIComponent(p.id)}`)}
                    style={{marginRight:8}}
                  >
                    View Chart
                  </Button>
                  <Button
                    onClick={() => navigate(`/patient/${encodeURIComponent(p.id)}?tab=copilot`)}
                  >
                    AI Analysis
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Wrap>
    </>
  );
}
