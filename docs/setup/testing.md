# Testing Guide - Frontend + Backend Integration

**Quick Start Guide for Testing the Consolidated Platform**

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (via Docker)

---

## Step 1: Start Database

```bash
cd kronos-eam-consolidated/backend
docker-compose up -d

# Wait for database to be ready (10-15 seconds)
docker ps | grep kronos-eam-db
```

---

## Step 2: Setup Backend

```bash
cd kronos-eam-consolidated/backend

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
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF

# Run migrations
alembic upgrade head

# Create test user (optional - use SQL or Python script)
```

---

## Step 3: Start Backend Server

```bash
cd kronos-eam-consolidated/backend
source venv/bin/activate  # If not already activated

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Open http://localhost:8000/docs - Should see Swagger UI

---

## Step 4: Setup Frontend

```bash
cd kronos-eam-consolidated/frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000/api/v1
EOF

# Start development server
npm run dev
```

**Verify**: Open http://localhost:5173 (or port shown) - Should see login page

---

## Step 5: Create Test User

### Option 1: Using Python Script

```bash
cd kronos-eam-consolidated/backend
source venv/bin/activate

python << EOF
from app.core.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import get_password_hash
from datetime import datetime, timedelta

# Get database session
db = next(get_db())

# Create test tenant
tenant = Tenant(
    id="demo",
    name="Demo Tenant",
    status="Active",
    plan="free",
    plan_expiry=datetime.utcnow() + timedelta(days=365)
)
db.add(tenant)
db.commit()

# Create test user
user = User(
    tenant_id="demo",
    name="Test User",
    email="test@example.com",
    password_hash=get_password_hash("test123"),
    role="Admin",
    status="Active",
    email_verified=True
)
db.add(user)
db.commit()

print(f"Created user: {user.email} / test123")
print(f"Tenant: {tenant.id}")
EOF
```

### Option 2: Using SQL

```bash
docker exec -it kronos-eam-db psql -U postgres -d kronos_eam

-- Create tenant
INSERT INTO tenants (id, name, status, plan, plan_expiry, created_at)
VALUES ('demo', 'Demo Tenant', 'Active', 'free', NOW() + INTERVAL '365 days', NOW());

-- Create user (password: test123)
INSERT INTO users (tenant_id, name, email, password_hash, role, status, email_verified, created_at)
VALUES (
  'demo',
  'Test User',
  'test@example.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJLjXZKKi',  -- bcrypt hash of 'test123'
  'Admin',
  'Active',
  true,
  NOW()
);
```

---

## Step 6: Test Login

1. Open frontend: http://localhost:5173
2. Login with:
   - **Email**: `test@example.com`
   - **Password**: `test123`
3. Should redirect to Dashboard

---

## Step 7: Test API Endpoints

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Test endpoints directly

### Using curl

```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123" \
  | jq -r '.access_token')

# Get plants
curl -X GET "http://localhost:8000/api/v1/plants" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: demo"

# Get dashboard stats
curl -X GET "http://localhost:8000/api/v1/dashboard/stats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: demo"
```

---

## 🧪 Test Scenarios

### 1. Create Plant
```bash
curl -X POST "http://localhost:8000/api/v1/plants" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: demo" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Solar Plant",
    "code": "SOL-001",
    "power": "1.5 MW",
    "power_kw": 1500,
    "status": "In Operation",
    "type": "Photovoltaic",
    "location": "Rome, Italy",
    "region": "Lazio"
  }'
```

### 2. Create CER
```bash
curl -X POST "http://localhost:8000/api/v1/cer/communities" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: demo" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test CER Community",
    "legal_type": "cooperative",
    "type": "active",
    "address": "Via Test 123",
    "region": "Lazio",
    "primary_substation_id": "SUB-001"
  }'
```

### 3. Link Plant to CER
```bash
# Get plant ID and CER ID from previous responses, then:
curl -X POST "http://localhost:8000/api/v1/plants/1/link-cer/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: demo"
```

---

## 🐛 Troubleshooting

### Backend Issues

**Database connection error**:
```bash
# Check database is running
docker ps | grep kronos-eam-db

# Check logs
docker logs kronos-eam-db

# Test connection
docker exec -it kronos-eam-db psql -U postgres -d kronos_eam -c "SELECT 1;"
```

**Migration errors**:
```bash
# Check migration status
alembic current

# Downgrade and retry
alembic downgrade -1
alembic upgrade head
```

**Port already in use**:
```bash
# Change port in uvicorn command
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Issues

**API connection error**:
- Check `.env` file has correct `VITE_API_URL`
- Check backend is running on port 8000
- Check CORS settings in backend

**Module not found**:
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Build errors**:
```bash
# Check TypeScript errors
npm run build

# Fix import paths
# Ensure all @/ imports resolve correctly
```

---

## ✅ Verification Checklist

- [ ] Database running (PostgreSQL + PostGIS)
- [ ] Backend server running (port 8000)
- [ ] Frontend dev server running (port 5173)
- [ ] Test user created
- [ ] Can login through frontend
- [ ] Dashboard loads
- [ ] Plants page loads
- [ ] CER page loads
- [ ] API endpoints accessible via Swagger UI

---

## 📝 Next Steps After Testing

1. **Create seed data** - Add sample plants, CERs, assets
2. **Test all CRUD operations** - Create, read, update, delete
3. **Test relationships** - Link plants to CERs, add assets to plants
4. **Test workflows** - Create and complete workflows
5. **Test compliance** - Create requirements and records

---

## 🎯 Expected Results

**Frontend**:
- ✅ Login page loads
- ✅ Dashboard shows statistics
- ✅ Plants page lists plants
- ✅ CER page lists communities
- ✅ Navigation works

**Backend**:
- ✅ Swagger UI accessible
- ✅ All endpoints respond
- ✅ Authentication works
- ✅ Multi-tenant filtering works
- ✅ Database queries succeed

---

**Ready to test!** 🚀


