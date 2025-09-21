import React, { useEffect, useMemo, useState } from 'react';
import styled from 'styled-components';
import { useParams, Link } from 'react-router-dom';
import Navbar from 'components/homepage/Navbar';
import { fetchPatientSummaryHybrid, PatientSummary } from 'services/patient';

const Page = styled.div`max-width:1220px; margin:0 auto; padding:20px;`;
const Grid = styled.div`display:grid; grid-template-columns: 1.2fr .8fr; gap:16px; align-items:start;`;
const Card = styled.div`background:#fff; border:1px solid #eef0f3; border-radius:12px; padding:16px;`;
const Tabs = styled.div`display:flex; border-bottom:1px solid #eee; gap:8px;`;
const Tab = styled.button<{active:boolean}>`
  padding:10px 14px; border:none; background:none; cursor:pointer;
  border-bottom:2px solid ${p=>p.active?'#2563eb':'transparent'};
  color:${p=>p.active?'#2563eb':'#6b7280'}; font-weight:${p=>p.active?700:500};
`;
const Label = styled.div`font-size:12px; color:#6b7280; margin-bottom:4px;`;
const Value = styled.div`font-weight:600; color:#111827;`;
const Row = styled.div`display:grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap:12px; margin:12px 0;`;
const RiskBadge = styled.span<{level:PatientSummary['risk']}>`
  padding:4px 10px; border-radius:999px; font-size:12px;
  ${({level}) => level==='High'
    ? 'background:#fee2e2;color:#b91c1c;'
    : level==='Medium'
    ? 'background:#fff7ed;color:#9a3412;'
    : level==='Low'
    ? 'background:#e6f4ff;color:#1d4ed8;'
    : 'background:#e5e7eb;color:#374151;'}
`;

type ChatMsg = { role: 'user'|'assistant'; text: string };
const ChatBox = styled.div`display:flex; flex-direction:column; height:520px;`;
const ChatLog = styled.div`flex:1; overflow:auto; border:1px solid #eee; border-radius:8px; padding:12px; margin-bottom:8px; background:#fafafa;`;
const ChatInput = styled.form`display:flex; gap:8px;`;
const Input = styled.input`flex:1; border:1px solid #d1d5db; border-radius:8px; padding:10px;`;

