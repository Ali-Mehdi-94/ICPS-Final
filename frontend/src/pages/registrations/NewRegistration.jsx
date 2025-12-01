import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  Mail, 
  Phone, 
  Calendar,
  BookOpen,
  DollarSign,
  Save,
  ArrowLeft,
  Loader2,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import api from '../../services/api';

function NewRegistration() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Dropdown options
  const [providers, setProviders] = useState([]);
  const [fields, setFields] = useState([]);
  const [levels, setLevels] = useState([]);
  const [loadingOptions, setLoadingOptions] = useState(true);

  // Qualification type options
  const qualificationTypes = [
    { value: 'award', label: 'Award' },
    { value: 'certificate', label: 'Certificate' },
    { value: 'diploma', label: 'Diploma' },
    { value: 'extended', label: 'Extended Diploma' },
  ];

  // Form data
  const [formData, setFormData] = useState({
    // Student Info
    name: '',
    email: '',
    phone: '',
    dob: '',
    // Course Selection
    provider: '',
    field: '',
    level: '',
    qualification_type: '',
    // Financials
    total_fee: '',
    upfront_payment_percent: 50,
    remaining_months: 2,
  });

  // Fetch initial dropdown options (providers and fields)
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [providersRes, fieldsRes] = await Promise.all([
          api.get('/api/providers/'),
          api.get('/api/fields/'),
        ]);
        setProviders(providersRes.data);
        setFields(fieldsRes.data);
      } catch (err) {
        setError('Failed to load form options');
      } finally {
        setLoadingOptions(false);
      }
    };

    fetchOptions();
  }, []);

  // Fetch levels when provider and field are selected
  useEffect(() => {
    const fetchLevels = async () => {
      if (formData.provider && formData.field) {
        try {
          const levelsRes = await api.get('/api/levels/', {
            params: {
              provider: formData.provider,
              field: formData.field,
            }
          });
          setLevels(levelsRes.data);
        } catch (err) {
          setLevels([]);
        }
      } else if (formData.provider) {
        // If only provider is selected, fetch all levels (fallback)
        try {
          const levelsRes = await api.get('/api/levels/');
          setLevels(levelsRes.data);
        } catch (err) {
          setLevels([]);
        }
      } else {
        setLevels([]);
      }
    };

    fetchLevels();
  }, [formData.provider, formData.field]);

  // Filter fields based on selected provider
  const filteredFields = formData.provider 
    ? fields.filter(f => f.provider === parseInt(formData.provider))
    : fields;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
      // Reset dependent fields when provider changes
      ...(name === 'provider' ? { field: '', level: '' } : {}),
      // Reset level when field changes
      ...(name === 'field' ? { level: '' } : {}),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // First create the student
      const studentResponse = await api.post('/api/students/', {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        dob: formData.dob,
      });

      const studentId = studentResponse.data.id;

      // Then create the registration
      await api.post('/api/registrations/', {
        student: studentId,
        provider: parseInt(formData.provider),
        field: parseInt(formData.field),
        level: parseInt(formData.level),
        qualification_type: formData.qualification_type || null,
        total_fee: formData.total_fee ? parseFloat(formData.total_fee) : null,
        upfront_payment_percent: parseInt(formData.upfront_payment_percent),
        remaining_months: parseInt(formData.remaining_months),
      });

      setSuccess(true);
      setTimeout(() => {
        navigate('/registrations');
      }, 1500);
    } catch (err) {
      const errorDetail = err.response?.data;
      if (typeof errorDetail === 'object') {
        const messages = Object.entries(errorDetail)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
          .join('; ');
        setError(messages || 'Failed to create registration');
      } else {
        setError(errorDetail || 'Failed to create registration');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loadingOptions) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={32} className="animate-spin text-primary" />
      </div>
    );
  }

  if (success) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-success/10 border border-success/20 rounded-xl p-8 text-center">
          <CheckCircle size={48} className="mx-auto mb-4 text-success" />
          <h2 className="text-xl font-bold text-gray-100 mb-2">Registration Created!</h2>
          <p className="text-gray-400">Redirecting to registration list...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
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
            <h2 className="text-2xl font-bold tracking-tight text-gray-100">New Registration</h2>
            <p className="text-gray-400 text-sm mt-1">Create a new student registration</p>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-error/10 border border-error/20 rounded-xl p-4 mb-6 text-error">
          <div className="flex items-center gap-3">
            <AlertTriangle size={20} />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Section 1: Student Info */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary/20 rounded-lg text-primary">
              <User size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Student Information</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Full Name *
              </label>
              <div className="relative">
                <User size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                  placeholder="Enter student name"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email *
              </label>
              <div className="relative">
                <Mail size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                  placeholder="student@email.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Phone *
              </label>
              <div className="relative">
                <Phone size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                  placeholder="+44 123 456 7890"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Date of Birth *
              </label>
              <div className="relative">
                <Calendar size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="date"
                  name="dob"
                  value={formData.dob}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Course Selection */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-accent/20 rounded-lg text-accent">
              <BookOpen size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Course Selection</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Provider *
              </label>
              <select
                name="provider"
                value={formData.provider}
                onChange={handleInputChange}
                required
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-gray-100 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              >
                <option value="">Select Provider</option>
                {providers.map(provider => (
                  <option key={provider.id} value={provider.id}>
                    {provider.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Field *
              </label>
              <select
                name="field"
                value={formData.field}
                onChange={handleInputChange}
                required
                disabled={!formData.provider}
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-gray-100 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">Select Field</option>
                {filteredFields.map(field => (
                  <option key={field.id} value={field.id}>
                    {field.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Level *
              </label>
              <select
                name="level"
                value={formData.level}
                onChange={handleInputChange}
                required
                disabled={!formData.field}
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-gray-100 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">Select Level</option>
                {levels.map(level => (
                  <option key={level.id} value={level.id}>
                    Level {level.number}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Qualification Type
              </label>
              <select
                name="qualification_type"
                value={formData.qualification_type}
                onChange={handleInputChange}
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-gray-100 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              >
                <option value="">Select Type (Optional)</option>
                {qualificationTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Section 3: Financials */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-success/20 rounded-lg text-success">
              <DollarSign size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Financial Details</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Total Fee (£)
              </label>
              <div className="relative">
                <DollarSign size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="number"
                  name="total_fee"
                  value={formData.total_fee}
                  onChange={handleInputChange}
                  min="0"
                  step="0.01"
                  className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Upfront Payment (%)
              </label>
              <input
                type="number"
                name="upfront_payment_percent"
                value={formData.upfront_payment_percent}
                onChange={handleInputChange}
                min="0"
                max="100"
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-gray-100 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Remaining Months
              </label>
              <input
                type="number"
                name="remaining_months"
                value={formData.remaining_months}
                onChange={handleInputChange}
                min="1"
                max="24"
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-gray-100 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/registrations')}
            className="px-6 py-2.5 border border-border rounded-lg text-gray-300 hover:bg-surface-hover transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary-hover rounded-lg text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Save size={18} />
                Create Registration
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default NewRegistration;
