# Kronos EAM - Consolidated Enterprise Platform

<div align="center">

**Complete Enterprise Asset Management for Italian Renewable Energy**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/Bloom79/kronos-eam/releases)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)

</div>

---

## 🌟 Overview

**Kronos EAM** is a comprehensive, enterprise-grade SaaS platform for managing renewable energy assets in Italy. This consolidated version combines:

- ✅ **Complete Compliance Management** (from Kronos EAM)
- ✅ **CER (Renewable Energy Communities)** support (from Sentrics)
- ✅ **Advanced Asset Management** (from Sentrics)
- ✅ **Workflow Automation** (from Kronos EAM)
- ✅ **Government Portal Integration** (from Kronos EAM)
- ✅ **Geographic Intelligence** (PostGIS from Sentrics)

### Key Features

#### 🏭 Plant & Asset Management
- **Complete Plant Registry**: Multi-tenant plant database with full lifecycle management
- **Advanced Asset Tracking**: Detailed equipment management (panels, inverters, batteries)
- **Asset Monitoring**: Real-time performance tracking
- **Maintenance Management**: Preventive and corrective maintenance scheduling

#### 🔄 Workflow & Compliance
- **Automated Workflows**: Pre-built templates for all regulatory processes
- **Annual Compliance Automation**: Never miss critical deadlines
- **Smart Deadline Calculator**: Intelligent deadline prediction
- **Penalty Prevention**: Cost analysis and risk mitigation
- **Document Management**: Centralized repository with versioning

#### 👥 CER (Renewable Energy Communities)
- **CER Setup & Management**: Complete lifecycle management
- **Member Management**: POD tracking, load profiles, billing
- **PNRR Funding Support**: 40% grant application workflows
- **Energy Sharing**: Production allocation and billing
- **Geographic Boundaries**: PostGIS-powered boundary management

#### 🔗 Government Portal Integration
- **GSE Integration**: RID activation, Fuel Mix, Anti-Mafia declarations
- **Terna GAUDÌ**: Plant registration and technical data
- **DSO Integration**: Connection management, TICA workflows
- **Agenzia Dogane**: UTF license management, EDI file generation

#### 📊 Analytics & Reporting
- **Compliance Scoring**: Real-time compliance percentage
- **Portfolio Analytics**: Multi-plant dashboard
- **Cost Tracking**: Fees, penalties, and administrative costs
- **Performance Monitoring**: Energy production/consumption tracking

---

## 🏗️ Architecture

### Technology Stack

**Backend**:
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 with PostGIS extension
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT with OAuth2
- **Caching**: Redis
- **Task Queue**: Celery

**Frontend**:
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **State Management**: React Query + Zustand
- **UI Library**: Tailwind CSS + shadcn/ui
- **Maps**: Leaflet + React Leaflet
- **Forms**: React Hook Form + Zod

**Infrastructure**:
- **Cloud**: Google Cloud Platform
- **Containers**: Docker + Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

### Multi-Tenant Architecture

- **Database**: Row-level security with `tenant_id`
- **API**: Automatic tenant filtering
- **Frontend**: Tenant-aware routing
- **Isolation**: Complete data segregation

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+ with PostGIS extension (running locally on port 5432)
- Redis (running locally on port 6379)
- Git with GitHub authentication configured

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Bloom79/SentricS2.git
cd SentricS2

# 2. Create Python virtual environment (at project root)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Configure environment variables
# Create .env file in backend directory
cat > .env << EOF
# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://0.0.0.0:3000","http://localhost:5173","http://127.0.0.1:5173","http://0.0.0.0:5173"]

# Database (ensure PostgreSQL with PostGIS is running)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kronos_eam

# Redis (ensure Redis is running)
REDIS_URL=redis://localhost:6379/0

# Optional: Set a persistent SECRET_KEY to prevent token invalidation on restart
# SECRET_KEY=your-secret-key-here
EOF

# 5. Initialize database
# Make sure PostgreSQL with PostGIS extension is running
alembic stamp head  # Mark database as up-to-date with migrations

# 6. Seed test data
python scripts/seed_test_data.py

# 7. Install frontend dependencies
cd ../frontend
npm install

# 8. Start development servers

