import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from 'contexts/AuthContext';
import { BYPASS } from 'utils/bypass';

type Role = 'patient' | 'clinician';

const RoleRoute = ({ role, children }: { role: Role; children: React.ReactNode }) => {
  const { loading, user } = useAuth();
  if (loading) return null;
  if (BYPASS) return <>{children}</>;
  if (user?.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
};

export default RoleRoute;
