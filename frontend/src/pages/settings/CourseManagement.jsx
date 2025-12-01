import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  BookOpen, 
  Layers,
  Plus,
  Loader2,
  AlertTriangle,
  CheckCircle,
  X
} from 'lucide-react';
import api from '../../services/api';

// Constants
const SUCCESS_TIMEOUT_MS = 3000;

function CourseManagement() {
  // Data states
  const [providers, setProviders] = useState([]);
  const [fields, setFields] = useState([]);
  const [levels, setLevels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Form states
  const [newProvider, setNewProvider] = useState('');
  const [newField, setNewField] = useState({ name: '', provider: '' });
  const [newLevel, setNewLevel] = useState('');
  
  // Submission states
  const [submitting, setSubmitting] = useState({ provider: false, field: false, level: false });
  const [success, setSuccess] = useState({ provider: false, field: false, level: false });

  // Fetch all data on mount
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [providersRes, fieldsRes, levelsRes] = await Promise.all([
        api.get('/api/providers/'),
        api.get('/api/fields/'),
        api.get('/api/levels/'),
      ]);
      setProviders(providersRes.data);
      setFields(fieldsRes.data);
      setLevels(levelsRes.data);
    } catch (err) {
      setError('Failed to load course management data');
    } finally {
      setLoading(false);
    }
  };

  // Add new provider
  const handleAddProvider = async (e) => {
    e.preventDefault();
    if (!newProvider.trim()) return;
    
    setSubmitting(prev => ({ ...prev, provider: true }));
    setSuccess(prev => ({ ...prev, provider: false }));
    
    try {
      const response = await api.post('/api/providers/', { name: newProvider.trim() });
      setProviders(prev => [...prev, response.data]);
      setNewProvider('');
      setSuccess(prev => ({ ...prev, provider: true }));
      setTimeout(() => setSuccess(prev => ({ ...prev, provider: false })), SUCCESS_TIMEOUT_MS);
    } catch (err) {
      setError('Failed to add provider');
    } finally {
      setSubmitting(prev => ({ ...prev, provider: false }));
    }
  };

  // Add new field
  const handleAddField = async (e) => {
    e.preventDefault();
    if (!newField.name.trim() || !newField.provider) return;
    
    setSubmitting(prev => ({ ...prev, field: true }));
    setSuccess(prev => ({ ...prev, field: false }));
    
    try {
      const response = await api.post('/api/fields/', {
        name: newField.name.trim(),
        provider: parseInt(newField.provider),
      });
      setFields(prev => [...prev, response.data]);
      setNewField({ name: '', provider: '' });
      setSuccess(prev => ({ ...prev, field: true }));
      setTimeout(() => setSuccess(prev => ({ ...prev, field: false })), SUCCESS_TIMEOUT_MS);
    } catch (err) {
      setError('Failed to add field');
    } finally {
      setSubmitting(prev => ({ ...prev, field: false }));
    }
  };

  // Add new level
  const handleAddLevel = async (e) => {
    e.preventDefault();
    if (!newLevel) return;
    
    setSubmitting(prev => ({ ...prev, level: true }));
    setSuccess(prev => ({ ...prev, level: false }));
    
    try {
      const response = await api.post('/api/levels/', { number: parseInt(newLevel) });
      setLevels(prev => [...prev, response.data].sort((a, b) => a.number - b.number));
      setNewLevel('');
      setSuccess(prev => ({ ...prev, level: true }));
      setTimeout(() => setSuccess(prev => ({ ...prev, level: false })), SUCCESS_TIMEOUT_MS);
    } catch (err) {
      setError('Failed to add level');
    } finally {
      setSubmitting(prev => ({ ...prev, level: false }));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={32} className="animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-6 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none" />
        <div className="relative z-10 flex items-center gap-4">
          <div className="p-4 bg-primary/20 rounded-xl text-primary">
            <BookOpen size={32} />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-gray-100">Course Settings</h2>
            <p className="text-gray-400 text-sm mt-1">Manage course providers, fields, and levels</p>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-error/10 border border-error/20 rounded-xl p-4 mb-6 text-error">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertTriangle size={20} />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="hover:text-error/70">
              <X size={18} />
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Providers Section */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary/20 rounded-lg text-primary">
              <Building2 size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Providers</h3>
          </div>

          {/* Provider List */}
          <div className="space-y-2 mb-6 max-h-48 overflow-y-auto">
            {providers.length === 0 ? (
              <p className="text-gray-500 text-sm">No providers yet</p>
            ) : (
              providers.map(provider => (
                <div key={provider.id} className="px-3 py-2 bg-background rounded-lg text-gray-300 text-sm">
                  {provider.name}
                </div>
              ))
            )}
          </div>

          {/* Add Provider Form */}
          <form onSubmit={handleAddProvider} className="space-y-3">
            <input
              type="text"
              value={newProvider}
              onChange={(e) => setNewProvider(e.target.value)}
              placeholder="New provider name"
              className="w-full bg-background border border-border rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            />
            <button
              type="submit"
              disabled={submitting.provider || !newProvider.trim()}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover rounded-lg text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting.provider ? (
                <Loader2 size={16} className="animate-spin" />
              ) : success.provider ? (
                <CheckCircle size={16} />
              ) : (
                <Plus size={16} />
              )}
              {success.provider ? 'Added!' : 'Add Provider'}
            </button>
          </form>
        </div>

        {/* Fields Section */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-accent/20 rounded-lg text-accent">
              <BookOpen size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Fields</h3>
          </div>

          {/* Field List */}
          <div className="space-y-2 mb-6 max-h-48 overflow-y-auto">
            {fields.length === 0 ? (
              <p className="text-gray-500 text-sm">No fields yet</p>
            ) : (
              fields.map(field => {
                const providerName = providers.find(p => p.id === field.provider)?.name || 'Unknown';
                return (
                  <div key={field.id} className="px-3 py-2 bg-background rounded-lg text-sm">
                    <span className="text-gray-300">{field.name}</span>
                    <span className="text-gray-500 text-xs ml-2">({providerName})</span>
                  </div>
                );
              })
            )}
          </div>

          {/* Add Field Form */}
          <form onSubmit={handleAddField} className="space-y-3">
            <input
              type="text"
              value={newField.name}
              onChange={(e) => setNewField(prev => ({ ...prev, name: e.target.value }))}
              placeholder="New field name"
              className="w-full bg-background border border-border rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            />
            <select
              value={newField.provider}
              onChange={(e) => setNewField(prev => ({ ...prev, provider: e.target.value }))}
              className="w-full bg-background border border-border rounded-lg px-4 py-2 text-gray-100 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            >
              <option value="">Select Provider</option>
              {providers.map(provider => (
                <option key={provider.id} value={provider.id}>
                  {provider.name}
                </option>
              ))}
            </select>
            <button
              type="submit"
              disabled={submitting.field || !newField.name.trim() || !newField.provider}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting.field ? (
                <Loader2 size={16} className="animate-spin" />
              ) : success.field ? (
                <CheckCircle size={16} />
              ) : (
                <Plus size={16} />
              )}
              {success.field ? 'Added!' : 'Add Field'}
            </button>
          </form>
        </div>

        {/* Levels Section */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-success/20 rounded-lg text-success">
              <Layers size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-100">Levels</h3>
          </div>

          {/* Level List */}
          <div className="space-y-2 mb-6 max-h-48 overflow-y-auto">
            {levels.length === 0 ? (
              <p className="text-gray-500 text-sm">No levels yet</p>
            ) : (
              levels.map(level => (
                <div key={level.id} className="px-3 py-2 bg-background rounded-lg text-gray-300 text-sm">
                  Level {level.number}
                </div>
              ))
            )}
          </div>

          {/* Add Level Form */}
          <form onSubmit={handleAddLevel} className="space-y-3">
            <input
              type="number"
              value={newLevel}
              onChange={(e) => setNewLevel(e.target.value)}
              placeholder="Level number (e.g., 3, 4, 5)"
              min="1"
              max="10"
              className="w-full bg-background border border-border rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            />
            <button
              type="submit"
              disabled={submitting.level || !newLevel}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-success hover:bg-success/80 rounded-lg text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting.level ? (
                <Loader2 size={16} className="animate-spin" />
              ) : success.level ? (
                <CheckCircle size={16} />
              ) : (
                <Plus size={16} />
              )}
              {success.level ? 'Added!' : 'Add Level'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default CourseManagement;
