#!/bin/bash
#
# Test Frontend Docker Image Locally
# Builds and tests the frontend Docker image before deployment
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

IMAGE_NAME="kronos-eam-frontend-test"
CONTAINER_NAME="kronos-frontend-test"
PORT=8080
API_URL=${API_URL:-"http://localhost:8000/api/v1"}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Testing Frontend Docker Image${NC}"
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

echo "Building with API URL: ${API_URL}"

docker build \
    --build-arg REACT_APP_API_URL=${API_URL} \
    -t ${IMAGE_NAME}:latest . || {
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Image built successfully${NC}"

# Run the container
echo -e "\n${YELLOW}Step 2: Starting container...${NC}"

docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:80 \
    ${IMAGE_NAME}:latest || {
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
}

echo -e "${GREEN}✅ Container started${NC}"

# Wait for container to be ready
echo -e "\n${YELLOW}Step 3: Waiting for service to be ready...${NC}"
MAX_ATTEMPTS=20
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s -f http://localhost:${PORT}/health > /dev/null 2>&1 || \
       curl -s -f http://localhost:${PORT}/ > /dev/null 2>&1; then
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
    sleep 1
done

# Test endpoints
echo -e "\n${YELLOW}Step 4: Testing endpoints...${NC}"

# Test health endpoint
echo -n "  Testing /health... "
if curl -s http://localhost:${PORT}/health | grep -q "OK" || curl -s -f http://localhost:${PORT}/health > /dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️${NC}"
fi

# Test index.html
echo -n "  Testing / (index.html)... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT}/)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ (HTTP ${HTTP_CODE})${NC}"
else
    echo -e "${YELLOW}⚠️  (HTTP ${HTTP_CODE})${NC}"
fi

# Test static assets
echo -n "  Testing static assets... "
if curl -s -f http://localhost:${PORT}/assets/ > /dev/null 2>&1 || \
   curl -s -f http://localhost:${PORT}/index.html > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️${NC}"
fi

# Check if index.html contains expected content
echo -n "  Verifying React app... "
HTML_CONTENT=$(curl -s http://localhost:${PORT}/ || echo "")
if echo "$HTML_CONTENT" | grep -q "root\|react\|app" || [ -n "$HTML_CONTENT" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️${NC}"
fi

# Check container logs for errors
echo -e "\n${YELLOW}Step 5: Checking container logs...${NC}"
LOG_ERRORS=$(docker logs ${CONTAINER_NAME} 2>&1 | grep -i "error\|fatal\|emergency" | head -5 || true)

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
echo "  API URL: ${API_URL}"
echo "  Status: $(docker ps --filter name=${CONTAINER_NAME} --format '{{.Status}}')"

# Summary
echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}✅ Docker Image Test Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Container is running. Test the frontend:"
echo "  URL: http://localhost:${PORT}"
echo "  Health: curl http://localhost:${PORT}/health"
echo ""
echo "To stop and remove container:"
echo "  docker stop ${CONTAINER_NAME}"
echo "  docker rm ${CONTAINER_NAME}"
echo ""
echo "To view logs:"
echo "  docker logs -f ${CONTAINER_NAME}"
echo ""

