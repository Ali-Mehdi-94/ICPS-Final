import React, { useState, useEffect } from 'react';
import { TrendingUp, Users, BookOpen, DollarSign, AlertTriangle, CheckCircle, Gift, Loader2 } from 'lucide-react';
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

function DashboardSales() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/api/dashboard/sales/summary/');
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

  const collectionRate = summary.revenue_expected > 0 
    ? Math.round((summary.revenue_collected / summary.revenue_expected) * 100) 
    : 0;

  return (
    <div className="max-w-6xl">
      {/* Header */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-6 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
        <div className="relative z-10 flex items-center gap-4">
          <div className="p-4 bg-primary/20 rounded-xl text-primary">
            <TrendingUp size={32} />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-gray-100">Sales Dashboard</h2>
            <p className="text-gray-400 text-sm mt-1">Sales performance and revenue analytics</p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="My Students"
          value={summary.students_total}
          icon={Users}
        />
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
      </div>

      {/* Revenue & Progress Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Revenue Overview</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Expected Revenue</span>
              <span className="text-xl font-bold text-gray-100">{formatCurrency(summary.revenue_expected)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Collected Revenue</span>
              <span className="text-xl font-bold text-success">{formatCurrency(summary.revenue_collected)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Pending Revenue</span>
              <span className="text-xl font-bold text-warning">{formatCurrency(summary.revenue_pending)}</span>
            </div>
            <div className="h-2 bg-surface-hover rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all duration-500"
                style={{ width: `${collectionRate}%` }}
              />
            </div>
            <p className="text-gray-500 text-sm text-center">{collectionRate}% collection rate</p>
          </div>
        </div>

        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Student Progress</h3>
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
                    className="text-primary"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-100">{summary.avg_progress_percent}%</span>
                </div>
              </div>
            </div>
            <p className="text-gray-500 text-sm text-center">Average unit progress across all registrations</p>
            {summary.units_overdue_total > 0 && (
              <div className="flex items-center justify-center gap-2 text-warning">
                <AlertTriangle size={16} />
                <span className="text-sm">{summary.units_overdue_total} overdue units</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Payments & Incentives Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Payment Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-success/20 text-success">
                  <CheckCircle size={16} />
                </div>
                <span className="text-gray-300">Paid Installments</span>
              </div>
              <span className="font-bold text-success">{summary.payments_paid}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/20 text-primary">
                  <DollarSign size={16} />
                </div>
                <span className="text-gray-300">Pending Installments</span>
              </div>
              <span className="font-bold text-primary">{summary.payments_pending}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${summary.payments_overdue > 0 ? 'bg-error/20 text-error' : 'bg-success/20 text-success'}`}>
                  <AlertTriangle size={16} />
                </div>
                <span className="text-gray-300">Overdue Installments</span>
              </div>
              <span className={`font-bold ${summary.payments_overdue > 0 ? 'text-error' : 'text-success'}`}>
                {summary.payments_overdue}
              </span>
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
                  <span className="text-gray-500 text-xs">{summary.incentives_earned} incentives</span>
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
                  <span className="text-gray-500 text-xs">{summary.incentives_pending} incentives</span>
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

export default DashboardSales;
