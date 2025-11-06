# SentricS2 - Enterprise Asset Management for Renewable Energy

<div align="center">

**Complete Enterprise Asset Management Platform for Italian Renewable Energy Sector**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/Bloom79/SentricS2/releases)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Deployment](https://img.shields.io/badge/deployment-GCP-4285F4.svg)](https://cloud.google.com/)

</div>

---

## 🌟 Overview

**SentricS2** (formerly Kronos EAM) is a comprehensive, production-grade SaaS platform designed specifically for managing renewable energy assets in Italy. Built with modern technologies and cloud-native architecture, it provides complete lifecycle management from planning to compliance.

### What We Solve

- ✅ **Regulatory Compliance** - Navigate complex Italian energy regulations (GSE, Terna, DSO, ADM)
- ✅ **Asset Management** - Track and monitor renewable energy equipment with real-time insights
- ✅ **Community Energy (CER)** - Manage Renewable Energy Communities with PNRR funding support
- ✅ **Workflow Automation** - Streamline multi-phase regulatory processes
- ✅ **Financial Tracking** - Complete billing and cost management
- ✅ **Document Management** - Centralized repository with version control

---

## 🚀 Key Features

### 🏭 Plant & Asset Management
- Multi-tenant plant registry with complete lifecycle tracking
- Visual plant designer with drag-and-drop interface (React Flow)
- Detailed asset tracking (panels, inverters, batteries, transformers)
- Real-time performance monitoring and alerts
- Predictive maintenance scheduling

### 👥 CER (Community Energy Resources)
- Complete CER lifecycle management
- Member onboarding and POD tracking
- PNRR funding application (40% grant support)
- Energy sharing optimization and billing
- Geographic boundary management (PostGIS)

### 🔄 Workflow & Compliance
- Pre-built templates for all regulatory processes
- 8-phase activation workflow automation
- Annual compliance deadline tracking
- Smart penalty prevention system
- Multi-portal integration (GSE, Terna, DSO, ADM)

### 📊 Analytics & Reporting
- Real-time compliance scoring
- Portfolio-wide analytics dashboard
- Custom report generation
- Cost tracking and optimization
- Energy production/consumption analysis

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15 with PostGIS extension
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT with OAuth2
- **Caching:** Redis
- **Task Queue:** Celery
- **AI/ML:** LangChain + Google Gemini

**Frontend:**
- **Framework:** React 18 with TypeScript 5
- **Build Tool:** Vite
- **State Management:** React Query + Zustand
- **UI Components:** Tailwind CSS + shadcn/ui
- **Maps:** Leaflet + React Leaflet
- **Visual Designer:** React Flow
- **Forms:** React Hook Form + Zod

**Infrastructure (GCP):**
- **Compute:** Cloud Run / GKE
- **Database:** Cloud SQL (PostgreSQL + PostGIS)
- **Storage:** Cloud Storage
- **Caching:** Memorystore (Redis)
- **Monitoring:** Cloud Monitoring + Cloud Logging
- **CI/CD:** Cloud Build + GitHub Actions

### Architecture Principles

- **Multi-tenant:** Complete data isolation per tenant
- **API-First:** RESTful APIs with OpenAPI documentation
- **Event-Driven:** Async processing with Celery
- **Cloud-Native:** Designed for GCP deployment
- **Security-First:** JWT auth, RBAC, rate limiting

---

## 📦 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+** with PostGIS extension
- **Docker** (for local development)
- **Redis** (optional, for caching)

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/Bloom79/SentricS2.git
cd SentricS2

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL with PostGIS
./compose.sh up -d

# Run database migrations
alembic upgrade head

# Create test user
python scripts/create_test_user.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

**Default Credentials:**
- Email: `admin@kronos-eam.local`
- Password: `Demo2024!`

For detailed setup instructions, see [Local Development Guide](docs/setup/local-development.md).

---

## 📁 Project Structure

```
SentricS2/
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/      # API endpoints
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/              # Business logic
│   │   └── core/                  # Core utilities
│   ├── alembic/                   # Database migrations
│   ├── tests/                     # Test suite
│   └── requirements.txt
│
├── frontend/                       # React frontend
│   ├── src/
│   │   ├── pages/                 # Page components
│   │   ├── components/            # Reusable components
│   │   ├── services/              # API clients
│   │   ├── hooks/                 # Custom React hooks
│   │   └── utils/                 # Utility functions
│   └── package.json
│
├── deploy/                         # Deployment configurations
│   └── gcp/                       # GCP-specific configs
│
├── docs/                          # Documentation
│   ├── setup/                     # Setup guides
│   ├── architecture/              # Architecture docs
│   ├── features/                  # Feature documentation
│   ├── deployment/                # Deployment guides
│   └── api/                       # API documentation
│
└── README.md                      # This file
```

---

## 📚 Documentation

### Getting Started
- [Quick Start Guide](docs/setup/quick-start.md)
- [Local Development](docs/setup/local-development.md)
- [Testing Guide](docs/setup/testing.md)
- [Docker Setup](docs/setup/docker-testing.md)

### Architecture & Design
- [Backend Architecture](docs/architecture/backend-architecture.md)
- [Database Schema](docs/architecture/database-schema.md)
- [Modular Refactoring](docs/architecture/modular-refactoring.md)
- [Multi-Tenant Design](docs/architecture/multi-tenant-design.md)

### Features
- [Plant Management](docs/features/plant-management.md)
- [CER Management](docs/features/cer-management.md)
- [Visual Plant Designer](docs/features/visual-plant-designer.md)
- [Compliance System](docs/features/compliance-system.md)
- [Workflow Automation](docs/features/workflow-automation.md)

### API Documentation
- [API Endpoint Reference](docs/api/endpoint-reference.md)
- [Interactive Swagger UI](http://localhost:8000/docs)
- [ReDoc Documentation](http://localhost:8000/redoc)

### Deployment
- [GCP Deployment Guide](docs/deployment/gcp-deployment.md)
- [Production Checklist](docs/deployment/production-checklist.md)
- [Environment Configuration](docs/deployment/environment-config.md)

### Compliance & Regulations
- [Italian Compliance Overview](docs/ITALIAN_COMPLIANCE_DOCUMENTS.md)
- [Compliance Module Roadmap](docs/COMPLIANCE_MODULE_ROADMAP.md)

---

## 🚢 Deployment

### GCP Deployment

SentricS2 is designed for deployment on Google Cloud Platform with the following services:

- **Cloud Run** or **GKE** for application hosting
- **Cloud SQL** (PostgreSQL + PostGIS) for database
- **Cloud Storage** for document storage
- **Memorystore** (Redis) for caching
- **Cloud Build** for CI/CD

**Quick Deploy:**
```bash
cd deploy/gcp
./deploy.sh production
```

See [GCP Deployment Guide](docs/deployment/gcp-deployment.md) for detailed instructions.

---

## 🔒 Security

- **Authentication:** JWT tokens with refresh mechanism
- **Authorization:** Role-Based Access Control (RBAC)
- **Rate Limiting:** API endpoint protection
- **Security Headers:** OWASP recommended headers
- **Data Isolation:** Complete tenant separation
- **Encryption:** TLS for data in transit, encryption at rest

For security best practices, see [Security Guide](docs/deployment/security.md).

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm test

# Run all tests
npm run test:all
```

Target: **70%+ code coverage**

See [Testing Guide](docs/setup/testing.md) for comprehensive testing instructions.

---

## 🤝 Contributing

We welcome contributions! Please see:
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Development Workflow](docs/setup/development-workflow.md)

**Quick contribution steps:**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📊 Project Status

**Current Version:** 2.0.0
**Status:** Production Ready with Active Development
**Last Updated:** January 2025

### Recent Improvements (Week 12-15, January 2025)
- ✅ **Modular Architecture:** Split 4 large files into 18 focused modules
- ✅ **Type Safety:** Replaced all response_model=dict with Pydantic schemas
- ✅ **Code Quality:** 47% reduction in complexity, eliminated 200+ lines of duplication
- ✅ **BaseService Pattern:** Standardized service layer with reusable utilities
- ✅ **Documentation:** Comprehensive architecture, API, and database docs
- ✅ **Backward Compatible:** All refactoring maintains existing API contracts

### Roadmap
- 🚧 Comprehensive test suite (Target: 70%+ coverage)
- 🚧 CI/CD pipeline automation
- 🚧 Advanced monitoring and observability
- 📋 Mobile-responsive UI enhancements
- 📋 Advanced reporting features

See [CODE_ANALYSIS_AND_RECOMMENDATIONS.md](CODE_ANALYSIS_AND_RECOMMENDATIONS.md) for detailed improvement plan.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/Bloom79/SentricS2/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Bloom79/SentricS2/discussions)
- **Documentation:** [docs/](docs/)

---

## 🙏 Acknowledgments

Built with ❤️ for the Italian renewable energy sector, supporting the transition to sustainable energy production and Community Energy Resources (CER).

**Special thanks to:**
- Italian regulatory bodies (GSE, Terna, ADM) for their documentation
- Open source community for excellent tools and libraries
- All contributors who help improve this platform

---

<div align="center">
  <p><strong>SentricS2</strong> - Empowering the Renewable Energy Future</p>
  <p>© 2025 SentricS2. All rights reserved.</p>
</div>
