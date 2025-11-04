#!/bin/bash
# Quick Test Start Script
# Starts both backend and frontend for testing

set -e

echo "🚀 Starting Kronos EAM Consolidated Platform..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start database
echo -e "${BLUE}📦 Starting database...${NC}"
cd backend
docker-compose up -d
sleep 5

# Check if database is ready
if ! docker exec kronos-eam-db pg_isready -U postgres > /dev/null 2>&1; then
    echo "❌ Database is not ready. Please check docker-compose logs."
    exit 1
fi

echo -e "${GREEN}✅ Database is running${NC}"

# Setup backend if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Setting up backend virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kronos_eam
SECRET_KEY=$SECRET_KEY
ENVIRONMENT=development
DEBUG=True
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF
fi

# Run migrations
echo -e "${BLUE}🔄 Running database migrations...${NC}"
alembic upgrade head

# Create test user
echo -e "${BLUE}👤 Creating test user...${NC}"
python scripts/create_test_user.py || echo "⚠️  Could not create test user (may already exist)"

# Start backend in background
echo -e "${BLUE}🔧 Starting backend server...${NC}"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Check if backend started
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start. Check backend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ Backend is running on http://localhost:8000${NC}"

# Setup frontend
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating frontend .env file...${NC}"
    echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
fi

# Start frontend
echo -e "${BLUE}🎨 Starting frontend server...${NC}"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 3

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Platform is running!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "📍 Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "📍 API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
echo -e "📍 Frontend:     ${BLUE}http://localhost:5173${NC}"
echo ""
echo -e "👤 Test Credentials:"
echo -e "   Email:    ${YELLOW}test@example.com${NC}"
echo -e "   Password: ${YELLOW}test123${NC}"
echo ""
echo -e "📝 Logs:"
echo -e "   Backend:  ${BLUE}tail -f backend.log${NC}"
echo -e "   Frontend: ${BLUE}tail -f frontend.log${NC}"
echo ""
echo -e "🛑 To stop:"
echo -e "   kill $BACKEND_PID $FRONTEND_PID"
echo -e "   docker-compose -f backend/docker-compose.yml down"
echo ""
echo -e "${GREEN}Happy testing! 🎉${NC}"

# Wait for user interrupt
wait


