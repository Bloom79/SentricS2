/**
 * Centralized logging utility
 * Consolidated from improvements
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const isProduction = import.meta.env.PROD;

class Logger {
  private shouldLog(level: LogLevel): boolean {
    if (isProduction) {
      return level === 'error' || level === 'warn';
    }
    return true;
  }

  debug(message: string, ...args: any[]): void {
    if (!this.shouldLog('debug')) return;
    console.debug(`[DEBUG] ${new Date().toISOString()}`, message, ...args);
  }

  info(message: string, ...args: any[]): void {
    if (!this.shouldLog('info')) return;
    console.info(`[INFO] ${new Date().toISOString()}`, message, ...args);
  }

  warn(message: string, ...args: any[]): void {
    if (!this.shouldLog('warn')) return;
    console.warn(`[WARN] ${new Date().toISOString()}`, message, ...args);
  }

  error(message: string, error?: Error | any, ...args: any[]): void {
    console.error(`[ERROR] ${new Date().toISOString()}`, message, error, ...args);
  }

  apiError(endpoint: string, method: string, status: number, error: any): void {
    this.error(
      `API Error: ${method} ${endpoint} - Status ${status}`,
      error,
      { endpoint, method, status }
    );
  }
}

export const logger = new Logger();

