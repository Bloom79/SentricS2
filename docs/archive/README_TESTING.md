# Quick Testing Guide

## 🚀 Fastest Way to Start

```bash
cd kronos-eam-consolidated
./QUICK_TEST_START.sh
```

This script will:
1. ✅ Start PostgreSQL with PostGIS
2. ✅ Setup backend virtual environment
3. ✅ Run database migrations
4. ✅ Create test user
5. ✅ Start backend server (port 8000)
6. ✅ Start frontend server (port 5173)

---

## 📍 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 👤 Test Credentials

- **Email**: `test@example.com`
- **Password**: `test123`
- **Tenant**: `demo`

---

## 🧪 Quick Test

1. Open http://localhost:5173
2. Login with test credentials
3. Navigate to Dashboard
4. Check Plants page
5. Check CER page
6. Test API at http://localhost:8000/docs

---

## 🛑 Stop Everything

```bash
# Stop servers
pkill -f "uvicorn app.main:app"
pkill -f "vite"

# Stop database
cd backend
docker-compose down
```

---

## 🐛 Troubleshooting

**Port 8000 in use**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Port 5173 in use**:
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**Database not starting**:
```bash
cd backend
docker-compose down
docker-compose up -d
docker logs kronos-eam-db
```

---

**Ready to test!** 🎉


