import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import SectionTabs from 'components/common/SectionTabs';
import { fetchAssignedPatientsHybrid, PatientRow } from 'services/clinician';

const Wrap = styled.div`max-width:1320px; margin:0 auto; padding:24px;`;
const Grid = styled.div`display:grid; grid-template-columns: 2fr 1.2fr; gap:20px; margin:16px 0 24px;`;
const Card = styled.div`background:#fff; padding:20px; border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,.08);`;
const CardTitle = styled.h3`margin:0 0 12px; font-size:16px; color:#374151;`;
const Stats = styled.div`display:grid; grid-template-columns:repeat(3,1fr); gap:12px;`;
const Stat = styled.div`background:#f9fafb; border:1px solid #eef0f3; border-radius:10px; padding:14px; text-align:center;`;
const StatVal = styled.div`font-size:24px; font-weight:700;`;
const StatLabel = styled.div`font-size:12px; color:#6b7280; margin-top:4px;`;
const Danger = styled(Card)`border-left:4px solid #ef4444;`;

type RiskLevel = 'High'|'Medium'|'Low'|'Unknown';
const Risk = styled.span<{level?:RiskLevel}>`
  display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px;
  ${({ level }) => {
    switch (level) {
      case 'High': return 'background:#fee2e2;color:#b91c1c;';
      case 'Medium': return 'background:#fff7ed;color:#9a3412;';
      case 'Low': return 'background:#e6f4ff;color:#1d4ed8;';
      default: return 'background:#e5e7eb;color:#374151;';
    }
  }}
`;

export default function ClinicianDashboard() {
  const [rows, setRows] = useState<PatientRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ok = true;
    (async () => {
      try {
        setLoading(true);
        const data = await fetchAssignedPatientsHybrid(); // live when logged in, demo otherwise
        if (ok) setRows(data);
      } finally {
        if (ok) setLoading(false);
      }
    })();
    return () => { ok = false; };
  }, []);

  // Counts
  const total = rows.length;
  const high = rows.filter(r => r.risk === 'High').length;
  const medium = rows.filter(r => r.risk === 'Medium').length;

  // “Recent updates” in last 7 days using updatedAt (fallback from patient row)
  const last7 = rows.filter(r => {
    const ts = r.updatedAt ? new Date(r.updatedAt).getTime() : 0;
    return Date.now() - ts < 7 * 864e5;
  }).length;

  // For a small confidence distribution if you need it later
  const confidences = rows
    .map(r => (r.lastDiagnosis?.confidence ?? null))
    .filter((x): x is number => typeof x === 'number');

  const highRiskPatients = rows.filter(r => r.risk === 'High');

  return (
    <>
      <Navbar />
      <SectionTabs />
      <Wrap>
        <h1 style={{margin:'0 0 20px'}}>Doctor Dashboard</h1>

        {loading ? (
          <div style={{ padding:40, textAlign:'center' }}>Loading…</div>
        ) : (
          <Grid>
            <Card>
              <CardTitle>Assigned Patients</CardTitle>
              <Stats>
                <Stat><StatVal>{total}</StatVal><StatLabel>Total Patients</StatLabel></Stat>
                <Stat><StatVal>{high}</StatVal><StatLabel>High Risk</StatLabel></Stat>
                <Stat><StatVal>{medium}</StatVal><StatLabel>Medium Risk</StatLabel></Stat>
              </Stats>

              <div style={{marginTop:16, fontSize:14, color:'#6b7280'}}>
                <strong>{last7}</strong> patient{last7===1?'':'s'} updated in the last 7 days.
              </div>

              {confidences.length > 0 && (
                <div style={{marginTop:8, fontSize:12, color:'#6b7280'}}>
                  Avg confidence: {Math.round(
                    (confidences.reduce((a,b)=>a+b,0) / confidences.length) * 100
                  )}%
                </div>
              )}
            </Card>

            <Danger>
              <CardTitle>High-Risk Patients Alert</CardTitle>
              {highRiskPatients.length ? (
                highRiskPatients.slice(0,4).map(p => (
                  <div key={p.id} style={{marginBottom:12, padding:10, background:'#fef2f2', borderRadius:8}}>
                    <div style={{display:'flex', justifyContent:'space-between', gap:8}}>
                      <div>
                        <strong>{p.name}</strong> — {p.lastDiagnosis?.title ?? '—'}{' '}
                        <Risk level={p.risk as RiskLevel}>{p.risk}</Risk>
                      </div>
                      <div style={{fontSize:12, color:'#6b7280'}}>
                        {p.updatedAt ? new Date(p.updatedAt).toLocaleDateString() : '—'}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p>No high-risk patients at this time</p>
              )}
            </Danger>
          </Grid>
        )}
      </Wrap>
    </>
  );
}