# Terminal 1 - Backend (from backend directory)
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (from frontend directory)
cd frontend
npm run dev
```

### Access Points

- **Frontend**: http://localhost:5173 (Vite dev server)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Documentation**: http://localhost:8000/redoc (ReDoc)

### Default Credentials

After running the seed script, use these credentials to log in:

- **Email**: `test@example.com`
- **Password**: `test123`

### Database Setup

The application requires PostgreSQL 15+ with the PostGIS extension:

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE kronos_eam;

-- Connect to the database
\c kronos_eam

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Troubleshooting

**401 Unauthorized Errors**: 
- Clear browser localStorage (F12 → Application → Local Storage → Clear)
- Refresh the page to be redirected to login
- If SECRET_KEY is not set in .env, tokens are invalidated on backend restart

**CORS Errors**:
- Ensure `.env` file exists in `backend/` directory
- Verify CORS origins include your frontend URL

**Database Connection Errors**:
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check database credentials in connection string
- Verify PostGIS extension is installed: `SELECT PostGIS_Version();`

**Import Errors**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

---

## 📁 Project Structure

```
kronos-eam/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── plants.py
│   │   │       │   ├── cer.py          # NEW: CER endpoints
│   │   │       │   ├── assets.py       # NEW: Asset endpoints
│   │   │       │   ├── workflows.py
│   │   │       │   ├── documents.py
│   │   │       │   └── compliance.py
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── plant.py
│   │   │   ├── cer.py         # NEW: CER model
│   │   │   ├── cer_member.py  # NEW: Member model
│   │   │   ├── asset.py        # NEW: Asset model
│   │   │   ├── workflow.py
│   │   │   └── document.py
│   │   ├── services/          # Business logic
│   │   │   ├── plant_service.py
│   │   │   ├── cer_service.py # NEW: CER service
│   │   │   ├── asset_service.py # NEW: Asset service
│   │   │   ├── workflow_service.py
│   │   │   └── compliance_service.py
│   │   ├── core/              # Core functionality
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── geography.py   # NEW: PostGIS helpers
│   │   │   └── config.py
│   │   └── schemas/           # Pydantic schemas
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   └── requirements.txt
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Plants/        # Plant management
│   │   │   ├── CER/          # NEW: CER management
│   │   │   ├── Workflows/    # Workflow management
│   │   │   ├── Compliance/   # Compliance tracking
│   │   │   └── Dashboard/   # Analytics dashboard
│   │   ├── components/
│   │   │   ├── plants/       # Plant components
│   │   │   ├── cer/         # NEW: CER components
│   │   │   ├── assets/      # NEW: Asset components
│   │   │   └── common/      # Shared components
│   │   ├── services/         # API clients
│   │   ├── hooks/           # React hooks
│   │   └── utils/           # Utilities
│   └── package.json
│
├── docs/                      # Documentation
│   ├── architecture.md
│   ├── api-reference.md
│   └── deployment.md
│
├── deploy/                    # Deployment scripts
│   └── gcp/                  # GCP deployment configs
│
└── scripts/                   # Utility scripts
    └── setup.sh
```

---

## 🔑 Key Modules

### 1. Plant Management
Complete lifecycle management for renewable energy plants:
- Plant registry with technical specifications
- Multi-dimensional organization (type, power, location, status)
- Integration status tracking (DSO, Terna, GSE, ADM)
- Compliance scoring
- Deadline management

### 2. CER (Renewable Energy Communities)
Full support for Italian energy communities:
- CER constitution and legal setup
- Member management with POD tracking
- PNRR funding application (40% grant)
- Energy sharing and billing
- Geographic boundary management
- GSE compliance tracking

### 3. Asset Management
Detailed equipment tracking:
- Asset type system (flexible attributes)
- Asset instances (panels, inverters, batteries)
- Hierarchical organization (parent-child relationships)
- Monitoring integration
- Maintenance tracking

### 4. Workflow Automation
Intelligent workflow management:
- Pre-built templates (activation, compliance, fiscal)
- Phase-based execution
- Task assignment and tracking
- Document generation
- Portal integration

### 5. Compliance Management
Automated compliance tracking:
- Annual recurring obligations
- Smart deadline calculation
- Penalty prevention
- Compliance scoring
- Document expiration tracking

### 6. Government Portal Integration
Smart integration with Italian authorities:
- GSE portal (RID, Fuel Mix, Anti-Mafia)
- Terna GAUDÌ (plant registration)
- DSO portals (connection management)
- Agenzia Dogane (UTF license, EDI files)

---

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment.md)
- [Development Guide](docs/development.md)
- [CER Management Guide](docs/cer-management.md)
- [Compliance Guide](docs/compliance.md)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 🚢 Deployment

### Production Deployment

```bash
# GCP Deployment
cd deploy/gcp
./deploy.sh
```

See [deployment guide](docs/deployment.md) for detailed instructions.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ for the Italian renewable energy sector

---

<div align="center">
  <p>© 2025 Kronos EAM. All rights reserved.</p>
</div>

