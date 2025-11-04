# Frontend Dockerfile for Kronos EAM Consolidated
# Multi-stage build for optimized production image

# Stage 1: Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build argument for API URL (Vite uses VITE_ prefix)
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Build the application
RUN npm run build

# Stage 2: Production stage
FROM nginx:alpine

# Install curl for health checks and gettext for envsubst
RUN apk add --no-cache curl gettext

# Copy custom nginx config template
COPY nginx.conf /etc/nginx/nginx.conf.template

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Ensure directories exist with correct permissions
RUN mkdir -p /var/cache/nginx /var/log/nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /var/run/nginx.pid /usr/share/nginx/html

# Create health check endpoint
RUN echo 'OK' > /usr/share/nginx/html/health

# Create startup script
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'export PORT=${PORT:-80}' >> /docker-entrypoint.sh && \
    echo 'envsubst "\$PORT" < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh && \
    chown nginx:nginx /docker-entrypoint.sh

# Switch to non-root user
USER nginx

# Expose port (dynamic at runtime)
EXPOSE 80 8080

# Health check (use PORT env var)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-80}/health || exit 1

# Start with entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]

