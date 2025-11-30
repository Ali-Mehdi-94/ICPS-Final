import React, { useState, useEffect } from 'react';
import { Settings, BookOpen, CheckCircle, AlertTriangle, Clock, Gift, Calendar, Loader2 } from 'lucide-react';
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

function DashboardOps() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/api/dashboard/ops/summary/');
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

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const taskCompletionRate = summary.tasks_total > 0 
    ? Math.round((summary.tasks_done / summary.tasks_total) * 100) 
    : 0;

  return (
    <div className="max-w-6xl">
      {/* Header */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-6 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
        <div className="relative z-10 flex items-center gap-4">
          <div className="p-4 bg-primary/20 rounded-xl text-primary">
            <Settings size={32} />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-gray-100">Operations Dashboard</h2>
            <p className="text-gray-400 text-sm mt-1">Operations management and workflow tracking</p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="My Registrations"
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
          title="Upcoming Deadlines"
          value={summary.upcoming_deadlines}
          icon={Calendar}
          variant={summary.upcoming_deadlines > 0 ? 'warning' : 'default'}
          subtitle="In next 7 days"
        />
      </div>

      {/* Tasks & Progress Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Task Overview</h3>
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
                    strokeDasharray={`${taskCompletionRate * 2.51} 251`}
                    className="text-primary"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-100">{taskCompletionRate}%</span>
                </div>
              </div>
            </div>
            <p className="text-gray-500 text-sm text-center">{summary.tasks_done} of {summary.tasks_total} tasks completed</p>
          </div>
        </div>

        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Task Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-success/20 text-success">
                  <CheckCircle size={16} />
                </div>
                <span className="text-gray-300">Completed Tasks</span>
              </div>
              <span className="font-bold text-success">{summary.tasks_done}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/20 text-primary">
                  <Clock size={16} />
                </div>
                <span className="text-gray-300">Pending Tasks</span>
              </div>
              <span className="font-bold text-primary">{summary.tasks_pending}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-warning/20 text-warning">
                  <Calendar size={16} />
                </div>
                <span className="text-gray-300">Due in 7 Days</span>
              </div>
              <span className="font-bold text-warning">{summary.tasks_due_7_days}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${summary.tasks_overdue > 0 ? 'bg-error/20 text-error' : 'bg-success/20 text-success'}`}>
                  <AlertTriangle size={16} />
                </div>
                <span className="text-gray-300">Overdue Tasks</span>
              </div>
              <span className={`font-bold ${summary.tasks_overdue > 0 ? 'text-error' : 'text-success'}`}>
                {summary.tasks_overdue}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Units & Incentives Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Unit Progress</h3>
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
                    strokeDasharray={`${summary.avg_unit_progress_percent * 2.51} 251`}
                    className="text-accent"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-100">{summary.avg_unit_progress_percent}%</span>
                </div>
              </div>
            </div>
            <p className="text-gray-500 text-sm text-center">Average unit progress</p>
            <div className="flex justify-center gap-6 text-sm">
              <div className="text-center">
                <p className="text-gray-400">Done</p>
                <p className="text-success font-bold">{summary.units_done}</p>
              </div>
              <div className="text-center">
                <p className="text-gray-400">Total</p>
                <p className="text-gray-100 font-bold">{summary.units_total}</p>
              </div>
              <div className="text-center">
                <p className="text-gray-400">Overdue</p>
                <p className={`font-bold ${summary.units_overdue > 0 ? 'text-error' : 'text-success'}`}>{summary.units_overdue}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Incentives</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-success/20 text-success">
                  <Gift size={16} />
                </div>
                <div>
                  <span className="text-gray-300 block">Earned</span>
                  <span className="text-gray-500 text-xs">{summary.incentives_earned_count} incentives</span>
                </div>
              </div>
              <span className="font-bold text-success">{formatCurrency(summary.incentives_amount_earned)}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-warning/20 text-warning">
                  <Gift size={16} />
                </div>
                <div>
                  <span className="text-gray-300 block">Pending</span>
                  <span className="text-gray-500 text-xs">{summary.incentives_pending_count} incentives</span>
                </div>
              </div>
              <span className="font-bold text-warning">{formatCurrency(summary.incentives_amount_pending)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardOps;
