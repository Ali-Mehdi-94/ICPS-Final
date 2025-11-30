import React, { useState, useEffect } from 'react';
import { Award, BookOpen, CheckCircle, AlertTriangle, Clock, Users, Loader2 } from 'lucide-react';
import api from '../../services/api';

function StatCard({ title, value, icon: Icon, subtitle, variant = 'default' }) {
  const variantStyles = {
    default: 'text-primary',
    success: 'text-success',
    warning: 'text-warning',
    error: 'text-error',
  };

  return (
    <div className="bg-surface border border-border rounded-xl p-6 relative overflow-hidden">
      <div className="absolute -top-10 -right-10 w-32 h-32 bg-primary/5 blur-2xl rounded-full pointer-events-none" />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-lg bg-surface-hover ${variantStyles[variant]}`}>
            <Icon size={20} />
          </div>
        </div>
        <p className="text-gray-400 text-sm mb-1">{title}</p>
        <p className="text-2xl font-bold text-gray-100">{value}</p>
        {subtitle && <p className="text-gray-500 text-xs mt-2">{subtitle}</p>}
      </div>
    </div>
  );
}

function DashboardProQual() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/api/dashboard/proqual/summary/');
        setSummary(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={32} className="animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-error/10 border border-error/20 rounded-xl p-6 text-error">
        <div className="flex items-center gap-3">
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  // Handle error from backend if ProQual provider not found
  if (summary.error) {
    return (
      <div className="max-w-6xl">
        <div className="bg-surface border border-border rounded-xl p-6 mb-6 relative overflow-hidden">
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
          <div className="relative z-10 flex items-center gap-4">
            <div className="p-4 bg-primary/20 rounded-xl text-primary">
              <Award size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-gray-100">ProQual Administration</h2>
              <p className="text-gray-400 text-sm mt-1">Quality assurance and certification management</p>
            </div>
          </div>
        </div>
        <div className="bg-warning/10 border border-warning/20 rounded-xl p-6 text-warning">
          <div className="flex items-center gap-3">
            <AlertTriangle size={20} />
            <span>{summary.error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl">
      {/* Header */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-6 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
        <div className="relative z-10 flex items-center gap-4">
          <div className="p-4 bg-primary/20 rounded-xl text-primary">
            <Award size={32} />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-gray-100">ProQual Administration</h2>
            <p className="text-gray-400 text-sm mt-1">Quality assurance and certification management</p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Total Registrations"
          value={summary.registrations_total}
          icon={BookOpen}
        />
        <StatCard
          title="Active"
          value={summary.registrations_active}
          icon={BookOpen}
          variant="success"
        />
        <StatCard
          title="Completed"
          value={summary.registrations_completed}
          icon={CheckCircle}
          variant="success"
        />
        <StatCard
          title="Avg Progress"
          value={`${summary.avg_progress_percent}%`}
          icon={Clock}
          variant="default"
        />
      </div>

      {/* Pending Actions Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Pending Actions</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${summary.registrations_pending_portal > 0 ? 'bg-warning/20 text-warning' : 'bg-success/20 text-success'}`}>
                  <Clock size={16} />
                </div>
                <span className="text-gray-300">Pending Portal Allocation</span>
              </div>
              <span className={`font-bold ${summary.registrations_pending_portal > 0 ? 'text-warning' : 'text-success'}`}>
                {summary.registrations_pending_portal}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${summary.registrations_pending_assignment > 0 ? 'bg-warning/20 text-warning' : 'bg-success/20 text-success'}`}>
                  <Users size={16} />
                </div>
                <span className="text-gray-300">Pending Ops Assignment</span>
              </div>
              <span className={`font-bold ${summary.registrations_pending_assignment > 0 ? 'text-warning' : 'text-success'}`}>
                {summary.registrations_pending_assignment}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${summary.units_overdue_total > 0 ? 'bg-error/20 text-error' : 'bg-success/20 text-success'}`}>
                  <AlertTriangle size={16} />
                </div>
                <span className="text-gray-300">Overdue Units</span>
              </div>
              <span className={`font-bold ${summary.units_overdue_total > 0 ? 'text-error' : 'text-success'}`}>
                {summary.units_overdue_total}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Progress Overview</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-center">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle 
                    cx="50" cy="50" r="40" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="8"
                    className="text-surface-hover"
                  />
                  <circle 
                    cx="50" cy="50" r="40" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={`${summary.avg_progress_percent * 2.51} 251`}
                    className="text-accent"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-100">{summary.avg_progress_percent}%</span>
                </div>
              </div>
            </div>
            <p className="text-gray-500 text-sm text-center">Average progress across all ProQual registrations</p>
          </div>
        </div>
      </div>

      {/* Ops Team Performance Section */}
      {summary.ops_performance && summary.ops_performance.length > 0 && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Ops Team Performance</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Ops Member</th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium text-sm">Registrations</th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium text-sm">Completed</th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium text-sm">Avg Progress</th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium text-sm">Overdue Units</th>
                </tr>
              </thead>
              <tbody>
                {summary.ops_performance.map((ops, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-surface-hover/30">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center border border-border">
                          <Users size={14} className="text-gray-300" />
                        </div>
                        <span className="text-gray-100">{ops.ops_name}</span>
                      </div>
                    </td>
                    <td className="text-center py-3 px-4 text-gray-300">{ops.total_registrations}</td>
                    <td className="text-center py-3 px-4 text-success">{ops.completed_registrations}</td>
                    <td className="text-center py-3 px-4">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-16 h-2 bg-surface-hover rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-accent rounded-full transition-all duration-500"
                            style={{ width: `${ops.avg_progress}%` }}
                          />
                        </div>
                        <span className="text-gray-300 text-sm">{ops.avg_progress}%</span>
                      </div>
                    </td>
                    <td className="text-center py-3 px-4">
                      <span className={ops.overdue_units > 0 ? 'text-error' : 'text-success'}>
                        {ops.overdue_units}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardProQual;
