import React, { useState, useEffect } from 'react';
import { Crown, Users, BookOpen, DollarSign, AlertTriangle, CheckCircle, Loader2, Calendar, Clock } from 'lucide-react';
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

function DashboardCEO() {
  const [summary, setSummary] = useState(null);
  const [overduePayments, setOverduePayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [overdueLoading, setOverdueLoading] = useState(true);
  const [error, setError] = useState(null);
  const [markingPaid, setMarkingPaid] = useState(null);
  const [actionError, setActionError] = useState(null);

  const fetchOverduePayments = async () => {
    try {
      setOverdueLoading(true);
      const response = await api.get('/api/dashboard/payments/overdue/');
      setOverduePayments(response.data);
    } catch (err) {
      console.error('Failed to load overdue payments:', err);
    } finally {
      setOverdueLoading(false);
    }
  };

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/api/dashboard/ceo/summary/');
        setSummary(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
    fetchOverduePayments();
  }, []);

  const handleMarkPaid = async (installmentId) => {
    try {
      setMarkingPaid(installmentId);
      setActionError(null);
      await api.post(`/api/installments/${installmentId}/pay/`);
      // Refresh overdue payments list
      await fetchOverduePayments();
      // Refresh summary to update counts
      const summaryResponse = await api.get('/api/dashboard/ceo/summary/');
      setSummary(summaryResponse.data);
    } catch (err) {
      console.error('Failed to mark payment as paid:', err);
      setActionError(err.response?.data?.detail || 'Failed to mark payment as paid');
    } finally {
      setMarkingPaid(null);
    }
  };

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
            <Crown size={32} />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-gray-100">CEO Dashboard</h2>
            <p className="text-gray-400 text-sm mt-1">Executive overview and key performance indicators</p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <StatCard
          title="Total Students"
          value={summary.students_total}
          icon={Users}
        />
        <StatCard
          title="Total Registrations"
          value={summary.registrations_total}
          icon={BookOpen}
        />
        <StatCard
          title="Active Registrations"
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
          title="Overdue Payments"
          value={overduePayments.length}
          icon={Clock}
          variant={overduePayments.length > 0 ? 'error' : 'success'}
        />
      </div>

      {/* Revenue Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Alerts & Issues</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${summary.payments_overdue > 0 ? 'bg-error/20 text-error' : 'bg-success/20 text-success'}`}>
                  <DollarSign size={16} />
                </div>
                <span className="text-gray-300">Overdue Payments</span>
              </div>
              <span className={`font-bold ${summary.payments_overdue > 0 ? 'text-error' : 'text-success'}`}>
                {summary.payments_overdue}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${summary.units_overdue_total > 0 ? 'bg-warning/20 text-warning' : 'bg-success/20 text-success'}`}>
                  <BookOpen size={16} />
                </div>
                <span className="text-gray-300">Overdue Units</span>
              </div>
              <span className={`font-bold ${summary.units_overdue_total > 0 ? 'text-warning' : 'text-success'}`}>
                {summary.units_overdue_total}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${summary.ops_overdue_tasks > 0 ? 'bg-warning/20 text-warning' : 'bg-success/20 text-success'}`}>
                  <AlertTriangle size={16} />
                </div>
                <span className="text-gray-300">Overdue Ops Tasks</span>
              </div>
              <span className={`font-bold ${summary.ops_overdue_tasks > 0 ? 'text-warning' : 'text-success'}`}>
                {summary.ops_overdue_tasks}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Overdue Payments Table */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-100">Overdue Payments</h3>
          <div className="flex items-center gap-2">
            <Calendar size={16} className="text-gray-400" />
            <span className="text-gray-400 text-sm">{overduePayments.length} pending</span>
          </div>
        </div>

        {/* Action Error Message */}
        {actionError && (
          <div className="bg-error/10 border border-error/20 rounded-lg p-3 mb-4 flex items-center gap-2">
            <AlertTriangle size={16} className="text-error" />
            <span className="text-error text-sm">{actionError}</span>
            <button
              onClick={() => setActionError(null)}
              className="ml-auto text-error hover:text-error/80"
            >
              ×
            </button>
          </div>
        )}
        
        {overdueLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={24} className="animate-spin text-primary" />
          </div>
        ) : overduePayments.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <CheckCircle size={32} className="mx-auto mb-2 text-success" />
            <p>No overdue payments</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Student</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Provider</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Registered By</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium text-sm">Amount</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Due Date</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium text-sm">Days Overdue</th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium text-sm">Action</th>
                </tr>
              </thead>
              <tbody>
                {overduePayments.map((payment) => (
                  <tr key={payment.id} className="border-b border-border/50 hover:bg-surface-hover/50">
                    <td className="py-3 px-4 text-gray-100">{payment.student_name}</td>
                    <td className="py-3 px-4 text-gray-300">{payment.provider}</td>
                    <td className="py-3 px-4 text-gray-300">{payment.registered_by}</td>
                    <td className="py-3 px-4 text-right text-gray-100 font-medium">{formatCurrency(payment.amount)}</td>
                    <td className="py-3 px-4 text-gray-300">{payment.due_date}</td>
                    <td className="py-3 px-4 text-right">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        payment.days_overdue > 30 ? 'bg-error/20 text-error' : 
                        payment.days_overdue > 14 ? 'bg-warning/20 text-warning' : 
                        'bg-yellow-500/20 text-yellow-500'
                      }`}>
                        {payment.days_overdue} days
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => handleMarkPaid(payment.id)}
                        disabled={markingPaid === payment.id}
                        className="px-3 py-1.5 bg-success/20 text-success hover:bg-success/30 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {markingPaid === payment.id ? (
                          <Loader2 size={14} className="animate-spin" />
                        ) : (
                          'Mark Paid'
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardCEO;
