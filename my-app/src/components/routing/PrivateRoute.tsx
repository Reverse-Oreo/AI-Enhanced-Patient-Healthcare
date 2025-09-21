import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from 'contexts/AuthContext';

interface PrivateRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
  requiredRole?: 'patient' | 'clinician' | 'nurse';
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ 
  children, 
  redirectTo = '/login',
  requiredRole 
}) => {
  const { loggedIn, hasRole, userRole } = useAuth();
  const location = useLocation();

  if (!loggedIn) {
    const params = new URLSearchParams();
    if (requiredRole) params.set('role', requiredRole);
    params.set('next', location.pathname);
    
    return <Navigate to={`${redirectTo}?${params.toString()}`} replace />;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    // Redirect to appropriate home based on actual role
    const homeRoute = userRole === 'clinician' ? '/clinician-home' :
                     userRole === 'nurse' ? '/nurse-home' : '/patient-home';
    return <Navigate to={homeRoute} replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;