export default function PatientChart() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<'overview'|'clinical'|'lab'|'treatment'|'copilot'>('overview');
  const [data, setData] = useState<PatientSummary | null>(null);
  const [msgs, setMsgs] = useState<ChatMsg[]>([
    { role: 'assistant', text: 'Hi doctor! Ask me about this patient’s risk, next tests, or treatment adjustments.' }
  ]);
  const [input, setInput] = useState('');

  useEffect(() => {
    let live = true;
    (async () => {
      const summary = await fetchPatientSummaryHybrid(id);
      if (live) setData(summary);
    })();
    return () => { live = false; };
  }, [id]);

  const vitals = data?.clinical;
  const labs = data?.labs;

  const overview = useMemo(() => {
    if (!data) return null;
    return (
      <>
        <Row>
          <div><Label>Patient</Label><Value>{data.name ?? '—'}</Value></div>
          <div><Label>Age / Gender</Label><Value>{data.age ?? '—'} • {data.gender ?? '—'}</Value></div>
        </Row>
        <Row>
          <div><Label>Risk</Label><Value><RiskBadge level={data.risk}>{data.risk}</RiskBadge></Value></div>
          <div><Label>Latest Report</Label>
            <Value>{data.lastReport?.title ?? '—'} {data.lastReport?.confidence != null ? `(${Math.round((data.lastReport.confidence)*100)}%)` : ''}</Value>
          </div>
        </Row>
      </>
    );
  }, [data]);

  function onSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;
    // Demo-only: simple canned assistant reply using fetched data.
    const question = input.trim();
    const assistant = (() => {
      const riskLine = data ? `Current risk is ${data.risk}.` : '';
      const bp = vitals?.blood_pressure ? `BP ${vitals.blood_pressure}` : '';
      const hba1c = labs?.hba1c != null ? `HbA1c ${labs.hba1c}.` : '';
      return `Here’s a quick take:\n• ${riskLine}\n• ${bp}\n• ${hba1c}\n\nI can draft orders or suggest next tests if you like.`;
    })();
    setMsgs(m => [...m, { role:'user', text: question }, { role:'assistant', text: assistant }]);
    setInput('');
  }

  return (
    <>
      <Navbar />
      <Page>
        <div style={{display:'flex', alignItems:'center', gap:12, marginBottom:12}}>
          <Link to="/patients" style={{textDecoration:'none'}}>← Back to Assigned Patients</Link>
          <h2 style={{margin:'0 0 0 8px'}}>Patient Chart</h2>
        </div>

        <Grid>
          {/* Left: tabbed panels */}
          <Card>
            <Tabs>
              {(['overview','clinical','lab','treatment','copilot'] as const).map(t => (
                <Tab key={t} active={tab===t} onClick={() => setTab(t)}>
                  {t[0].toUpperCase()+t.slice(1)}
                </Tab>
              ))}
            </Tabs>

            {tab === 'overview' && (
              <div style={{paddingTop:12}}>
                {overview}
              </div>
            )}

            {tab === 'clinical' && (
              <div style={{paddingTop:12}}>
                <Row>
                  <div><Label>Blood Pressure</Label><Value>{vitals?.blood_pressure ?? '—'}</Value></div>
                  <div><Label>Heart Rate</Label><Value>{vitals?.heart_rate ?? '—'} bpm</Value></div>
                </Row>
                <Row>
                  <div><Label>Temperature</Label><Value>{vitals?.temperature ?? '—'} °C</Value></div>
                  <div><Label>BMI</Label><Value>{vitals?.bmi ?? '—'}</Value></div>
                </Row>
                <Row>
                  <div><Label>Chronic</Label><Value>
                    {(vitals?.diabetes ? 'Diabetes, ' : '')}
                    {(vitals?.hypertension ? 'Hypertension, ' : '')}
                    {(vitals?.heart_disease ? 'Heart disease' : '') || '—'}
                  </Value></div>
                  <div><Label>Recorded</Label><Value>{vitals?.recorded_at ? new Date(vitals.recorded_at).toLocaleString() : '—'}</Value></div>
                </Row>
                <Row>
                  <div><Label>Medications</Label><Value>{vitals?.medications ?? '—'}</Value></div>
                  <div><Label>Symptoms</Label><Value>{vitals?.symptoms ?? '—'}</Value></div>
                </Row>
              </div>
            )}

            {tab === 'lab' && (
              <div style={{paddingTop:12}}>
                <Row>
                  <div><Label>HbA1c</Label><Value>{labs?.hba1c ?? '—'}</Value></div>
                  <div><Label>Fasting Glucose</Label><Value>{labs?.fasting_blood_sugar ?? '—'}</Value></div>
                </Row>
                <Row>
                  <div><Label>LDL / HDL</Label><Value>{labs?.ldl ?? '—'} / {labs?.hdl ?? '—'}</Value></div>
                  <div><Label>Total Cholesterol</Label><Value>{labs?.total_cholesterol ?? '—'}</Value></div>
                </Row>
                <Row>
                  <div><Label>Hemoglobin</Label><Value>{labs?.hemoglobin ?? '—'}</Value></div>
                  <div><Label>Creatinine</Label><Value>{labs?.creatinine ?? '—'}</Value></div>
                </Row>
                <Row>
                  <div><Label>ALT / AST</Label><Value>{labs?.alt ?? '—'} / {labs?.ast ?? '—'}</Value></div>
                  <div><Label>Recorded</Label><Value>{labs?.recorded_at ? new Date(labs.recorded_at).toLocaleString() : '—'}</Value></div>
                </Row>
              </div>
            )}

            {tab === 'treatment' && (
              <div style={{paddingTop:12}}>
                <p>Plan: (draft orders, meds, follow-ups)</p>
                <ul>
                  <li>Continue BP log; review in 2 weeks</li>
                  <li>Consider lipid-lowering if LDL &gt;= 160</li>
                </ul>
              </div>
            )}

            {tab === 'copilot' && (
              <div style={{paddingTop:12}}>
                <p>Ask anything about this patient. (This demo answers locally; swap to your LLM endpoint later.)</p>
              </div>
            )}
          </Card>

          {/* Right: Copilot panel (always visible) */}
          <Card>
            <h3 style={{marginTop:0}}>Copilot</h3>
            <ChatBox>
              <ChatLog>
                {msgs.map((m,i) => (
                  <div key={i} style={{marginBottom:10}}>
                    <strong>{m.role==='user'?'You':'Assistant'}: </strong>
                    <span style={{whiteSpace:'pre-wrap'}}>{m.text}</span>
                  </div>
                ))}
              </ChatLog>
              <ChatInput onSubmit={onSend}>
                <Input
                  placeholder="e.g. summarize risk and suggest next tests"
                  value={input}
                  onChange={e=>setInput(e.target.value)}
                />
                <button type="submit" style={{padding:'10px 14px'}}>Send</button>
              </ChatInput>
            </ChatBox>
          </Card>
        </Grid>
      </Page>
    </>
  );
}
