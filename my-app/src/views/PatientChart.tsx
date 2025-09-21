import React, { useEffect, useMemo, useState } from 'react';
import styled from 'styled-components';
import { useParams, Link } from 'react-router-dom';
import Navbar from 'components/homepage/Navbar';
import { fetchPatientSummaryHybrid, PatientSummary } from 'services/patient';
import { supabase } from '../lib/supabase'; // adjust path if your alias differs
import { jsPDF } from 'jspdf';

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

/* ---------- Treatment styles ---------- */
const TreatmentWrap = styled.div`padding-top:12px;`;
const IndentedList = styled.ul`padding-left:22px; margin:8px 0;`; /* move bullets to the right */
const NoteHeader = styled.div`display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin:8px 0 6px;`;
const NoteList = styled.div`display:flex; flex-direction:column; gap:8px;`;
const NoteCard = styled.div`border:1px solid #e5e7eb; border-radius:8px; padding:10px; background:#fafafa;`;
const Small = styled.div`font-size:12px; color:#6b7280;`;
const Button = styled.button`
  padding:8px 12px; border-radius:8px; border:1px solid #d1d5db; background:#fff; cursor:pointer;
  &:hover{background:#f8fafc;}
`;
const Primary = styled(Button)`background:#2563eb; color:#fff; border-color:#2563eb; &:hover{background:#1d4ed8;}`;

type NoteVersion = { text: string; editedAt: string };
type Note = { id: string; text: string; createdAt: string; versions: NoteVersion[] };

