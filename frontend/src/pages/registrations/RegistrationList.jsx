import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  Plus, 
  Loader2, 
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign
} from 'lucide-react';
import api from '../../services/api';

function RegistrationList() {
  const navigate = useNavigate();
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRegistrations = async () => {
      try {
        const response = await api.get('/api/registrations/');
        setRegistrations(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load registrations');
      } finally {
        setLoading(false);
      }
    };

    fetchRegistrations();
  }, []);

  const getStatusBadge = (registration) => {
    // Determine status based on unit progress
    const progress = registration.unit_progress_percent || 0;
    if (progress >= 100) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-success/20 text-success">
          <CheckCircle size={12} />
          Completed
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-primary/20 text-primary">
        <Clock size={12} />
        Active
      </span>
    );
  };

  const getFinancialStatus = (registration) => {
    const paymentProgress = registration.payment_progress_percent || 0;
    const paymentsOverdue = registration.payments_overdue || 0;
    
    if (paymentProgress >= 100) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-success/20 text-success">
          <DollarSign size={12} />
          Paid
        </span>
      );
    }
    if (paymentsOverdue > 0) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-error/20 text-error">
          <AlertTriangle size={12} />
          Overdue
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-warning/20 text-warning">
        <Clock size={12} />
        Pending
      </span>
    );
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

  return (
    <div className="max-w-6xl">
      {/* Header */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-6 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-primary/20 rounded-xl text-primary">
              <BookOpen size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-gray-100">Student Registrations</h2>
              <p className="text-gray-400 text-sm mt-1">Manage student course registrations</p>
            </div>
          </div>
          <Link
            to="/registrations/new"
            className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover rounded-lg text-white font-medium transition-colors"
          >
            <Plus size={18} />
            New Registration
          </Link>
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        {registrations.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <BookOpen size={48} className="mx-auto mb-4 opacity-50" />
            <p>No registrations found</p>
            <Link 
              to="/registrations/new" 
              className="inline-flex items-center gap-2 mt-4 text-primary hover:underline"
            >
              <Plus size={16} />
              Create your first registration
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-surface-hover border-b border-border">
                <tr>
                  <th className="text-left px-6 py-4 text-sm font-semibold text-gray-300">
                    Student Name
                  </th>
                  <th className="text-left px-6 py-4 text-sm font-semibold text-gray-300">
                    Course
                  </th>
                  <th className="text-left px-6 py-4 text-sm font-semibold text-gray-300">
                    Status
                  </th>
                  <th className="text-left px-6 py-4 text-sm font-semibold text-gray-300">
                    Progress
                  </th>
                  <th className="text-left px-6 py-4 text-sm font-semibold text-gray-300">
                    Financial Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {registrations.map((registration) => (
                  <tr 
                    key={registration.id} 
                    className="hover:bg-surface-hover/50 transition-colors cursor-pointer"
                    onClick={() => navigate(`/registrations/${registration.id}`)}
                  >
                    <td className="px-6 py-4">
                      <span className="text-gray-100 font-medium hover:text-primary transition-colors">
                        {registration.student_name}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-gray-100">
                        {registration.provider_name}
                      </div>
                      <div className="text-gray-400 text-sm">
                        {registration.field_name} • Level {registration.level_name}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(registration)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-surface-hover rounded-full overflow-hidden min-w-[80px]">
                          <div 
                            className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all duration-500"
                            style={{ width: `${registration.unit_progress_percent || 0}%` }}
                          />
                        </div>
                        <span className="text-gray-300 text-sm min-w-[40px]">
                          {registration.unit_progress_percent || 0}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getFinancialStatus(registration)}
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

export default RegistrationList;
