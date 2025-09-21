import Navbar from "components/homepage/Navbar";
import styled from "styled-components";
import { useAuth } from "contexts/AuthContext";

const Wrap = styled.div`
  max-width: 1100px; margin: 40px auto; padding: 0 20px;
`;
const H1 = styled.h1`font-size: 44px; margin-bottom: 8px;`;
const Sub = styled.p`color:#64748b; margin:0 0 24px;`;
const Btn = styled.a<{ $primary?: boolean }>`
  display:inline-flex; align-items:center; padding:10px 14px; border-radius:10px; font-weight:700;
  text-decoration:none;
  background:${p=>p.$primary?'#1365ff':'#f6f7fb'}; color:${p=>p.$primary?'#fff':'#222'};
`;

export default function NurseHome() {
  const { user } = useAuth();
  return (
    <>
      <Navbar />
      <Wrap>
        <H1>Welcome, Nurse {user?.name || 'User'} 🩺</H1>
        <Sub>Insight-driven, efficient care at a glance.</Sub>

        <div style={{display:'flex', gap:16, flexWrap:'wrap'}}>
          <Btn href="/nurse-patients" $primary>Patients →</Btn>
          <Btn href="/nurse-worklist">Worklist</Btn>
        </div>
      </Wrap>
    </>
  );
}
