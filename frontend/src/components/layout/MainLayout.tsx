/**
 * Main Layout Component
 * Consolidated from Kronos EAM - Mobile Optimized
 */

import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard,
  Factory,
  Users,
  Workflow,
  FileCheck,
  LogOut,
  FileText,
  Calendar,
  Link2,
  FileBarChart,
  Settings,
  User,
  Bell,
  CheckSquare,
  Zap,
  BookOpen,
  Building2,
  Sparkles,
  Menu,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// Main dashboard
const mainNavigation = [{ name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard }];

// CER Management Module
const cerManagementNavigation = [{ name: 'CER Communities', href: '/cer', icon: Sparkles }];

// Plant Management Module
const plantManagementNavigation = [
  { name: 'Sites', href: '/sites', icon: Building2 },
  { name: 'Plants', href: '/plants', icon: Factory },
];

// Compliance Management Module
const complianceManagementNavigation = [
  { name: 'Compliance Dashboard', href: '/compliance', icon: FileCheck },
  { name: 'Active Workflows', href: '/workflows', icon: Workflow },
  { name: 'Workflow Templates', href: '/workflow-templates', icon: FileText },
  { name: 'Document Library', href: '/documents', icon: BookOpen },
];

// General Tools
const generalToolsNavigation = [
  { name: 'Agenda', href: '/agenda', icon: Calendar },
  { name: 'Integrations', href: '/integrations', icon: Link2 },
  { name: 'Team', href: '/team', icon: Users },
  { name: 'AI Assistant', href: '/ai-assistant', icon: Zap },
];

const adminNavigation = [
  { name: 'Administration', href: '/administration', icon: Settings },
  { name: 'User Management', href: '/admin/users', icon: Users },
];

