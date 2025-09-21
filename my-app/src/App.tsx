import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from 'contexts/AuthContext';
import GeneralHome from 'views/homepage';
import PatientHome from 'views/patienthome';
import ClinicianHome from 'views/clinicianhome';
import LoginPage from 'views/loginpage';
import RegisterPage from 'views/registerpage';
import ProfilePage from 'views/profilepage';
import DiagnosisPage from 'views/diagnosis';
import Patients from 'views/patients';
import ClinicianDashboard from 'views/clinicianDashboard';
import PrivateRoute from 'components/routing/PrivateRoute';
import RoleRoute from 'components/routing/RoleRoute';
import NurseHome from 'views/nursehome';
import NurseWorklist from 'views/nurse/worklist';
import NursePatients from 'views/nurse/patients';
import ConfirmationPending from './views/confirmationpage';
import AdminInvite from './pages/adminInvites'
import PatientChart from './views/PatientChart';

const App: React.FC = () => (
  <AuthProvider>
    <Routes>

      <Route path="/admin-invite" element={<AdminInvite />} />
      
      {/* Neutral marketing/landing */}
      <Route path="/" element={<GeneralHome />} />

      {/* Role homes (public, but look different) */}
      <Route path="/patient-home" element={<PatientHome />} />
      <Route path="/clinician-home" element={<ClinicianHome />} />
      <Route path="/nurse-home" element={<NurseHome />} />

      {/* Auth */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Patient-only area */}
      <Route
        path="/profile"
        element={
          <PrivateRoute>
              <ProfilePage />
          </PrivateRoute>
        }
      />
      <Route
        path="/diagnosis"
        element={
          <PrivateRoute requiredRole="patient">
            <RoleRoute role="patient">
              <DiagnosisPage />
            </RoleRoute>
          </PrivateRoute>
        }
      />

      {/* Nurse-only area */}
      {/* <Route
        path="/nurse-patients"
        element={
          <PrivateRoute requiredRole="nurse">
            <RoleRoute role="nurse">
              <NursePatients />
            </RoleRoute>
          </PrivateRoute>
        }
      /> */}

      {/* To this (temporarily remove protection): */}
      <Route path="/nurse-patients" element={<NursePatients />} />
      <Route
        path="/nurse-worklist"
        element={
          <PrivateRoute requiredRole="nurse">
            <RoleRoute role="nurse">
              <NurseWorklist />
            </RoleRoute>
          </PrivateRoute>
        }
      />

      {/* Clinician-only area */}
      {/* <Route
        path="/patients"
        element={
          <PrivateRoute requiredRole="clinician">
            <RoleRoute role="clinician">
              <Patients />
            </RoleRoute>
          </PrivateRoute>
        }
      /> */}

      <Route path="/patients" element={<Patients />} />

      <Route path="/patient/:id" element={<PatientChart />} />

      {/* <Route
        path="/clinicianDashboard"
        element={
          <PrivateRoute requiredRole="clinician">
            <RoleRoute role="clinician">
              <ClinicianDashboard />
            </RoleRoute>
          </PrivateRoute>
        }
      /> */}

      <Route path="/clinicianDashboard" element={<ClinicianDashboard />} />


      <Route
        path="/confirmation-pending"
        element={<ConfirmationPending />}
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </AuthProvider>
);

export default App;