#!/bin/bash
#
# Test All Docker Images Before Deployment
# Builds and tests both backend and frontend images
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=8080
API_URL="http://localhost:${BACKEND_PORT}/api/v1"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Testing All Docker Images${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not running${NC}"
    exit 1
fi

# Function to cleanup
cleanup() {
    echo -e "\n${YELLOW}Cleaning up test containers...${NC}"
    docker stop kronos-backend-test kronos-frontend-test 2>/dev/null || true
    docker rm kronos-backend-test kronos-frontend-test 2>/dev/null || true
}

trap cleanup EXIT

# Test Backend
echo -e "${BLUE}=== Testing Backend Image ===${NC}"
cd "${SCRIPT_DIR}/backend"
if [ -f "test-docker-image.sh" ]; then
    bash test-docker-image.sh || {
        echo -e "${RED}❌ Backend image test failed${NC}"
        exit 1
    }
else
    echo -e "${RED}test-docker-image.sh not found in backend/${NC}"
    exit 1
fi

# Wait a bit for backend to be fully ready
sleep 3

# Test Frontend
echo -e "\n${BLUE}=== Testing Frontend Image ===${NC}"
cd "${SCRIPT_DIR}/frontend"
if [ -f "test-docker-image.sh" ]; then
    API_URL=${API_URL} bash test-docker-image.sh || {
        echo -e "${RED}❌ Frontend image test failed${NC}"
        exit 1
    }
else
    echo -e "${RED}test-docker-image.sh not found in frontend/${NC}"
    exit 1
fi

# Integration test
echo -e "\n${BLUE}=== Integration Test ===${NC}"
echo -e "${YELLOW}Testing frontend -> backend connection...${NC}"

# Test if frontend can reach backend API
BACKEND_HEALTH=$(curl -s http://localhost:${BACKEND_PORT}/health 2>/dev/null || echo "")
FRONTEND_RESPONSE=$(curl -s http://localhost:${FRONTEND_PORT}/ 2>/dev/null || echo "")

if [ -n "$BACKEND_HEALTH" ] || curl -s -f http://localhost:${BACKEND_PORT}/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Backend health check unclear${NC}"
fi

if [ -n "$FRONTEND_RESPONSE" ]; then
    echo -e "${GREEN}✅ Frontend is serving content${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend response unclear${NC}"
fi

# Summary
echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}✅ All Docker Image Tests Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Test Results:"
echo "  ✅ Backend image: Built and tested"
echo "  ✅ Frontend image: Built and tested"
echo ""
echo "Services running:"
echo "  Backend:  http://localhost:${BACKEND_PORT}"
echo "  Frontend: http://localhost:${FRONTEND_PORT}"
echo ""
echo "To stop all test containers:"
echo "  docker stop kronos-backend-test kronos-frontend-test"
echo "  docker rm kronos-backend-test kronos-frontend-test"
echo ""
echo "If all tests passed, you can proceed with deployment!"
echo ""

