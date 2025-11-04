# 🚀 Start Testing - Frontend + Backend Integration

## Quick Start (Recommended)

```bash
cd /home/bloom/sentrics/kronos-eam-consolidated
./QUICK_TEST_START.sh
```

This will start everything automatically!

---

## Manual Start (Step by Step)

### 1. Start Database

```bash
cd backend
docker-compose up -d

# Wait 10 seconds for database to initialize
sleep 10

# Verify database is ready
docker exec kronos-eam-db pg_isready -U postgres
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Create .env file (first time only)
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kronos_eam
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ENVIRONMENT=development
DEBUG=True
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF

# Run migrations
alembic upgrade head

# Create test user
python scripts/create_test_user.py
```

### 3. Start Backend Server

```bash
cd backend
source venv/bin/activate  # If not already activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Open http://localhost:8000/docs - Should see Swagger UI

### 4. Setup Frontend (New Terminal)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Create .env file (first time only)
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Start development server
npm run dev
```

**Verify**: Open http://localhost:5173 - Should see login page

---

## 🧪 Test the Integration

### Test Login

1. Open http://localhost:5173
2. Enter credentials:
   - **Email**: `test@example.com`
   - **Password**: `test123`
3. Click "Sign in"
4. Should redirect to Dashboard

### Test Dashboard

- Should show statistics cards
- Should show recent activity
- Should display plant count, CER count, etc.

### Test Plants Page

- Navigate to "Plants" in sidebar
- Should show plants list (empty initially)
- Can create new plant via API

### Test CER Page

- Navigate to "CER" in sidebar
- Should show CER communities list (empty initially)
- Can create new CER via API

### Test API Directly

1. Open http://localhost:8000/docs
2. Click "Authorize"
3. Login via Swagger UI to get token
4. Test endpoints:
   - GET `/api/v1/dashboard/stats`
   - GET `/api/v1/plants`
   - GET `/api/v1/cer/communities`

---

## ✅ Verification Checklist

- [ ] Database running (check `docker ps`)
- [ ] Backend running (check http://localhost:8000/health)
- [ ] Frontend running (check http://localhost:5173)
- [ ] Can login through frontend
- [ ] Dashboard loads and shows data
- [ ] Plants page loads
- [ ] CER page loads
- [ ] API docs accessible
- [ ] No console errors in browser

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Check database connection
docker exec kronos-eam-db psql -U postgres -d kronos_eam -c "SELECT 1;"

# Check backend logs
tail -f backend.log  # if using script
```

### Frontend won't start

```bash
# Check if port 5173 is in use
lsof -i :5173

# Check node_modules
rm -rf node_modules package-lock.json
npm install

# Check .env file
cat .env
```

### CORS errors

```bash
# Check backend .env has correct CORS origins
cat backend/.env | grep CORS

# Should include frontend URL
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

### Login fails

```bash
# Check test user exists
cd backend
source venv/bin/activate
python scripts/create_test_user.py

# Check database
docker exec -it kronos-eam-db psql -U postgres -d kronos_eam -c "SELECT email FROM users;"
```

---

## 📊 What to Test

### Backend API
- ✅ Health endpoint
- ✅ Login endpoint
- ✅ Get current user
- ✅ Dashboard stats
- ✅ Plants CRUD
- ✅ CER CRUD
- ✅ Assets CRUD

### Frontend Pages
- ✅ Login page
- ✅ Dashboard
- ✅ Plants list
- ✅ Plant detail
- ✅ CER list
- ✅ CER detail
- ✅ Workflows
- ✅ Compliance

### Integration
- ✅ Authentication flow
- ✅ API calls from frontend
- ✅ Data display
- ✅ Navigation
- ✅ Error handling

---

## 🎯 Success Criteria

**Backend**:
- ✅ All endpoints respond
- ✅ Authentication works
- ✅ Multi-tenant filtering works
- ✅ Database queries succeed

**Frontend**:
- ✅ Pages load without errors
- ✅ API calls succeed
- ✅ Data displays correctly
- ✅ Navigation works
- ✅ Authentication persists

**Integration**:
- ✅ Frontend can call backend APIs
- ✅ Auth tokens work
- ✅ Data flows correctly
- ✅ Errors handled gracefully

---

**Ready to test! Follow the steps above and verify everything works!** 🚀


