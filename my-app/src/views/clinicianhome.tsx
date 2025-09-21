import styled from 'styled-components';
import { useAuth } from 'contexts/AuthContext';
import Navbar from 'components/homepage/Navbar';

const Page = styled.main`
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 16px 56px;
`;

const Hero = styled.section`
  display: grid;
  grid-template-columns: 1.1fr .9fr;
  gap: 24px;
  align-items: center;
  margin-bottom: 40px;
  @media (max-width: 900px){ grid-template-columns: 1fr; }
`;

const H1 = styled.h1`
  font-size: 44px;
  margin-bottom: 8px;
`;

const Sub = styled.p`
  color: #64748b;
  margin: 0 0 24px;
`;

const Btn = styled.a<{ $primary?: boolean }>`
  display: inline-flex;
  align-items: center;
  padding: 10px 14px;
  border-radius: 10px;
  font-weight: 700;
  text-decoration: none;
  background: ${p => p.$primary ? '#1365ff' : '#f6f7fb'};
  color: ${p => p.$primary ? '#fff' : '#222'};
`;

const Art = styled.img`
  width: 100%;
  max-width: 400px;
  height: auto;
  justify-self: center;
`;

export default function ClinicianHome() {
  const { user } = useAuth();
  return (
    <>
      <Navbar />
      <Page>
        <Hero>
          <div>
            <H1>Welcome, Dr. {user?.name || 'User'} 🩺</H1>
            <Sub>Insight-driven, efficient care at a glance.</Sub>
            <div style={{display:'flex', gap:16, flexWrap:'wrap', marginTop: 24}}>
              <Btn href="/patients" $primary>Patients →</Btn>
              <Btn href="/clinician-dashboard">Dashboard</Btn>
            </div>
          </div>
                    <Art src="/assets/doctors.png" alt="Doctor illustration" />
        </Hero>
      </Page>
    </>
  );
}