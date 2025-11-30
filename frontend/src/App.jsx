import React from 'react';
import { LayoutDashboard, Sparkles } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-white p-4">
      <div className="max-w-md w-full bg-surface border border-border rounded-xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-3xl rounded-full pointer-events-none"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-primary/20 rounded-lg text-primary">
              <LayoutDashboard size={24} />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">ICPS Portal</h1>
          </div>
          <p className="text-gray-400 mb-8 leading-relaxed">
            Welcome to the Integrated Course Management System. 
            The frontend is initialized and ready for development.
          </p>
          <button className="w-full py-3 px-4 bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-opacity rounded-lg font-medium flex items-center justify-center gap-2">
            <Sparkles size={18} />
            <span>Initialize System</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
