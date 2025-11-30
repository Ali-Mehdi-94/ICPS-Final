import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft,
  User, 
  Mail, 
  Phone, 
  BookOpen,
  CheckCircle,
  Clock,
  AlertTriangle,
  Loader2,
  DollarSign,
  FileText,
  ClipboardList
} from 'lucide-react';
import api from '../../services/api';

function RegistrationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [registration, setRegistration] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tasksLoading, setTasksLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingTaskId, setUpdatingTaskId] = useState(null);

  useEffect(() => {
    const fetchRegistration = async () => {
      try {
        const response = await api.get(`/api/registrations/${id}/`);
        setRegistration(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load registration details');
      } finally {
        setLoading(false);
      }
    };

    const fetchTasks = async () => {
      try {
        const response = await api.get(`/api/registrations/${id}/tasks/`);
        setTasks(response.data);
      } catch (err) {
        // Tasks may not exist yet, so we don't set error
        console.log('No tasks found or error fetching tasks');
      } finally {
        setTasksLoading(false);
      }
    };

    fetchRegistration();
    fetchTasks();
  }, [id]);

  const handleTaskStatusChange = async (taskId, newStatus) => {
    setUpdatingTaskId(taskId);
    try {
      await api.patch(`/api/tasks/${taskId}/`, { status: newStatus });
      setTasks(tasks.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ));
    } catch (err) {
      console.error('Failed to update task status:', err);
    } finally {
      setUpdatingTaskId(null);
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
        <button
          onClick={() => navigate('/registrations')}
          className="mt-4 flex items-center gap-2 text-gray-400 hover:text-gray-100 transition-colors"
        >
          <ArrowLeft size={18} />
          Back to Registrations
        </button>
      </div>
    );
  }

  const unitProgress = registration?.unit_progress_percent || 0;
  const paymentProgress = registration?.payment_progress_percent || 0;

  return (
    <div className="max-w-6xl">
      {/* Header */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-6 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
        <div className="relative z-10 flex items-center gap-4">
          <button
            onClick={() => navigate('/registrations')}
            className="p-2 hover:bg-surface-hover rounded-lg text-gray-400 hover:text-gray-100 transition-colors"
          >
            <ArrowLeft size={24} />
          </button>
          <div className="p-4 bg-primary/20 rounded-xl text-primary">
            <BookOpen size={32} />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-gray-100">
              Registration Details
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              {registration?.student_name} - {registration?.provider_name}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Student Information */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary/20 rounded-lg text-primary">
              <User size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Student Information</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-3 bg-surface-hover/50 rounded-lg">
              <User size={18} className="text-gray-500" />
              <div>
                <p className="text-gray-400 text-xs">Name</p>
                <p className="text-gray-100 font-medium">{registration?.student_name || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-surface-hover/50 rounded-lg">
              <Mail size={18} className="text-gray-500" />
              <div>
                <p className="text-gray-400 text-xs">Email</p>
                <p className="text-gray-100 font-medium">{registration?.student_email || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-surface-hover/50 rounded-lg">
              <Phone size={18} className="text-gray-500" />
              <div>
                <p className="text-gray-400 text-xs">Phone</p>
                <p className="text-gray-100 font-medium">{registration?.student_phone || 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Course Details */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-accent/20 rounded-lg text-accent">
              <BookOpen size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Course Details</h3>
          </div>
          
          <div className="space-y-4">
            <div className="p-3 bg-surface-hover/50 rounded-lg">
              <p className="text-gray-400 text-xs">Provider</p>
              <p className="text-gray-100 font-medium">{registration?.provider_name || 'N/A'}</p>
            </div>
            <div className="p-3 bg-surface-hover/50 rounded-lg">
              <p className="text-gray-400 text-xs">Field</p>
              <p className="text-gray-100 font-medium">{registration?.field_name || 'N/A'}</p>
            </div>
            <div className="p-3 bg-surface-hover/50 rounded-lg">
              <p className="text-gray-400 text-xs">Level</p>
              <p className="text-gray-100 font-medium">Level {registration?.level_name || 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* Units Progress */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-success/20 rounded-lg text-success">
              <ClipboardList size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Units Progress</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Completed Units</span>
              <span className="text-gray-100 font-bold">{unitProgress}%</span>
            </div>
            <div className="h-3 bg-surface-hover rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-success to-accent rounded-full transition-all duration-500"
                style={{ width: `${unitProgress}%` }}
              />
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">
                {registration?.units_completed || 0} of {registration?.units_total || 0} units
              </span>
              {registration?.units_overdue > 0 && (
                <span className="text-error flex items-center gap-1">
                  <AlertTriangle size={14} />
                  {registration.units_overdue} overdue
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Payment Progress */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-warning/20 rounded-lg text-warning">
              <DollarSign size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Payment Progress</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Payment Status</span>
              <span className="text-gray-100 font-bold">{paymentProgress}%</span>
            </div>
            <div className="h-3 bg-surface-hover rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${
                  paymentProgress >= 100 
                    ? 'bg-gradient-to-r from-success to-success' 
                    : 'bg-gradient-to-r from-warning to-primary'
                }`}
                style={{ width: `${paymentProgress}%` }}
              />
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">
                {registration?.payments_completed || 0} of {registration?.payments_total || 0} payments
              </span>
              {registration?.payments_overdue > 0 && (
                <span className="text-error flex items-center gap-1">
                  <AlertTriangle size={14} />
                  {registration.payments_overdue} overdue
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Task List / Timeline Section */}
      <div className="bg-surface border border-border rounded-xl p-6 mt-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-primary/20 rounded-lg text-primary">
            <FileText size={20} />
          </div>
          <h3 className="text-lg font-semibold text-gray-100">Task List</h3>
        </div>

        {tasksLoading ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 size={24} className="animate-spin text-primary" />
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <FileText size={48} className="mx-auto mb-4 opacity-50" />
            <p>No tasks found for this registration</p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <div 
                key={task.id} 
                className="flex items-center justify-between p-4 bg-surface-hover/50 rounded-lg border border-border hover:border-primary/30 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${
                    task.status === 'DONE' 
                      ? 'bg-success/20 text-success' 
                      : 'bg-warning/20 text-warning'
                  }`}>
                    {task.status === 'DONE' ? <CheckCircle size={18} /> : <Clock size={18} />}
                  </div>
                  <div>
                    <p className="text-gray-100 font-medium">{task.name || task.title}</p>
                    <p className="text-gray-500 text-sm">
                      {task.type || 'Task'} 
                      {task.due_date && ` • Due: ${new Date(task.due_date).toLocaleDateString()}`}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  {task.is_overdue && (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-error/20 text-error">
                      Overdue
                    </span>
                  )}
                  <select
                    value={task.status}
                    onChange={(e) => handleTaskStatusChange(task.id, e.target.value)}
                    disabled={updatingTaskId === task.id}
                    className="bg-background border border-border rounded-lg px-3 py-1.5 text-sm text-gray-100 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors disabled:opacity-50"
                  >
                    <option value="PENDING">Pending</option>
                    <option value="DONE">Done</option>
                  </select>
                  {updatingTaskId === task.id && (
                    <Loader2 size={16} className="animate-spin text-primary" />
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default RegistrationDetail;