export default function PatientChart() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<'overview'|'clinical'|'lab'|'treatment'|'copilot'>('overview');
  const [data, setData] = useState<PatientSummary | null>(null);

  // Chat state
  const [msgs, setMsgs] = useState<ChatMsg[]>([
    { role: 'assistant', text: 'Hi doctor! Ask me about this patient’s risk, next tests, or treatment adjustments.' }
  ]);
  const [input, setInput] = useState('');

  // Treatment notes state
  const [notes, setNotes] = useState<Note[]>([]);
  const [draft, setDraft] = useState('');
  const [editingId, setEditingId] = useState<string|null>(null);
  const [loadingNotes, setLoadingNotes] = useState(false);
  const [savingNotes, setSavingNotes] = useState(false);

  /* ---------- Fetch patient summary ---------- */
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

  /* ---------- Load notes from Supabase (if logged-in) ---------- */
  useEffect(() => {
    let on = true;
    (async () => {
      if (!id) return;
      setLoadingNotes(true);
      try {
        // Try to load latest "doctor_notes" record
        const { data: existing, error } = await supabase
          .from('medical_reports')
          .select('id, followup_data')
          .eq('user_id', id)
          .eq('session_id', 'doctor_notes')
          .order('updated_at', { ascending: false })
          .limit(1)
          .maybeSingle();

        if (!on) return;
        if (!error && existing?.followup_data?.notes) {
          setNotes(existing.followup_data.notes as Note[]);
        } else {
          // demo fallback: show nothing or a starter note
          setNotes([]);
        }
      } catch {
        // demo mode / not logged in
        setNotes([]);
      } finally {
        if (on) setLoadingNotes(false);
      }
    })();
    return () => { on = false; };
  }, [id]);

  /* ---------- Save notes to Supabase (if logged-in) ---------- */
  async function persistNotes(updated: Note[]) {
    if (!id) return; // demo mode / unknown id
    setSavingNotes(true);
    try {
      const { data: existing } = await supabase
        .from('medical_reports')
        .select('id')
        .eq('user_id', id)
        .eq('session_id', 'doctor_notes')
        .maybeSingle();

      if (existing?.id) {
        await supabase.from('medical_reports').update({
          followup_data: { notes: updated },
          updated_at: new Date().toISOString()
        }).eq('id', existing.id);
      } else {
        await supabase.from('medical_reports').insert({
          user_id: id,
          session_id: 'doctor_notes',
          report_title: 'Doctor Notes',
          report_status: 'completed',
          followup_data: { notes: updated }
        });
      }
    } finally {
      setSavingNotes(false);
    }
  }

  /* ---------- Notes UI handlers ---------- */
  function addNote() {
    if (!draft.trim()) return;
    const n: Note = {
      id: crypto.randomUUID(),
      text: draft.trim(),
      createdAt: new Date().toISOString(),
      versions: []
    };
    const updated = [n, ...notes];
    setNotes(updated);
    setDraft('');
    // try to persist (no-op in demo)
    void persistNotes(updated);
  }

  function startEdit(id: string, text: string) {
    setEditingId(id);
    setDraft(text);
  }

  function cancelEdit() {
    setEditingId(null);
    setDraft('');
  }

  function saveEdit() {
    if (!editingId) return;
    const updated = notes.map(n => {
      if (n.id !== editingId) return n;
      return {
        ...n,
        versions: [{ text: n.text, editedAt: new Date().toISOString() }, ...n.versions],
        text: draft.trim()
      };
    });
    setNotes(updated);
    setEditingId(null);
    setDraft('');
    void persistNotes(updated);
  }

  /* ---------- PDF helpers ---------- */
  function downloadTreatmentPDF() {
    const doc = new jsPDF();
    let y = 16;
    doc.setFontSize(16);
    doc.text('Patient Treatment Plan', 14, y);
    y += 8;
    if (data?.name) { doc.setFontSize(11); doc.text(`Patient: ${data.name}`, 14, y); y += 6; }
    doc.setFontSize(12);
    doc.text('Plan (static items):', 14, y); y += 6;
    const staticItems = [
      'Continue BP log; review in 2 weeks',
      'Consider lipid-lowering if LDL >= 160'
    ];
    staticItems.forEach(s => { doc.text(`• ${s}`, 20, y); y += 6; });

    if (notes.length) {
      y += 6;
      doc.text('Doctor Notes:', 14, y); y += 6;
      notes.forEach(n => {
        doc.text(`• ${n.text}`, 20, y);
        y += 5;
        if (n.versions?.length) {
          n.versions.slice(0,2).forEach(v => { doc.text(`  (prev) ${v.text}`, 20, y); y += 5; });
        }
        y += 1;
        if (y > 280) { doc.addPage(); y = 16; }
      });
    }
    doc.save(`treatment_${id ?? 'demo'}.pdf`);
  }

  function downloadChatPDF() {
  const doc = new jsPDF();
  let y = 16;
  doc.setFontSize(16);
  doc.text('Patient Chat Transcript', 14, y); y += 8;
  doc.setFontSize(11);

  msgs.forEach((m: ChatMsg) => {
    const chunks = doc.splitTextToSize(
      `${m.role === 'user' ? 'You' : 'Assistant'}: ${m.text}`,
      180
    ) as string[];                           // ← type the result

    chunks.forEach((line: string) => {       // ← type the item
      doc.text(line, 14, y);
      y += 6;
      if (y > 280) { doc.addPage(); y = 16; }
    });

    y += 2;
  });

  doc.save(`chat_${id ?? 'demo'}.pdf`);
}


  /* ---------- Demo reply ---------- */
  function onSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;
    const question = input.trim();
    const riskLine = data ? `Current risk is ${data.risk}.` : '';
    const bp = vitals?.blood_pressure ? `BP ${vitals.blood_pressure}` : '';
    const hba1c = labs?.hba1c != null ? `HbA1c ${labs.hba1c}.` : '';
    const assistant = `Here’s a quick take:\n• ${riskLine}\n• ${bp}\n• ${hba1c}\n\nI can draft orders or suggest next tests if you like.`;
    setMsgs(m => [...m, { role:'user', text: question }, { role:'assistant', text: assistant }]);
    setInput('');
  }

  /* ---------- Overview panel ---------- */
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

            {tab === 'overview' && <div style={{paddingTop:12}}>{overview}</div>}

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
              <TreatmentWrap>
                <p style={{margin:'0 0 6px'}}>Plan: <Small>(draft orders, meds, follow-ups)</Small></p>
                <IndentedList>
                  <li>Continue BP log; review in 2 weeks</li>
                  <li>Consider lipid-lowering if LDL &gt;= 160</li>
                </IndentedList>

                <NoteHeader>
                  <strong style={{marginRight:8}}>Doctor Notes</strong>
                  <Small>{loadingNotes ? 'Loading…' : savingNotes ? 'Saving…' : data?.source === 'demo' ? 'Demo (not persisted)' : 'Live'}</Small>
                  <div style={{flex:1}} />
                  <Button onClick={downloadTreatmentPDF}>Download as PDF</Button>
                </NoteHeader>

                {/* Draft / Edit area */}
                <div style={{display:'grid', gap:8, margin:'8px 0 10px'}}>
                  <textarea
                    value={draft}
                    onChange={e=>setDraft(e.target.value)}
                    placeholder={editingId ? 'Edit note…' : 'Add a note…'}
                    rows={3}
                    style={{width:'100%', border:'1px solid #d1d5db', borderRadius:8, padding:10}}
                  />
                  <div style={{display:'flex', gap:8}}>
                    {editingId ? (
                      <>
                        <Primary onClick={saveEdit}>Save changes</Primary>
                        <Button onClick={cancelEdit}>Cancel</Button>
                      </>
                    ) : (
                      <Primary onClick={addNote}>Add note</Primary>
                    )}
                  </div>
                </div>

                {/* Notes list with history */}
                <NoteList>
                  {notes.length === 0 && <Small>No notes yet.</Small>}
                  {notes.map(n => (
                    <NoteCard key={n.id}>
                      <div style={{display:'flex', justifyContent:'space-between', gap:8}}>
                        <div style={{whiteSpace:'pre-wrap'}}>{n.text}</div>
                        <div style={{display:'flex', gap:8}}>
                          <Button onClick={()=>startEdit(n.id, n.text)}>Edit</Button>
                        </div>
                      </div>
                      <Small>Created {new Date(n.createdAt).toLocaleString()}</Small>
                      {n.versions?.length > 0 && (
                        <details style={{marginTop:6}}>
                          <summary style={{cursor:'pointer'}}>View history ({n.versions.length})</summary>
                          <div style={{marginTop:6, display:'grid', gap:6}}>
                            {n.versions.map((v, i) => (
                              <div key={i} style={{borderLeft:'3px solid #e5e7eb', paddingLeft:8}}>
                                <Small>Edited {new Date(v.editedAt).toLocaleString()}</Small>
                                <div style={{whiteSpace:'pre-wrap'}}>{v.text}</div>
                              </div>
                            ))}
                          </div>
                        </details>
                      )}
                    </NoteCard>
                  ))}
                </NoteList>
              </TreatmentWrap>
            )}

            {tab === 'copilot' && (
              <div style={{paddingTop:12}}>
                <p>Ask anything about this patient. (This demo answers locally; swap to LLM endpoint later.)</p>
              </div>
            )}
          </Card>

          {/* Right: Copilot panel (always visible) */}
          <Card>
            <div style={{display:'flex', alignItems:'center', justifyContent:'space-between'}}>
              <h3 style={{marginTop:0}}>Copilot</h3>
              <Button onClick={downloadChatPDF}>Save chat as PDF</Button>
            </div>
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
                <Primary type="submit">Send</Primary>
              </ChatInput>
            </ChatBox>
          </Card>
        </Grid>
      </Page>
    </>
  );
}
