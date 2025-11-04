# Backend Dockerfile for Kronos EAM Consolidated
# Multi-stage build for optimized production image

# Stage 1: Build stage
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --root-user-action=ignore --no-cache-dir --upgrade pip && \
    pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 kronos

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=kronos:kronos . .

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for database to be ready (only for TCP connections, not Unix sockets)\n\
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" != *"/cloudsql/"* ]] && [[ "$DATABASE_URL" == *"@"* ]]; then\n\
  echo "Waiting for database..."\n\
  DB_HOST=$(echo $DATABASE_URL | sed -n "s/.*@\\([^:]*\\):.*/\\1/p")\n\
  DB_PORT=$(echo $DATABASE_URL | sed -n "s/.*:\\([0-9]*\\)\\/.*/\\1/p")\n\
  if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then\n\
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" 2>/dev/null; do\n\
      echo "Database not ready, waiting..."\n\
      sleep 2\n\
    done\n\
    echo "Database is ready"\n\
  fi\n\
fi\n\
\n\
# Run migrations\n\
if [ -n "$DATABASE_URL" ]; then\n\
  echo "Running database migrations..."\n\
  alembic upgrade head || echo "Migration failed or already applied, continuing..."\n\
fi\n\
\n\
# Start the application\n\
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-2} --proxy-headers --forwarded-allow-ips="*"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Switch to non-root user
USER kronos

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expose port (Cloud Run will use PORT environment variable)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]

