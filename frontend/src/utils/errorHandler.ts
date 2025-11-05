/**
 * Centralized error handling utilities
 * Consolidated from improvements
 */

import { AxiosError } from 'axios';
import { logger } from './logger';

export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public userMessage?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'AppError';
    Object.setPrototypeOf(this, AppError.prototype);
  }

  toUserMessage(): string {
    return this.userMessage || this.message || 'An unexpected error occurred';
  }
}

export const ErrorCodes = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  API_ERROR: 'API_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
} as const;

export function handleError(error: unknown): AppError {
  if (error instanceof AppError) {
    return error;
  }

  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosError = error as AxiosError;
    const status = axiosError.response?.status || 500;
    const endpoint = axiosError.config?.url || 'unknown';
    const method = axiosError.config?.method?.toUpperCase() || 'UNKNOWN';

    logger.apiError(endpoint, method, status, axiosError.response?.data);

    const errorCodeMap: Record<number, string> = {
      400: ErrorCodes.VALIDATION_ERROR,
      401: ErrorCodes.UNAUTHORIZED,
      403: ErrorCodes.FORBIDDEN,
      404: ErrorCodes.NOT_FOUND,
      500: ErrorCodes.SERVER_ERROR,
    };

    const code = errorCodeMap[status] || ErrorCodes.API_ERROR;
    const responseData = axiosError.response?.data as any;
    const userMessage =
      responseData?.detail || responseData?.message || getDefaultUserMessage(status);

    return new AppError(
      axiosError.message || `API request failed: ${method} ${endpoint}`,
      code,
      status,
      userMessage,
      { endpoint, method, status, responseData }
    );
  }

  if (error instanceof Error) {
    return new AppError(
      error.message,
      ErrorCodes.UNKNOWN_ERROR,
      500,
      'An unexpected error occurred. Please try again.'
    );
  }

  return new AppError(
    'An unknown error occurred',
    ErrorCodes.UNKNOWN_ERROR,
    500,
    'An unexpected error occurred. Please try again.'
  );
}

function getDefaultUserMessage(status: number): string {
  const messages: Record<number, string> = {
    400: 'Invalid request. Please check your input and try again.',
    401: 'You are not authorized. Please log in again.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    500: 'A server error occurred. Please try again later.',
  };
  return messages[status] || 'An error occurred. Please try again.';
}
