#!/bin/bash
#
# Test Backend Docker Image Locally
# Builds and tests the backend Docker image before deployment
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

IMAGE_NAME="kronos-eam-backend-test"
CONTAINER_NAME="kronos-backend-test"
PORT=8000

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Testing Backend Docker Image${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not running${NC}"
    exit 1
fi

# Stop and remove existing container if it exists
echo -e "${YELLOW}Cleaning up existing containers...${NC}"
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

# Build the image
echo -e "\n${YELLOW}Step 1: Building Docker image...${NC}"
cd "$(dirname "$0")"
docker build -t ${IMAGE_NAME}:latest . || {
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Image built successfully${NC}"

# Check if we have a local database to test with
USE_LOCAL_DB=false
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == *"localhost"* ]]; then
    USE_LOCAL_DB=true
    echo -e "\n${YELLOW}Step 2: Using local database for testing${NC}"
    echo "DATABASE_URL: ${DATABASE_URL}"
else
    echo -e "\n${YELLOW}Step 2: No local DATABASE_URL found${NC}"
    echo "Using test environment variables"
fi

# Run the container
echo -e "\n${YELLOW}Step 3: Starting container...${NC}"

# Prepare environment variables
ENV_ARGS=(
    -e "PORT=${PORT}"
    -e "ENVIRONMENT=testing"
    -e "LOG_LEVEL=INFO"
    -e "DEBUG=false"
)

if [ "$USE_LOCAL_DB" = true ]; then
    # For local database, use host network or expose port
    ENV_ARGS+=(-e "DATABASE_URL=${DATABASE_URL}")
    NETWORK_ARGS="--network host"
else
    # Use test database URL
    ENV_ARGS+=(-e "DATABASE_URL=postgresql://test:test@localhost/kronos_eam_test")
    NETWORK_ARGS="-p ${PORT}:${PORT}"
fi

# Add JWT secret for testing
ENV_ARGS+=(-e "JWT_SECRET_KEY=test-secret-key-for-local-testing-only-change-in-production")

docker run -d \
    --name ${CONTAINER_NAME} \
    ${NETWORK_ARGS} \
    "${ENV_ARGS[@]}" \
    ${IMAGE_NAME}:latest || {
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
}

echo -e "${GREEN}✅ Container started${NC}"

# Wait for container to be ready
echo -e "\n${YELLOW}Step 4: Waiting for service to be ready...${NC}"
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s -f http://localhost:${PORT}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Service is ready!${NC}"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo -e "${RED}❌ Service did not become ready in time${NC}"
        echo "Container logs:"
        docker logs ${CONTAINER_NAME}
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        exit 1
    fi
    
    echo -n "."
    sleep 2
done

# Test endpoints
echo -e "\n${YELLOW}Step 5: Testing endpoints...${NC}"

# Test health endpoint
echo -n "  Testing /health... "
if curl -s http://localhost:${PORT}/health | grep -q "OK\|ok\|healthy" || curl -s -f http://localhost:${PORT}/health > /dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  (may be OK if endpoint returns 200)${NC}"
fi

# Test root endpoint
echo -n "  Testing /... "
if curl -s -f http://localhost:${PORT}/ > /dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️${NC}"
fi

# Test API docs
echo -n "  Testing /docs... "
if curl -s -f http://localhost:${PORT}/docs > /dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️${NC}"
fi

# Check container logs for errors
echo -e "\n${YELLOW}Step 6: Checking container logs...${NC}"
LOG_ERRORS=$(docker logs ${CONTAINER_NAME} 2>&1 | grep -i "error\|exception\|traceback" | head -5 || true)

if [ -n "$LOG_ERRORS" ]; then
    echo -e "${YELLOW}⚠️  Found potential errors in logs:${NC}"
    echo "$LOG_ERRORS"
else
    echo -e "${GREEN}✅ No critical errors found in logs${NC}"
fi

# Display container info
echo -e "\n${YELLOW}Container Information:${NC}"
echo "  Image: ${IMAGE_NAME}:latest"
echo "  Container: ${CONTAINER_NAME}"
echo "  Port: ${PORT}"
echo "  Status: $(docker ps --filter name=${CONTAINER_NAME} --format '{{.Status}}')"

# Summary
echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}✅ Docker Image Test Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Container is running. Test endpoints:"
echo "  Health: curl http://localhost:${PORT}/health"
echo "  Docs:   http://localhost:${PORT}/docs"
echo ""
echo "To stop and remove container:"
echo "  docker stop ${CONTAINER_NAME}"
echo "  docker rm ${CONTAINER_NAME}"
echo ""
echo "To view logs:"
echo "  docker logs -f ${CONTAINER_NAME}"
echo ""

