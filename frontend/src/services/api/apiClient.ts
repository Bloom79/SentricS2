/**
 * API Client Configuration
 * Consolidated API client for Kronos EAM
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { logger } from '@/utils/logger';

// Get API URL from environment
// In production, VITE_API_URL MUST be set - no fallback to localhost
const getApiBaseUrl = (): string => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const mode = import.meta.env.MODE;

  // In production/staging, API URL is required
  if ((mode === 'production' || mode === 'staging') && !apiUrl) {
    throw new Error(
      'VITE_API_URL environment variable is not set! ' +
      'API URL must be configured for production deployment.'
    );
  }

  // In development, use localhost as fallback
  return apiUrl || 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Reduced from 30s to 15s for faster failure detection
  headers: {
    'Content-Type': 'application/json',
  },
  maxRedirects: 5, // Follow redirects (e.g., /plants -> /plants/)
  validateStatus: (status) => status < 500, // Don't throw on 3xx/4xx, let us handle them
});

// Request interceptor to add auth token and deduplicate requests
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      logger.debug(`Adding auth token to request: ${config.url}`);
    } else {
      logger.debug(`No auth token found for request: ${config.url}`);
    }

    // Add tenant ID from user data
    const userData = localStorage.getItem('user_data');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        if (user?.tenant_id) {
          config.headers['X-Tenant-ID'] = user.tenant_id;
        }
      } catch (e) {
        // Ignore parse errors
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Clear all auth data
      logger.warn('Authentication failed (401), clearing tokens and redirecting to login');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_data');
      
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
      
      return Promise.reject(error);
    }

    // Handle network errors (timeout, no connection, etc.)
    if (error.code === 'ECONNABORTED' || error.message === 'Network Error' || !error.response) {
      logger.error(`Network error: ${error.message || 'Connection timeout or network unavailable'}`);
      // Don't block the UI - let React Query handle the error state
      return Promise.reject(error);
    }

    // Handle other errors with logger
    if (error.response) {
      logger.apiError(
        originalRequest.url || 'unknown',
        originalRequest.method || 'unknown',
        error.response.status,
        error.response.data
      );
    }

    return Promise.reject(error);
  }
);

export default apiClient;
