import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Loader2 } from 'lucide-react';
import DashboardCEO from './dashboards/DashboardCEO';
import DashboardSales from './dashboards/DashboardSales';
import DashboardOps from './dashboards/DashboardOps';
import DashboardProQual from './dashboards/DashboardProQual';

function Dashboard() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={32} className="animate-spin text-primary" />
      </div>
    );
  }

  // Determine user role from JWT claims
  // Possible roles: CEO, Sales, Ops, ProQual
  const userRole = user?.role?.toLowerCase();

  // Render dashboard based on user role
  switch (userRole) {
    case 'ceo':
      return <DashboardCEO />;
    case 'sales':
      return <DashboardSales />;
    case 'ops':
      return <DashboardOps />;
    case 'proqual':
    case 'proqual_admin':
      return <DashboardProQual />;
    default:
      // Default dashboard for users without a specific role
      return (
        <div className="max-w-4xl">
          <div className="bg-surface border border-border rounded-xl p-8 shadow-2xl relative overflow-hidden">
            <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-4 bg-primary/20 rounded-xl text-primary">
                  <LayoutDashboard size={32} />
                </div>
                <div>
                  <h2 className="text-2xl font-bold tracking-tight text-gray-100">Welcome to ICPS</h2>
                  <p className="text-gray-400 text-sm mt-1">
                    Integrated Course Management System - Select a dashboard from the sidebar
                  </p>
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
                {user?.username ? `Hello, ${user.username}!` : ''} Please use the sidebar to navigate to your dashboard.
              </p>
            </div>
          </div>
        </div>
      );
  }
}

export default Dashboard;
