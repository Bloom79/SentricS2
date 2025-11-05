/**
 * Main App Component
 * Consolidated Kronos EAM Frontend
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';

// Pages
import Login from '@/pages/Auth/Login';
import Dashboard from '@/pages/Dashboard/Dashboard';
import Sites from '@/pages/Sites/Sites';
import SiteDetail from '@/pages/Sites/SiteDetail';
import Plants from '@/pages/Plants/Plants';
import PlantDetail from '@/pages/Plants/PlantDetail';
import CERManagement from '@/pages/CER/CERManagement';
import CERDetail from '@/pages/CER/CERDetail';
import CERCreate from '@/pages/CER/CERCreate';
import MemberDetail from '@/pages/CER/MemberDetail';
import Workflows from '@/pages/Workflows/Workflows';
import WorkflowDetail from '@/pages/Workflows/WorkflowDetail';
import WorkflowPhaseDetail from '@/pages/Workflows/WorkflowPhaseDetail';
import WorkflowTemplates from '@/pages/Workflows/WorkflowTemplates';
import Compliance from '@/pages/Compliance/Compliance';
import ComplianceManagement from '@/pages/ComplianceManagement/ComplianceManagement';
import Documents from '@/pages/Documents/Documents';
import UserManagement from '@/pages/Admin/UserManagement';
import Reports from '@/pages/Reports/Reports';
import Administration from '@/pages/Admin/Administration';
import Profile from '@/pages/Profile/Profile';
import Notifications from '@/pages/Notifications/Notifications';
import MyTasks from '@/pages/MyTasks/MyTasks';
import Team from '@/pages/Team/Team';
import Integrations from '@/pages/Integrations/Integrations';
import Agenda from '@/pages/Agenda/Agenda';
import AIAssistant from '@/pages/AIAssistant/AIAssistant';

// Layout
import MainLayout from '@/components/layout/MainLayout';

// Auth context
import { AuthProvider, useAuth } from '@/contexts/AuthContext';

// Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false, // Don't retry - let API client handle redirects on 401
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      refetchOnMount: true,
      refetchOnReconnect: false,
      // Add timeout for queries
      meta: {
        errorMessage: 'Failed to load data. Please try again.',
      },
    },
  },
});

// Protected route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public route component
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />

        {/* Sites */}
        <Route path="sites" element={<Sites />} />
        <Route path="sites/:id" element={<SiteDetail />} />

        {/* Plants */}
        <Route path="plants" element={<Plants />} />
        <Route path="plants/:id" element={<PlantDetail />} />

        {/* CER */}
        <Route path="cer" element={<CERManagement />} />
        <Route path="cer/new" element={<CERCreate />} />
        <Route path="cer/:id" element={<CERDetail />} />
        <Route path="cer/:id/members/:memberId" element={<MemberDetail />} />

        {/* Workflows */}
        <Route path="workflows" element={<Workflows />} />
        <Route path="workflows/:workflowId" element={<WorkflowDetail />} />
        <Route path="workflows/:workflowId/phases/:phaseId" element={<WorkflowPhaseDetail />} />
        <Route path="workflow-templates" element={<WorkflowTemplates />} />

        {/* Compliance */}
        <Route path="compliance" element={<ComplianceManagement />} />
        <Route path="compliance-overview" element={<Compliance />} />
        <Route path="plants/:id/compliance" element={<PlantDetail />} />

        {/* Documents */}
        <Route path="documents" element={<Documents />} />

        {/* Admin */}
        <Route path="admin/users" element={<UserManagement />} />
        <Route path="administration" element={<Administration />} />

        {/* User Pages */}
        <Route path="profile" element={<Profile />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="my-tasks" element={<MyTasks />} />
        <Route path="team" element={<Team />} />

        {/* Tools */}
        <Route path="integrations" element={<Integrations />} />
        <Route path="agenda" element={<Agenda />} />
        <Route path="ai-assistant" element={<AIAssistant />} />

        {/* Reports */}
        <Route path="reports" element={<Reports />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <AppRoutes />
          <Toaster />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
