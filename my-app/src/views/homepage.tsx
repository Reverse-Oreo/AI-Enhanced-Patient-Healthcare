import React from 'react';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';

const Wrap = styled.main`padding:32px 16px 56px;`;
const Hero = styled.section`
  max-width:1100px; margin:0 auto; display:grid; grid-template-columns:1.1fr .9fr;
  gap:24px; align-items:center;
  @media (max-width:900px){ grid-template-columns:1fr; }
`;
const H1 = styled.h1`
  font-size:64px; line-height:.95; margin:16px 0; letter-spacing:-.02em;
`;
const P = styled.p`color:#4b5563; max-width:60ch;`;

const GeneralHome: React.FC = () => (
  <>
    <Navbar />
    <Wrap>
      <Hero>
        <div>
          <H1>Understand your symptoms with AI guidance</H1>
          <P>Pick “Patient” or “Clinician” in the header to preview the experience, or log in to continue.</P>
        </div>
        <img src="/assets/hero.png" alt="" style={{width:'100%', height:'auto'}}/>
      </Hero>
    </Wrap>
  </>
);

export default GeneralHome;
