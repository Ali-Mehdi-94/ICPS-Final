import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Crown, 
  TrendingUp, 
  Settings, 
  Award,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Cog
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from '../context/AuthContext';

const navigationItems = [
  { 
    name: 'CEO Dashboard', 
    path: '/ceo', 
    icon: Crown,
    description: 'Executive overview'
  },
  { 
    name: 'Sales Dashboard', 
    path: '/sales', 
    icon: TrendingUp,
    description: 'Sales performance'
  },
  { 
    name: 'Ops Dashboard', 
    path: '/ops', 
    icon: Settings,
    description: 'Operations management'
  },
  { 
    name: 'ProQual Admin', 
    path: '/proqual', 
    icon: Award,
    description: 'Quality administration'
  },
  { 
    name: 'Registrations', 
    path: '/registrations', 
    icon: BookOpen,
    description: 'Student registrations'
  },
];

// Course Settings visible only to Sales, CEO, ProQualAdmin
const courseSettingsItem = { 
  name: 'Course Settings', 
  path: '/settings/courses', 
  icon: Cog,
  description: 'Manage courses',
  roles: ['Sales', 'CEO', 'ProQualAdmin']
};

function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { user } = useAuth();

  const toggleSidebar = () => setIsCollapsed(!isCollapsed);
  const toggleMobile = () => setIsMobileOpen(!isMobileOpen);

  // Build navigation items based on user role
  const userRole = user?.role || '';
  const navItems = [...navigationItems];
  
  // Add Course Settings if user has appropriate role
  if (courseSettingsItem.roles.includes(userRole)) {
    navItems.push(courseSettingsItem);
  }

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={toggleMobile}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-surface border border-border rounded-lg text-gray-100 hover:bg-surface-hover transition-colors"
        aria-label="Toggle mobile menu"
      >
        {isMobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-30"
          onClick={toggleMobile}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed lg:relative z-40 h-screen bg-surface border-r border-border flex flex-col transition-all duration-300 ease-in-out',
          isCollapsed ? 'w-20' : 'w-64',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo area */}
        <div className={clsx(
          'flex items-center h-16 px-4 border-b border-border',
          isCollapsed ? 'justify-center' : 'justify-between'
        )}>
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">IC</span>
              </div>
              <span className="font-semibold text-gray-100 tracking-tight">ICPS Portal</span>
            </div>
          )}
          
          {/* Collapse toggle - hidden on mobile */}
          <button
            onClick={toggleSidebar}
            className="hidden lg:flex p-1.5 hover:bg-surface-hover rounded-lg transition-colors text-gray-400 hover:text-gray-100"
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setIsMobileOpen(false)}
              className={({ isActive }) => clsx(
                'group flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 relative',
                isActive 
                  ? 'bg-primary/10 text-primary' 
                  : 'text-gray-400 hover:text-gray-100 hover:bg-surface-hover'
              )}
            >
              {({ isActive }) => (
                <>
                  {/* Glow effect for active item */}
                  {isActive && (
                    <div className="absolute inset-0 bg-primary/5 rounded-lg blur-xl pointer-events-none" />
                  )}
                  
                  {/* Active indicator bar */}
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary rounded-r-full shadow-[0_0_8px_2px_rgba(59,130,246,0.5)]" />
                  )}
                  
                  <item.icon 
                    size={20} 
                    className={clsx(
                      'flex-shrink-0 transition-all duration-200',
                      isActive && 'drop-shadow-[0_0_6px_rgba(59,130,246,0.6)]'
                    )} 
                  />
                  
                  {!isCollapsed && (
                    <div className="relative z-10 min-w-0">
                      <span className="block font-medium text-sm truncate">{item.name}</span>
                      <span className={clsx(
                        'block text-xs truncate transition-colors',
                        isActive ? 'text-primary/70' : 'text-gray-500'
                      )}>
                        {item.description}
                      </span>
                    </div>
                  )}
                  
                  {/* Tooltip for collapsed state */}
                  {isCollapsed && (
                    <div 
                      role="tooltip" 
                      className="absolute left-full ml-2 px-2 py-1 bg-surface border border-border rounded-md opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50"
                    >
                      <span className="text-sm text-gray-100">{item.name}</span>
                    </div>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className={clsx(
          'p-4 border-t border-border',
          isCollapsed && 'flex justify-center'
        )}>
          {!isCollapsed ? (
            <div className="text-xs text-gray-500">
              <p>ICPS v1.0.0</p>
              <p className="mt-0.5">© 2024 ICPS</p>
            </div>
          ) : (
            <div className="w-2 h-2 bg-success rounded-full" title="System Online" />
          )}
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
