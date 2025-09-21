import React from 'react';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import ExternalDashboard from 'components/dashboard/ExternalDashboard';

const DashboardWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
`;

const DashboardContent = styled.div`
  flex: 1;
  overflow: hidden;
`;

interface DashboardPageProps {
  role?: 'nurse' | 'clinician';
}

const DashboardPage: React.FC<DashboardPageProps> = ({ role }) => {
  return (
    <DashboardWrapper>
      <Navbar />
      <DashboardContent>
        <ExternalDashboard role={role} />
      </DashboardContent>
    </DashboardWrapper>
  );
};

export default DashboardPage;