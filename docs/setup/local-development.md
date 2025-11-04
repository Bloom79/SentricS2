# Setup Instructions - Kronos EAM Consolidated

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (via Docker)

### Step 1: Clone and Setup

```bash
# If cloning from GitHub
git clone https://github.com/Bloom79/kronos-eam.git
cd kronos-eam

# Or if using local consolidated project
cd kronos-eam-consolidated
```

### Step 2: Database Setup

```bash
cd backend
docker-compose up -d

# Wait for database to be ready (10-15 seconds)
# Verify PostGIS is enabled
docker exec kronos-eam-db psql -U postgres -d kronos_eam -c "SELECT PostGIS_version();"
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kronos_eam
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
ENVIRONMENT=development
DEBUG=True
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
EOF

# Run migrations
alembic upgrade head

# Verify tables created
docker exec kronos-eam-db psql -U postgres -d kronos_eam -c "\dt"
```

### Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000/api/v1
EOF

# Start development server
npm run dev
```

### Step 5: Verify Installation

**Backend**:
```bash
# Test API
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# Test docs
open http://localhost:8000/docs
```

**Frontend**:
```bash
# Open browser
open http://localhost:3000
```

---

## Database Migrations

### Create New Migration

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

---

## Development Commands

### Backend
```bash
# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Format code
black app/

# Lint
flake8 app/
```

### Frontend
```bash
# Development server
npm run dev

# Build
npm run build

# Tests
npm test

# Lint
npm run lint
```

---

## Troubleshooting

### PostGIS Not Available
```bash
# Enable PostGIS manually
docker exec -it kronos-eam-db psql -U postgres -d kronos_eam
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
```

### Database Connection Error
```bash
# Check database is running
docker ps | grep kronos-eam-db

# Check connection
docker exec kronos-eam-db pg_isready -U postgres
```

---

## Production Deployment

See `docs/deployment.md` for production deployment instructions.

