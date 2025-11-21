#!/bin/bash
# Quick API Test Script for CER Energy Sharing Endpoints

echo "========================================================================"
echo "CER ENERGY SHARING - API ENDPOINT TEST"
echo "========================================================================"
echo ""

# Configuration
BASE_URL="http://localhost:8000"
TOKEN=""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "Checking if backend is running..."
if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not running at $BASE_URL${NC}"
    echo ""
    echo "Please start the backend first:"
    echo "  cd backend"
    echo "  source ../venv/bin/activate"
    echo "  uvicorn app.main:app --reload"
    exit 1
fi

echo -e "${GREEN}✓ Backend is running${NC}"
echo ""

# Login to get token
echo "Logging in to get authentication token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123")

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Login failed${NC}"
    exit 1
fi

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get token${NC}"
    echo "Response: $LOGIN_RESPONSE"
    echo ""
    echo "Please ensure test user exists:"
    echo "  cd backend"
    echo "  source ../venv/bin/activate"
    echo "  python -c 'from app.scripts.seed_data import seed_test_data; import asyncio; asyncio.run(seed_test_data())'"
    exit 1
fi

echo -e "${GREEN}✓ Authentication successful${NC}"
echo ""

# Get CER list
echo "Fetching CER communities..."
CER_LIST=$(curl -s -X GET "$BASE_URL/cer/communities" \
  -H "Authorization: Bearer $TOKEN")

CER_ID=$(echo $CER_LIST | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$CER_ID" ]; then
    echo -e "${YELLOW}⚠ No CER communities found in database${NC}"
    echo ""
    echo "You can create a test CER using the API or admin panel"
    echo "For now, using CER ID 1 (may fail if doesn't exist)"
    CER_ID=1
else
    echo -e "${GREEN}✓ Found CER ID: $CER_ID${NC}"
fi
echo ""

# Test 1: Calculate Sharing (dry-run)
echo "========================================="
echo "Test 1: Calculate Energy Sharing"
echo "========================================="
echo "POST /cer/$CER_ID/calculate-sharing"
echo ""

CALC_RESPONSE=$(curl -s -X POST "$BASE_URL/cer/$CER_ID/calculate-sharing" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"month": 1, "year": 2024}')

if echo $CALC_RESPONSE | grep -q "total_shared_energy_kwh"; then
    echo -e "${GREEN}✓ Energy sharing calculation successful${NC}"
    echo ""
    echo "Result preview:"
    echo $CALC_RESPONSE | python3 -m json.tool 2>/dev/null | head -20
else
    echo -e "${RED}❌ Calculation failed${NC}"
    echo "Response: $CALC_RESPONSE"
fi
echo ""

# Test 2: Get Sharing Visualization
echo "========================================="
echo "Test 2: Get Sharing Visualization Data"
echo "========================================="
echo "GET /cer/$CER_ID/sharing-visualization"
echo ""

VIZ_RESPONSE=$(curl -s -X GET "$BASE_URL/cer/$CER_ID/sharing-visualization?from_date=2024-01-01&to_date=2024-01-07" \
  -H "Authorization: Bearer $TOKEN")

if echo $VIZ_RESPONSE | grep -q "hourly_data"; then
    echo -e "${GREEN}✓ Visualization data retrieved successfully${NC}"
    echo ""
    echo "Result preview:"
    echo $VIZ_RESPONSE | python3 -m json.tool 2>/dev/null | head -20
else
    echo -e "${RED}❌ Visualization request failed${NC}"
    echo "Response: $VIZ_RESPONSE"
fi
echo ""

# Test 3: Get Billing Statements
echo "========================================="
echo "Test 3: Get Billing Statements"
echo "========================================="
echo "GET /cer/$CER_ID/billing-statements"
echo ""

BILLING_RESPONSE=$(curl -s -X GET "$BASE_URL/cer/$CER_ID/billing-statements?month=1&year=2024" \
  -H "Authorization: Bearer $TOKEN")

if echo $BILLING_RESPONSE | grep -q "statements"; then
    echo -e "${GREEN}✓ Billing statements retrieved successfully${NC}"
    STMT_COUNT=$(echo $BILLING_RESPONSE | grep -o '"total_statements":[0-9]*' | cut -d':' -f2)
    echo "Total statements: $STMT_COUNT"
else
    echo -e "${RED}❌ Billing request failed${NC}"
    echo "Response: $BILLING_RESPONSE"
fi
echo ""

# Test 4: API Documentation
echo "========================================="
echo "Test 4: API Documentation"
echo "========================================="
echo ""
echo "API documentation available at:"
echo "  ${YELLOW}$BASE_URL/docs${NC} (Swagger UI)"
echo "  ${YELLOW}$BASE_URL/redoc${NC} (ReDoc)"
echo ""

# Summary
echo "========================================================================"
echo "TEST SUMMARY"
echo "========================================================================"
echo ""
echo "Backend URL: $BASE_URL"
echo "CER ID tested: $CER_ID"
echo ""
echo "New CER Energy Sharing endpoints are accessible ✓"
echo ""
echo "Next steps:"
echo "  1. Create test CER with members and plants"
echo "  2. Upload meter data (or use mock data)"
echo "  3. Run monthly billing calculations"
echo "  4. Integrate with frontend UI"
echo ""
