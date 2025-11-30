import React from 'react';
import { useLocation } from 'react-router-dom';
import { User, LogOut } from 'lucide-react';
import Sidebar from './Sidebar';
import { useAuth } from '../context/AuthContext';

// Map routes to page titles
const pageTitles = {
  '/': 'Dashboard',
  '/ceo': 'CEO Dashboard',
  '/sales': 'Sales Dashboard',
  '/ops': 'Operations Dashboard',
  '/proqual': 'ProQual Administration',
  '/registrations': 'Student Registrations',
  '/registrations/new': 'New Registration',
};

function Layout({ children }) {
  const location = useLocation();
  const pageTitle = pageTitles[location.pathname] || 'Dashboard';
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 bg-surface/50 backdrop-blur-sm border-b border-border flex items-center justify-between px-6 lg:px-8">
          {/* Page title - with left padding on mobile for menu button */}
          <div className="pl-12 lg:pl-0">
            <h1 className="text-lg font-semibold text-gray-100 truncate">{pageTitle}</h1>
          </div>

          {/* User actions */}
          <div className="flex items-center gap-3">
            {/* User profile button */}
            <button 
              aria-label="User profile"
              className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-surface-hover transition-colors group"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center border border-border">
                <User size={16} className="text-gray-300" />
              </div>
              <span className="hidden sm:block text-sm text-gray-300 group-hover:text-gray-100 transition-colors">
                {user?.username || 'Profile'}
              </span>
            </button>

            {/* Logout button */}
            <button 
              aria-label="Logout"
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-error/10 text-gray-400 hover:text-error transition-colors group"
            >
              <LogOut size={18} />
              <span className="hidden sm:block text-sm">
                Logout
              </span>
            </button>
          </div>
        </header>

        {/* Main content with gradient background */}
        <main className="flex-1 overflow-y-auto relative">
          {/* Subtle gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5 pointer-events-none" />
          
          {/* Decorative glow elements */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 blur-3xl rounded-full pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent/5 blur-3xl rounded-full pointer-events-none" />

          {/* Content */}
          <div className="relative z-10 p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

export default Layout;