export default function MainLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Close sidebar when route changes on mobile
  React.useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-sm">
            <Factory className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Kronos EAM
          </span>
        </div>
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label="Toggle menu"
        >
          {sidebarOpen ? (
            <X className="h-6 w-6 text-gray-600" />
          ) : (
            <Menu className="h-6 w-6 text-gray-600" />
          )}
        </button>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40 transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-white to-gray-50/50 border-r border-gray-200/60 shadow-lg lg:shadow-sm transition-transform duration-300 ease-in-out',
          'lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-2 p-6 border-b border-gray-200/60 bg-gradient-to-r from-primary/5 to-transparent">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-sm">
              <Factory className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Kronos EAM
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            {/* Main Dashboard */}
            {mainNavigation.map((item) => {
              const isActive = location.pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group',
                    isActive
                      ? 'bg-gradient-to-r from-primary to-primary/90 text-white shadow-md shadow-primary/20'
                      : 'text-gray-700 hover:bg-gradient-to-r hover:from-primary/5 hover:to-primary/10 hover:text-primary hover:shadow-sm'
                  )}
                >
                  <item.icon
                    className={cn(
                      'h-5 w-5 transition-transform',
                      isActive ? 'text-white' : 'text-gray-500 group-hover:text-primary'
                    )}
                  />
                  <span className={cn('font-medium', isActive && 'font-semibold')}>
                    {item.name}
                  </span>
                </Link>
              );
            })}

            {/* CER Management Module */}
            <div className="pt-4 mt-4 border-t border-gray-200/60">
              <p className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                CER Management
              </p>
            </div>
            {cerManagementNavigation.map((item) => {
              const isActive = location.pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group relative',
                    isActive
                      ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-md shadow-purple-500/20'
                      : 'text-gray-700 hover:bg-gradient-to-r hover:from-purple-50 hover:to-purple-100/50 hover:text-purple-700 hover:shadow-sm'
                  )}
                >
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                  )}
                  <item.icon
                    className={cn(
                      'h-5 w-5 transition-transform',
                      isActive ? 'text-white' : 'text-gray-500 group-hover:text-purple-600'
                    )}
                  />
                  <span className={cn('font-medium', isActive && 'font-semibold')}>
                    {item.name}
                  </span>
                </Link>
              );
            })}

            {/* Plant Management Module */}
            <div className="pt-4 mt-4 border-t border-gray-200/60">
              <p className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Plant Management
              </p>
            </div>
            {plantManagementNavigation.map((item) => {
              const isActive = location.pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group relative',
                    isActive
                      ? 'bg-gradient-to-r from-teal-500 to-teal-600 text-white shadow-md shadow-teal-500/20'
                      : 'text-gray-700 hover:bg-gradient-to-r hover:from-teal-50 hover:to-teal-100/50 hover:text-teal-700 hover:shadow-sm'
                  )}
                >
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                  )}
                  <item.icon
                    className={cn(
                      'h-5 w-5 transition-transform',
                      isActive ? 'text-white' : 'text-gray-500 group-hover:text-teal-600'
                    )}
                  />
                  <span className={cn('font-medium', isActive && 'font-semibold')}>
                    {item.name}
                  </span>
                </Link>
              );
            })}

            {/* Compliance Management Module */}
            <div className="pt-4 mt-4 border-t border-gray-200/60">
              <p className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Compliance Management
              </p>
            </div>
            {complianceManagementNavigation.map((item) => {
              const isActive = location.pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group relative',
                    isActive
                      ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md shadow-blue-500/20'
                      : 'text-gray-700 hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100/50 hover:text-blue-700 hover:shadow-sm'
                  )}
                >
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                  )}
                  <item.icon
                    className={cn(
                      'h-5 w-5 transition-transform',
                      isActive ? 'text-white' : 'text-gray-500 group-hover:text-blue-600'
                    )}
                  />
                  <span className={cn('font-medium', isActive && 'font-semibold')}>
                    {item.name}
                  </span>
                </Link>
              );
            })}

            {/* General Tools */}
            <div className="pt-4 mt-4 border-t border-gray-200/60">
              <p className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                General Tools
              </p>
            </div>
            {generalToolsNavigation.map((item) => {
              const isActive = location.pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group relative',
                    isActive
                      ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-md shadow-orange-500/20'
                      : 'text-gray-700 hover:bg-gradient-to-r hover:from-orange-50 hover:to-orange-100/50 hover:text-orange-700 hover:shadow-sm'
                  )}
                >
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                  )}
                  <item.icon
                    className={cn(
                      'h-5 w-5 transition-transform',
                      isActive ? 'text-white' : 'text-gray-500 group-hover:text-orange-600'
                    )}
                  />
                  <span className={cn('font-medium', isActive && 'font-semibold')}>
                    {item.name}
                  </span>
                </Link>
              );
            })}

            {/* Admin Navigation */}
            {user?.role === 'Admin' && (
              <>
                <div className="pt-4 mt-4 border-t border-gray-200/60">
                  <p className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Administration
                  </p>
                </div>
                {adminNavigation.map((item) => {
                  const isActive = location.pathname.startsWith(item.href);
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={cn(
                        'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group relative',
                        isActive
                          ? 'bg-gradient-to-r from-gray-700 to-gray-800 text-white shadow-md shadow-gray-700/20'
                          : 'text-gray-700 hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100/50 hover:text-gray-900 hover:shadow-sm'
                      )}
                    >
                      {isActive && (
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                      )}
                      <item.icon
                        className={cn(
                          'h-5 w-5 transition-transform',
                          isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-900'
                        )}
                      />
                      <span className={cn('font-medium', isActive && 'font-semibold')}>
                        {item.name}
                      </span>
                    </Link>
                  );
                })}
              </>
            )}

            {/* User Quick Links */}
            <div className="pt-4 mt-4 border-t border-gray-200/60">
              <Link
                to="/my-tasks"
                className={cn(
                  'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group relative mb-1',
                  location.pathname === '/my-tasks'
                    ? 'bg-gradient-to-r from-primary to-primary/90 text-white shadow-md shadow-primary/20'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-primary/5 hover:to-primary/10 hover:text-primary hover:shadow-sm'
                )}
              >
                {location.pathname === '/my-tasks' && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                )}
                <CheckSquare
                  className={cn(
                    'h-5 w-5 transition-transform',
                    location.pathname === '/my-tasks'
                      ? 'text-white'
                      : 'text-gray-500 group-hover:text-primary'
                  )}
                />
                <span
                  className={cn(
                    'font-medium',
                    location.pathname === '/my-tasks' && 'font-semibold'
                  )}
                >
                  My Tasks
                </span>
              </Link>
              <Link
                to="/notifications"
                className={cn(
                  'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group relative mb-1',
                  location.pathname === '/notifications'
                    ? 'bg-gradient-to-r from-primary to-primary/90 text-white shadow-md shadow-primary/20'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-primary/5 hover:to-primary/10 hover:text-primary hover:shadow-sm'
                )}
              >
                {location.pathname === '/notifications' && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                )}
                <Bell
                  className={cn(
                    'h-5 w-5 transition-transform',
                    location.pathname === '/notifications'
                      ? 'text-white'
                      : 'text-gray-500 group-hover:text-primary'
                  )}
                />
                <span
                  className={cn(
                    'font-medium',
                    location.pathname === '/notifications' && 'font-semibold'
                  )}
                >
                  Notifications
                </span>
              </Link>
              <Link
                to="/profile"
                className={cn(
                  'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group relative',
                  location.pathname === '/profile'
                    ? 'bg-gradient-to-r from-primary to-primary/90 text-white shadow-md shadow-primary/20'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-primary/5 hover:to-primary/10 hover:text-primary hover:shadow-sm'
                )}
              >
                {location.pathname === '/profile' && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                )}
                <User
                  className={cn(
                    'h-5 w-5 transition-transform',
                    location.pathname === '/profile'
                      ? 'text-white'
                      : 'text-gray-500 group-hover:text-primary'
                  )}
                />
                <span
                  className={cn('font-medium', location.pathname === '/profile' && 'font-semibold')}
                >
                  Profile
                </span>
              </Link>
            </div>
          </nav>

          {/* User Section */}
          <div className="p-4 border-t border-gray-200/60 bg-gradient-to-t from-gray-50/50 to-transparent">
            <div className="flex items-center gap-3 mb-4 p-3 rounded-lg bg-white/80 backdrop-blur-sm border border-gray-200/60 shadow-sm">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-md">
                <span className="text-sm font-semibold text-white">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
            <Button
              variant="outline"
              className="w-full border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all"
              onClick={logout}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64 pt-16 lg:pt-0">
        <main className="p-3 sm:p-4 lg:p-6 bg-gradient-to-br from-gray-50/50 via-gray-50/30 to-gray-100/40 min-h-screen">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
