# Quick Start Guide - Fresh Installation

This guide will help you set up Kronos EAM from scratch on a new device.

---

## Prerequisites

Before starting, ensure you have:

- **Podman** (or Docker) - Container runtime
- **Python 3.11+** - Backend runtime
- **Node.js 18+** and **npm** - Frontend build tools

### Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y podman python3 python3-venv python3-pip
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Fedora/RHEL:**
```bash
sudo dnf install -y podman python3 python3-pip nodejs npm
```

**macOS:**
```bash
brew install podman python@3.11 node
```

---

## One-Command Setup

For a completely fresh installation, run:

```bash
cd backend
./setup-from-scratch.sh
```

This script will:
1. ✅ Check all prerequisites
2. ✅ Create Python virtual environment
3. ✅ Install backend dependencies
4. ✅ Install frontend dependencies
5. ✅ Start containers (PostgreSQL + Redis)
6. ✅ Initialize database
7. ✅ Create tables
8. ✅ Seed test data (tenant, user, plants, assets)
9. ✅ Start backend server
10. ✅ Start frontend server

---

## Manual Setup (Step by Step)

If you prefer to set up manually:

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Services

```bash
# Start all services (containers + apps)
./start-services.sh

# Or start step by step:
# - Start containers only
./start-services.sh --skip-seed --skip-frontend

# - Start without seeding (if data already exists)
./start-services.sh --skip-seed
```

### 3. Access Application

Once started, access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

**Default Credentials:**
- Email: `test@example.com`
- Password: `test123`

---

## Stop Services

```bash
cd backend
./stop-services.sh
```

---

## Troubleshooting

### Database Connection Issues

If the database isn't connecting:
```bash
# Check container status
podman ps

# Check database logs
podman logs kronos-eam-db

# Restart containers
podman restart kronos-eam-db
```

### Port Already in Use

If ports 3000, 8000, 5432, or 6379 are in use:
```bash
# Find what's using the port
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # Frontend
sudo lsof -i :5432  # Database
sudo lsof -i :6379  # Redis

# Stop conflicting services or change ports in:
# - Backend: app/core/config.py
# - Frontend: vite.config.ts
# - Containers: docker-compose.yml or start-services.sh
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Build Issues

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database Reset (Clean Start)

⚠️ **Warning**: This will delete all data!

```bash
# Stop services
./stop-services.sh

# Remove containers and volumes
podman stop kronos-eam-db kronos-eam-redis
podman rm kronos-eam-db kronos-eam-redis
podman volume rm kronos_eam_postgres_data kronos_eam_redis_data

# Restart
./start-services.sh
```

---

## Development Workflow

### Daily Startup

```bash
cd backend
./start-services.sh
```

### View Logs

```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
tail -f /tmp/frontend.log

# Database logs
podman logs -f kronos-eam-db

# Redis logs
podman logs -f kronos-eam-redis
```

### Code Changes

- **Backend**: Auto-reloads on code changes (uvicorn --reload)
- **Frontend**: Hot Module Replacement (HMR) enabled

### Database Migrations

```bash
cd backend
source venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## What Gets Created

### Database Tables
- `users` - User accounts
- `tenants` - Multi-tenant organizations
- `plants` - Power plants
- `sites` - Plant sites
- `assets` - Equipment/assets
- `asset_types` - Asset type definitions
- `cer_configuration` - CER entities
- `cer_members` - CER members
- `workflows` - Workflow templates
- `documents` - Document storage
- And more...

### Test Data
- **Tenant**: `demo` (Demo Tenant)
- **User**: `test@example.com` / `test123` (Admin)
- **Plants**: 6 test plants (solar, wind, hydro)
- **Assets**: 22+ test assets (panels, inverters, etc.)
- **Sites**: 3 test sites
- **Storage Units**: 2 BESS units
- **Consumers**: 3 test consumers

---

## Next Steps

1. **Login**: Use `test@example.com` / `test123`
2. **Explore**: Navigate to Plants, Sites, Assets
3. **API**: Check http://localhost:8000/docs
4. **Customize**: Modify seed data in `app/api/v1/endpoints/dev.py`

---

## Support

For issues or questions:
- Check logs: `tail -f /tmp/backend.log`
- Review documentation: `README.md`
- Check container status: `podman ps`

---

**Happy coding! 🚀**
