// App.tsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';

import PrivateRoute from 'components/routing/PrivateRoute';
import RoleRoute from 'components/routing/RoleRoute';

import Homepage from 'views/homepage';
import PatientHome from 'views/patienthome';
import ClinicianHome from 'views/clinicianhome';

import LoginPage from 'views/loginpage';
import RegisterPage from 'views/registerpage';
import ConfirmationPending from 'views/confirmationpage';

import ProfilePage from 'views/profilepage';
import DiagnosisFunction from 'views/diagnosis';
import ChatbotPage from 'views/chatbot';

import PatientsPage from 'views/patients';
import ClinicianDashboard from 'views/clinicianDashboard';

function App(): React.JSX.Element {
  return (
    <Routes>
      {/* public */}
      <Route path="/" element={<Homepage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/confirmation-pending" element={<ConfirmationPending />} />

      {/* patient-only (must be logged in unless BYPASS=true) */}
      <Route
        path="/patient-home"
        element={
          <PrivateRoute>
            <RoleRoute role="patient">
              <PatientHome />
            </RoleRoute>
          </PrivateRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <PrivateRoute>
            <RoleRoute role="patient">
              <ProfilePage />
            </RoleRoute>
          </PrivateRoute>
        }
      />
      <Route
        path="/diagnosis"
        element={
          <PrivateRoute>
            <RoleRoute role="patient">
              <DiagnosisFunction />
            </RoleRoute>
          </PrivateRoute>
        }
      />
      <Route
        path="/chatbot"
        element={
          <PrivateRoute>
            {/* If you want both roles to use Chatbot, drop RoleRoute and keep PrivateRoute only */}
            <RoleRoute role="patient">
              <ChatbotPage />
            </RoleRoute>
          </PrivateRoute>
        }
      />

      {/* clinician-only */}
      <Route
        path="/clinician-home"
        element={
          <PrivateRoute>
            <RoleRoute role="clinician">
              <ClinicianHome />
            </RoleRoute>
          </PrivateRoute>
        }
      />
      <Route
        path="/patients"
        element={
          <PrivateRoute>
            <RoleRoute role="clinician">
              <PatientsPage />
            </RoleRoute>
          </PrivateRoute>
        }
      />
      <Route
        path="/clinician-dashboard"
        element={
          <PrivateRoute>
            <RoleRoute role="clinician">
              <ClinicianDashboard />
            </RoleRoute>
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

export default App;
