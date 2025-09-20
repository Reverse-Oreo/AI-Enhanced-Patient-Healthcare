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

  .right  { text-align:right;  font-variant-numeric: tabular-nums; } /* 48% / 82% align */
  .center { text-align:center; }
  .nowrap { white-space:nowrap; }                                    /* action button */
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

export default function Patients() {
  const { loggedIn } = useAuth();
  const [rows, setRows] = useState<any[]>([]);
  const [q, setQ] = useState('');
  const [risk, setRisk] = useState<'All'|'High'|'Medium'|'Low'>('All');

  useEffect(() => { fetchPatients().then(setRows).catch(console.error); }, []);

  const filtered = rows.filter(r =>
    (risk==='All' || r.risk===risk) &&
    (r.name.toLowerCase().includes(q.toLowerCase()) || r.id.toLowerCase().includes(q.toLowerCase()))
  );

  return (
    <>
      <Navbar />
      <Wrap>
        <h1 style={{margin:'0 0 10px'}}>Patients</h1>

        <Controls>
          <input placeholder="Search name or ID…" value={q} onChange={e=>setQ(e.target.value)} />
          <select value={risk} onChange={e=>setRisk(e.target.value as any)}>
            <option>All</option><option>High</option><option>Medium</option><option>Low</option>
          </select>
        </Controls>

        <Table>
            <colgroup>
            <col style={{ width: '30%' }} />  {/* Patient */}
            <col style={{ width: '28%' }} />  {/* Last Diagnosis */}
            <col style={{ width: '12%' }} />  {/* Confidence */}
            <col style={{ width: '10%' }} />  {/* Risk */}
            <col style={{ width: '12%' }} />  {/* Updated */}
            <col style={{ width: '8%'  }} />  {/* Actions */}
            </colgroup>

            <thead>
                <tr>
                <th>Patient</th>
                <th>Last Diagnosis</th>
                <th className="right">Confidence</th>
                <th className="center">Risk</th>
                <th className="right">Updated</th>
                <th className="nowrap"></th>
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
                    <td className="nowrap"><button>Open chart →</button></td>
                </tr>
                ))}
            </tbody>
        </Table>
      </Wrap>
    </>
  );
}
