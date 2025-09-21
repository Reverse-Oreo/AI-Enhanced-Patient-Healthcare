import React from 'react';
import styled from 'styled-components';
import { useAuth } from 'contexts/AuthContext';

const DashboardContainer = styled.div`
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const DashboardIframe = styled.iframe`
  width: 100%;
  height: 100%;
  border: none;
  background: #f5f5f5;
  flex: 1;
`;

const LoadingMessage = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-size: 1.2rem;
  color: #666;
`;

interface ExternalDashboardProps {
  role?: 'nurse' | 'clinician';
}

const ExternalDashboard: React.FC<ExternalDashboardProps> = ({ role }) => {
  const { user } = useAuth();
  
  const dashboardUrl = 'http://healthcare-dashboard-ai.s3-website-us-east-1.amazonaws.com';
  
  // Add user context as query parameters
  const urlWithParams = `${dashboardUrl}?role=${role || user?.role}&user_id=${user?.id}&name=${encodeURIComponent(user?.name || '')}`;
  
  return (
    <DashboardContainer>
      <DashboardIframe
        src={urlWithParams}
        title="Healthcare Dashboard"
        allow="fullscreen"
        loading="lazy"
        onError={() => console.error('Failed to load dashboard')}
      />
    </DashboardContainer>
  );
};

export default ExternalDashboard;