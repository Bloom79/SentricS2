/**
 * Authentication Context
 * Consolidated from Kronos EAM
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiClient from '@/services/api/apiClient';
import { logger } from '@/utils/logger';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  tenant_id: string;
  permissions: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session by validating token with backend
    const validateSession = async () => {
      const token = localStorage.getItem('access_token');
      const userData = localStorage.getItem('user_data');

      if (token && userData) {
        try {
          // Validate token with backend
          const response = await apiClient.get('/auth/me');
          const validatedUser = response.data;
          localStorage.setItem('user_data', JSON.stringify(validatedUser));
          setUser(validatedUser);
        } catch (error) {
          logger.error('Session validation failed', error);
          // Clear localStorage synchronously
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_data');
          localStorage.removeItem('refresh_token');
          setUser(null);
        }
      }
      setLoading(false);
    };

    validateSession();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // Use URLSearchParams for OAuth2 form data
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const response = await apiClient.post('/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token, user: userData } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_data', JSON.stringify(userData));

      setUser(userData);
    } catch (error: any) {
      logger.error('Login failed', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const response = await apiClient.get('/auth/me');
      const userData = response.data;
      localStorage.setItem('user_data', JSON.stringify(userData));
      setUser(userData);
    } catch (error) {
      logger.error('Failed to refresh user', error);
      logout();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

