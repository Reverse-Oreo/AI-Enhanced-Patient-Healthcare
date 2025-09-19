import React, { useState } from 'react';
import { Helmet } from 'react-helmet';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import heroImg from 'assets/hero.png'

const Page = styled.main`
  max-width: 1320px; margin: 0 auto; padding: 24px;
`;

const HeroGrid = styled.section`
  display: grid; grid-template-columns: 1.1fr 0.9fr; gap: clamp(16px,4vw,40px); align-items:center;
  @media (max-width: 1024px){ grid-template-columns: 1fr; }
`;

const Eyebrow = styled.p`
  margin: 0 0 14px;
  font-weight: 700; text-transform: uppercase; letter-spacing: .12em;
  font-size: clamp(13px, 1.4vw, 18px); line-height: 1.25;
`;

const Title = styled.h1`
  margin: 0 0 16px; font-weight: 800; letter-spacing: -0.02em;
  font-size: clamp(40px, 8vw, 108px); line-height: 1.06;
`;

const Subtitle = styled.p`
  margin: 0 0 24px; color: var(--secondary); line-height:1.55;
  font-size: clamp(14px, 1.6vw, 18px);
`;

const Art = styled.img`
  width: 100%; max-width: 580px; height: auto; justify-self:center;
`;

const Sections = styled.section`
  margin-top: 48px; display:grid; gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
`;

const Card = styled.div`
  background:#fff; border:1px solid #eef0f3; border-radius:16px; padding:16px 18px;
  h3{ margin:0 0 6px; font-size:16px; }
  p{ margin:0; color:var(--secondary); font-size:14px; line-height:1.5; }
`;

export default function Homepage(): React.JSX.Element {
  const [role, setRole] = useState<'patient'|'clinician'>(
    (localStorage.getItem('role') as any) || 'patient'
  );
  const setAndSaveRole = (r:'patient'|'clinician') => { setRole(r); localStorage.setItem('role', r); };

  return (
    <>
      <Helmet>
        <title>MediSage — AI Insights for Better Care</title>
        <meta name="description" content="Unified data, risk alerts, and personalized insights for patients and clinicians." />
      </Helmet>

      <Navbar role={role} onRoleChange={setAndSaveRole} />

      <Page>
        {/* HERO */}
        <HeroGrid>
          <div>
            <Eyebrow>
              {role === 'patient'
                ? 'Welcome — get answers and guidance fast'
                : 'For clinicians — insight-driven, efficient care'}
            </Eyebrow>

            <Title>
              {role === 'patient'
                ? 'Understand your symptoms with AI guidance'
                : 'AI-powered insights for better clinical decisions'}
            </Title>

            <Subtitle>
              {role === 'patient'
                ? 'Answer a few questions and get likely causes, confidence scores, and next steps. Save or share reports with your doctor.'
                : 'See unified patient data at a glance, risk alerts for deteriorating patients, and suggested actions to optimize care and resources.'}
            </Subtitle>
          </div>

          <Art src={heroImg} alt="Illustration of clinicians and patient" />
        </HeroGrid>

        <Sections>
          <Card>
            <h3>Unified Patient Data</h3>
            <p>Clinical, lab, and lifestyle data in one view—no more silos.</p>
          </Card>
          <Card>
            <h3>Predictive Risk Alerts</h3>
            <p>Early warnings for high-risk or deteriorating patients.</p>
          </Card>
          <Card>
            <h3>Personalized Insights</h3>
            <p>Tailored guidance and recommendations for each individual.</p>
          </Card>
          <Card>
            <h3>Resource Optimization</h3>
            <p>Smarter scheduling and fewer bottlenecks across staff/equipment.</p>
          </Card>
        </Sections>
      </Page>
    </>
  );
}
