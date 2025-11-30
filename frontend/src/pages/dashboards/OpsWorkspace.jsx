import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Settings, 
  BookOpen, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Calendar, 
  Loader2,
  User,
  ChevronRight,
  Bell
} from 'lucide-react';
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

function OpsWorkspace() {
  const [students, setStudents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [studentsRes, summaryRes] = await Promise.all([
          api.get('/api/dashboard/ops/students/'),
          api.get('/api/dashboard/ops/summary/')
        ]);
        setStudents(studentsRes.data);
        setSummary(summaryRes.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load workspace data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getDeadlineStatus = (student) => {
    if (student.overdue_tasks > 0 || student.overdue_units > 0) {
      return 'overdue';
    }
    if (student.upcoming_deadlines > 0) {
      return 'upcoming';
    }
    return 'ontrack';
  };

  const getDeadlineBadge = (student) => {
    const status = getDeadlineStatus(student);
    
    if (status === 'overdue') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-error/20 text-error">
          <AlertTriangle size={12} />
          Overdue
        </span>
      );
    }
    if (status === 'upcoming') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-warning/20 text-warning">
          <Clock size={12} />
          Upcoming Deadline
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-success/20 text-success">
        <CheckCircle size={12} />
        On Track
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

  // Calculate overdue and upcoming counts
  const overdueCount = students.filter(s => 
    s.overdue_tasks > 0 || s.overdue_units > 0
  ).length;
  const upcomingCount = students.filter(s => 
    s.upcoming_deadlines > 0 && !(s.overdue_tasks > 0 || s.overdue_units > 0)
  ).length;

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
            <h2 className="text-2xl font-bold tracking-tight text-gray-100">Ops Workspace</h2>
            <p className="text-gray-400 text-sm mt-1">Manage your assigned students and track progress</p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Assigned Students"
          value={students.length}
          icon={User}
        />
        <StatCard
          title="On Track"
          value={students.length - overdueCount - upcomingCount}
          icon={CheckCircle}
          variant="success"
        />
        <StatCard
          title="Upcoming Deadlines"
          value={upcomingCount}
          icon={Calendar}
          variant={upcomingCount > 0 ? 'warning' : 'default'}
        />
        <StatCard
          title="Overdue"
          value={overdueCount}
          icon={AlertTriangle}
          variant={overdueCount > 0 ? 'error' : 'success'}
        />
      </div>

      {/* Alerts Section */}
      {overdueCount > 0 && (
        <div className="bg-error/10 border border-error/20 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-3">
            <Bell size={20} className="text-error" />
            <span className="text-error font-medium">
              {overdueCount} student{overdueCount > 1 ? 's' : ''} with overdue tasks or units
            </span>
          </div>
        </div>
      )}

      {/* Student List */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="p-4 border-b border-border bg-surface-hover/50">
          <h3 className="text-lg font-semibold text-gray-100">Assigned Students</h3>
        </div>
        
        {students.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <User size={48} className="mx-auto mb-4 opacity-50" />
            <p>No students assigned to you</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {students.map((student) => (
              <Link
                key={student.registration_id}
                to={`/registrations/${student.registration_id}`}
                className="flex items-center justify-between p-4 hover:bg-surface-hover/50 transition-colors group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center border border-border">
                    <User size={18} className="text-gray-300" />
                  </div>
                  <div>
                    <p className="text-gray-100 font-medium group-hover:text-primary transition-colors">
                      {student.student_name}
                    </p>
                    <p className="text-gray-500 text-sm">
                      {student.provider_name} • {student.field_name} • Level {student.level_name}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  {/* Progress Bar */}
                  <div className="hidden md:flex items-center gap-3">
                    <div className="flex-1 h-2 bg-surface-hover rounded-full overflow-hidden min-w-[80px]">
                      <div 
                        className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all duration-500"
                        style={{ width: `${student.unit_progress_percent || 0}%` }}
                      />
                    </div>
                    <span className="text-gray-400 text-sm min-w-[40px]">
                      {student.unit_progress_percent || 0}%
                    </span>
                  </div>
                  
                  {getDeadlineBadge(student)}
                  
                  <ChevronRight size={18} className="text-gray-500 group-hover:text-primary transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Upcoming Deadlines Section */}
      {summary && summary.upcoming_deadlines > 0 && (
        <div className="bg-surface border border-border rounded-xl p-6 mt-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-warning/20 rounded-lg text-warning">
              <Calendar size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Upcoming Deadlines (Next 7 Days)</h3>
          </div>
          
          <div className="space-y-3">
            {students
              .filter(s => s.upcoming_deadlines > 0)
              .map((student) => (
                <Link
                  key={student.registration_id}
                  to={`/registrations/${student.registration_id}`}
                  className="flex items-center justify-between p-3 bg-surface-hover/50 rounded-lg border border-border hover:border-warning/30 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Clock size={18} className="text-warning" />
                    <div>
                      <p className="text-gray-100 font-medium">{student.student_name}</p>
                      <p className="text-gray-500 text-sm">
                        {student.upcoming_deadlines} deadline{student.upcoming_deadlines > 1 ? 's' : ''} approaching
                      </p>
                    </div>
                  </div>
                  <ChevronRight size={18} className="text-gray-500" />
                </Link>
              ))
            }
          </div>
        </div>
      )}
    </div>
  );
}

export default OpsWorkspace;
