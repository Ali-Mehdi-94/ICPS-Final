import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import DashboardCEO from './pages/dashboards/DashboardCEO';
import DashboardSales from './pages/dashboards/DashboardSales';
import DashboardOps from './pages/dashboards/DashboardOps';
import DashboardProQual from './pages/dashboards/DashboardProQual';
import RegistrationList from './pages/registrations/RegistrationList';
import NewRegistration from './pages/registrations/NewRegistration';
import RegistrationDetail from './pages/registrations/RegistrationDetail';
import OpsWorkspace from './pages/dashboards/OpsWorkspace';
import CourseManagement from './pages/settings/CourseManagement';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/ceo" element={<DashboardCEO />} />
                    <Route path="/sales" element={<DashboardSales />} />
                    <Route path="/ops" element={<DashboardOps />} />
                    <Route path="/proqual" element={<DashboardProQual />} />
                    <Route path="/registrations" element={<RegistrationList />} />
                    <Route path="/registrations/new" element={<NewRegistration />} />
                    <Route path="/registrations/:id" element={<RegistrationDetail />} />
                    <Route path="/ops/workspace" element={<OpsWorkspace />} />
                    <Route path="/settings/courses" element={<CourseManagement />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
