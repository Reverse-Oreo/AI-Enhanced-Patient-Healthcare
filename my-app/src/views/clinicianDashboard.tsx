import React, { useEffect, useMemo, useState } from 'react';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import { fetchAssignedPatientsHybrid, PatientRow } from 'services/clinician';

const Wrap = styled.div`max-width:1320px; margin:0 auto; padding:24px;`;
const KPIs = styled.div`display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:12px;`;
const Card = styled.div`background:#fff; border:1px solid #eef0f3; border-radius:16px; padding:18px;`;
const Big = styled.div`font-size:28px; font-weight:800;`;

export default function ClinicianDashboard() {
  const [rows, setRows] = useState<PatientRow[]>([]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      const data = await fetchAssignedPatientsHybrid();
      if (mounted) setRows(data);
    })();
    return () => { mounted = false; };
  }, []);

  const kpi = useMemo(() => {
    const total = rows.length;
    const high = rows.filter(r => r.risk === 'High').length;
    const last7 = rows.filter(r => {
      const ts = r.lastDiagnosis?.createdAt ? new Date(r.lastDiagnosis.createdAt).getTime() : 0;
      return Date.now() - ts < 7 * 864e5;
    }).length;
    const confidences = rows.map(r => r.lastDiagnosis?.confidence).filter(Boolean) as number[];
    const avgConf = confidences.length ? Math.round((confidences.reduce((a,b)=>a+b,0)/confidences.length)*100) : 0;
    const alerts = [...rows]
      .filter(r => r.risk === 'High')
      .sort((a,b) => (a.lastDiagnosis?.confidence ?? 1) - (b.lastDiagnosis?.confidence ?? 1))
      .slice(0,5);
    return { total, high, last7, avgConf, alerts };
  }, [rows]);

  return (
    <>
      <Navbar />
      <Wrap>
        <h1 style={{margin:'0 0 12px'}}>Clinician Dashboard</h1>
        <KPIs>
          <Card><div>Total Patients</div><Big>{kpi.total}</Big></Card>
          <Card><div>High-Risk</div><Big>{kpi.high}</Big></Card>
          <Card><div>Reports (7d)</div><Big>{kpi.last7}</Big></Card>
          <Card><div>Avg Confidence</div><Big>{kpi.avgConf}%</Big></Card>
        </KPIs>

        <h2 style={{margin:'24px 0 8px'}}>Alerts (Top)</h2>
        {kpi.alerts.map(p => (
          <Card key={p.id} style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
            <div>
              <strong>{p.name}</strong> — {p.lastDiagnosis?.title ?? '—'}
              <div style={{color:'#6b7280'}}>
                Conf: {p.lastDiagnosis ? Math.round((p.lastDiagnosis.confidence ?? 0)*100) : 0}% • Updated: {p.updatedAt ? new Date(p.updatedAt).toLocaleDateString() : '—'}
              </div>
            </div>
            <button onClick={() => alert('Open chart →')}>Open chart →</button>
          </Card>
        ))}
      </Wrap>
    </>
  );
}
