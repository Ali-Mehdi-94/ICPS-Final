import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Crown, TrendingUp, Settings, Award, LayoutDashboard } from 'lucide-react';
import Layout from './components/Layout';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';

// Placeholder Dashboard Component
function DashboardPlaceholder({ title, icon: Icon, description }) {
  return (
    <div className="max-w-4xl">
      <div className="bg-surface border border-border rounded-xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-4 bg-primary/20 rounded-xl text-primary">
              <Icon size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-gray-100">{title}</h2>
              <p className="text-gray-400 text-sm mt-1">{description}</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-surface-hover/50 border border-border rounded-lg p-4">
                <div className="h-2 bg-border rounded w-3/4 mb-3" />
                <div className="h-8 bg-border/50 rounded" />
              </div>
            ))}
          </div>
          <p className="text-gray-500 text-sm mt-8 text-center">
            Dashboard content coming soon...
          </p>
        </div>
      </div>
    </div>
  );
}

// Home Dashboard
function HomeDashboard() {
  return (
    <DashboardPlaceholder
      title="Welcome to ICPS"
      icon={LayoutDashboard}
      description="Integrated Course Management System - Select a dashboard from the sidebar"
    />
  );
}

// CEO Dashboard
function CEODashboard() {
  return (
    <DashboardPlaceholder
      title="CEO Dashboard"
      icon={Crown}
      description="Executive overview and key performance indicators"
    />
  );
}

// Sales Dashboard
function SalesDashboard() {
  return (
    <DashboardPlaceholder
      title="Sales Dashboard"
      icon={TrendingUp}
      description="Sales performance and revenue analytics"
    />
  );
}

// Ops Dashboard
function OpsDashboard() {
  return (
    <DashboardPlaceholder
      title="Operations Dashboard"
      icon={Settings}
      description="Operations management and workflow tracking"
    />
  );
}

// ProQual Admin Dashboard
function ProQualDashboard() {
  return (
    <DashboardPlaceholder
      title="ProQual Administration"
      icon={Award}
      description="Quality assurance and certification management"
    />
  );
}

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
                    <Route path="/" element={<HomeDashboard />} />
                    <Route path="/ceo" element={<CEODashboard />} />
                    <Route path="/sales" element={<SalesDashboard />} />
                    <Route path="/ops" element={<OpsDashboard />} />
                    <Route path="/proqual" element={<ProQualDashboard />} />
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
