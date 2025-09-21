import React from 'react';
import { Helmet } from 'react-helmet';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';

const Page = styled.main`
  max-width: 1320px;
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
  font-size: clamp(36px, 6vw, 64px);
  line-height: 1.05;
  margin: 12px 0 16px;
  letter-spacing: -0.02em;
`;

const P = styled.p`
  color: #4b5563;
  max-width: 62ch;
  font-size: clamp(14px, 1.6vw, 18px);
`;

const Art = styled.img`
  width: 100%;
  max-width: 600px;
  height: auto;
  justify-self: center;
`;

const Sections = styled.section`
  margin-top: 8px;
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
`;

const Card = styled.div`
  background: #fff;
  border: 1px solid #eef0f3;
  border-radius: 16px;
  padding: 16px 18px;
  h3 { margin: 0 0 6px; font-size: 16px; }
  p  { margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5; }
`;

export default function Homepage(): React.JSX.Element {
  return (
    <>
      <Helmet>
        <title>MediSage — AI Insights for Better Care</title>
        <meta
          name="description"
          content="Unified data, risk alerts, and personalized insights for patients and doctors."
        />
      </Helmet>

      <Navbar />

      <Page>
        {/* HERO (newer layout) */}
        <Hero>
          <div>
            <H1>Understand your symptoms with AI guidance</H1>
            <P>
              Pick “Patient” or “Clinician” in the header to preview the experience, or log in to continue.
              See unified patient data at a glance, risk alerts for deteriorating patients, and suggested
              actions to optimize care and resources.
            </P>
          </div>
          <Art src="/assets/hero.png" alt="Illustration of clinicians and patient" />
        </Hero>

        {/* FEATURE CARDS (merged from the other homepage) */}
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
