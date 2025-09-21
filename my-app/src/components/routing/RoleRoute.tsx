import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from 'contexts/AuthContext';
import type { Role } from 'types/auth';

interface RoleRouteProps {
  children: React.ReactNode;
  role: Role;
  fallback?: string;
}

const RoleRoute: React.FC<RoleRouteProps> = ({ 
  children, 
  role, 
  fallback = '/login' 
}) => {
  const { user, userRole, loggedIn, hasRole } = useAuth();
  const location = useLocation();

  if (!loggedIn) {
    return <Navigate to={`${fallback}?role=${role}&next=${location.pathname}`} replace />;
  }

  if (!hasRole(role)) {
    // Redirect to appropriate home based on actual role
    const homeRoute = userRole === 'clinician' ? '/clinician-home' :
                     userRole === 'nurse' ? '/nurse-home' : '/patient-home';
    return <Navigate to={homeRoute} replace />;
  }

  return <>{children}</>;
};

export default RoleRoute;