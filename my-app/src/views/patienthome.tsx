import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import { useAuth } from 'contexts/AuthContext';

const Wrap = styled.main`padding:32px 16px 56px;`;
const Hero = styled.section`
  max-width:1100px; margin:0 auto; display:grid; grid-template-columns:1.1fr .9fr;
  gap:24px; align-items:center;
  @media (max-width:900px){ grid-template-columns:1fr; }
`;
const H1 = styled.h1`
  font-size:64px; line-height:.95; margin:16px 0; letter-spacing:-.02em;
`;
const P = styled.p`color:#4b5563; max-width:52ch;`;
const CTA = styled.div`display:flex; gap:10px; margin-top:18px;`;
const Btn = styled.a<{ $primary?: boolean }>`
  display:inline-flex; align-items:center; padding:10px 14px; border-radius:10px; font-weight:700;
  text-decoration:none;
  background:${p=>p.$primary?'#16a34a':'#f6f7fb'}; color:${p=>p.$primary?'#fff':'#222'};
`;
const Accent = styled.div`height:4px; background:#22c55e;`;

const PatientHome: React.FC = () => {
  const { user } = useAuth();
  return (
    <>
      <Navbar />
      <Accent />
      <Wrap>
        <Hero>
          <div>
            <H1>Welcome{user?.name ? `, ${user.name}` : ''} 👋</H1>
            <P>Answer a few questions and get likely causes, confidence scores, and next steps. Save or share reports with your doctor.</P>
            <CTA>
              <Btn href="/diagnosis" $primary>Start Diagnosis →</Btn>
              <Btn href="/profile">My Reports</Btn>
            </CTA>
          </div>
          <img src="/assets/patients.png" alt="" style={{width:'100%', height:'auto'}}/>
        </Hero>
      </Wrap>
    </>
  );
};
export default PatientHome;
