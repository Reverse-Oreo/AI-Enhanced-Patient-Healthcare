import React from 'react';
import { Hero } from 'components/homepage/Hero';
import { Features } from 'components/homepage/Features';
import { FeaturesGallery } from 'components/homepage/FeaturesGallery';
import { Cta } from 'components/homepage/Cta';
import { Partners } from 'components/homepage/Partners';
import { Button } from 'components/common/Button';
import { useNavigate } from 'react-router-dom';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div>
      <Hero />
      <Features />
      <FeaturesGallery />
      <Partners />
      <Cta />
      <div style={{ textAlign: 'center', margin: 'var(--spacing-xl) 0' }}>
        <Button
          variant="primary"
          size="lg"
          onClick={() => navigate('/diagnosis')}
        >
          Start Diagnosis
        </Button>
      </div>
    </div>
  );
};