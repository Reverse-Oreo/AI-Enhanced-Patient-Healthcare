import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from 'contexts/AuthContext';
import { BYPASS } from 'utils/bypass';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { loading, loggedIn } = useAuth();
  if (loading) return null;                 // or a spinner
  if (!loggedIn && !BYPASS) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

export default PrivateRoute;
