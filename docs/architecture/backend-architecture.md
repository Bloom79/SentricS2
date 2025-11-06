# Backend Architecture - SentricS2

**Last Updated:** January 2025
**Version:** 2.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Layer Architecture](#layer-architecture)
6. [Modular Design](#modular-design)
7. [Database Architecture](#database-architecture)
8. [API Design](#api-design)
9. [Security](#security)
10. [Recent Improvements](#recent-improvements)

---

## Overview

SentricS2's backend is built with **FastAPI**, a modern Python web framework known for high performance and automatic API documentation. The architecture follows clean code principles with clear separation of concerns across multiple layers.

### Key Characteristics

- **API-First Design:** RESTful APIs with automatic OpenAPI documentation
- **Multi-Tenant:** Complete data isolation per tenant with row-level security
- **Type-Safe:** Pydantic schemas for request/response validation
- **Modular:** Domain-driven design with focused modules
- **Cloud-Native:** Designed for containerized deployment on GCP
- **Async-Ready:** Support for asynchronous operations where needed

---

## Architecture Principles

### 1. **Separation of Concerns**
Each layer has a distinct responsibility:
- **Models:** Database schema and ORM definitions
- **Schemas:** Request/response validation and serialization
- **Services:** Business logic and domain operations
- **Endpoints:** HTTP request handling and routing
- **Core:** Shared utilities, security, and configuration

### 2. **Multi-Tenant Isolation**
Every database query includes tenant filtering to ensure complete data isolation:
```python
# All services inherit from BaseService
class MyService(BaseService):
    @staticmethod
    def get_by_id(db, id, tenant_id):
        return BaseService._get_by_id(db, Model, id, tenant_id)
```

### 3. **Type Safety**
Pydantic schemas provide runtime type validation:
```python
# Request schema
class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    plant_id: int

# Response schema
class WorkflowResponse(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        from_attributes = True  # Enable ORM mode
```

### 4. **DRY Principle**
Shared functionality is extracted into reusable components:
- BaseService class for common database operations
- Shared Pydantic schemas for consistent responses
- Helper functions for complex operations

---

## Technology Stack

### Core Framework
- **FastAPI 0.104+:** Modern async web framework
- **Python 3.11+:** Latest Python features and performance
- **Uvicorn:** ASGI server for production deployment

### Database
- **SQLAlchemy 2.0:** Modern ORM with async support
- **Alembic:** Database migration management
- **PostgreSQL 15+:** Primary database with ACID compliance
- **PostGIS:** Geographic data support for CER boundaries
- **psycopg2:** PostgreSQL adapter

### Validation & Serialization
- **Pydantic 2.0+:** Data validation and serialization
- **Python-Jose:** JWT token handling
- **Passlib:** Password hashing (bcrypt)

### AI/ML
- **LangChain:** AI agent framework
- **Google Gemini:** LLM integration for compliance assistance

### Utilities
- **Python-Multipart:** File upload handling
- **Pandas:** Data processing and CSV import
- **Openpyxl:** Excel file handling
- **python-dateutil:** Date parsing and manipulation

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                      # Application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── api.py               # API router aggregation
│   │       └── endpoints/           # API endpoints (modular)
│   │           ├── auth.py          # Authentication
│   │           ├── users.py         # User management
│   │           ├── plants.py        # Plant management
│   │           ├── cer/             # 🆕 Modular CER endpoints
│   │           │   ├── __init__.py  # Router aggregator
│   │           │   ├── crud.py      # CER CRUD operations
│   │           │   └── members.py   # Member management
│   │           ├── workflows/       # 🆕 Modular workflow endpoints
│   │           │   ├── __init__.py
│   │           │   ├── crud.py      # Workflow CRUD
│   │           │   └── templates.py # Template management
│   │           ├── workflow_phases/ # 🆕 Modular phase endpoints
│   │           │   ├── __init__.py
│   │           │   ├── details.py   # Phase details
│   │           │   ├── updates.py   # Status/assignment
│   │           │   └── attachments.py # Documents/comments
│   │           ├── assets/          # 🆕 Modular asset endpoints
│   │           │   ├── __init__.py
│   │           │   ├── types.py     # Asset types
│   │           │   ├── crud.py      # Asset CRUD
│   │           │   ├── strings.py   # String config
│   │           │   └── bulk.py      # Bulk import
│   │           ├── compliance.py    # Compliance tracking
│   │           ├── documents.py     # Document management
│   │           └── dev.py           # Development/testing
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── plant.py
│   │   ├── cer.py
│   │   ├── workflow.py
│   │   ├── compliance.py
│   │   └── document.py
│   │
│   ├── schemas/                     # Pydantic schemas
│   │   ├── user.py
│   │   ├── plant.py
│   │   ├── cer.py
│   │   ├── workflow.py              # 🆕 Enhanced with 13 new schemas
│   │   ├── compliance.py
│   │   └── document.py
│   │
│   ├── services/                    # Business logic layer
│   │   ├── base.py                  # 🆕 BaseService with 9 utilities
│   │   ├── user_service.py
│   │   ├── plant_service.py
│   │   ├── cer_service.py
│   │   ├── workflow_service.py
│   │   ├── workflow_template_service.py
│   │   ├── compliance_service.py
│   │   ├── document_service.py
│   │   ├── billing_service.py
│   │   ├── energy_service.py
│   │   ├── bulk_import_service.py
│   │   └── string_config_service.py
│   │
│   └── core/                        # Core utilities
│       ├── config.py                # Configuration management
│       ├── security.py              # JWT auth, password hashing
│       ├── database.py              # Database connection
│       ├── geography.py             # PostGIS utilities
│       └── exceptions.py            # Custom exceptions
│
├── alembic/                         # Database migrations
│   ├── versions/                    # Migration files
│   └── env.py                       # Alembic configuration
│
├── tests/                           # Test suite
│   ├── conftest.py                  # Test fixtures
│   ├── test_auth.py
│   ├── test_plants.py
│   └── ...
│
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
└── alembic.ini                      # Alembic config
```

---

## Layer Architecture

### 1. **API Layer (Endpoints)**

**Purpose:** Handle HTTP requests, validate input, return responses

**Responsibilities:**
- Route definition and HTTP method handling
- Request validation via Pydantic schemas
- Call appropriate service methods
- Return standardized responses
- Handle HTTP-specific concerns (status codes, headers)

**Example:**
```python
@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_workflow(
    workflow_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get detailed workflow information"""
    workflow = workflow_service.get_workflow(db, workflow_id, current_user.tenant_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowDetailResponse.from_orm(workflow)
```

### 2. **Service Layer**

**Purpose:** Implement business logic and domain operations

**Responsibilities:**
- Business rule enforcement
- Complex data transformations
- Cross-entity operations
- Integration with external systems
- Transaction management

**Example:**
```python
class WorkflowService(BaseService):
    @staticmethod
    def create_workflow(db: Session, workflow_data: WorkflowCreate, tenant_id: str, user_id: int):
        # Validate plant exists
        plant = BaseService._get_by_id(db, Plant, workflow_data.plant_id, tenant_id)
        if not plant:
            raise ValueError("Plant not found")

        # Create workflow
        workflow = Workflow(
            **workflow_data.dict(),
            tenant_id=tenant_id,
            created_by=user_id
        )
        db.add(workflow)
        db.commit()
        return workflow
```

### 3. **Model Layer (ORM)**

**Purpose:** Define database schema and relationships

**Responsibilities:**
- Table structure definition
- Relationships between entities
- Database constraints
- Soft delete support

**Example:**
```python
class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"))

    # Relationships
    plant = relationship("Plant", back_populates="workflows")
    phases = relationship("WorkflowPhase", back_populates="workflow")

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
```

### 4. **Schema Layer (Pydantic)**

**Purpose:** Validate and serialize data

**Responsibilities:**
- Request validation
- Response serialization
- Type checking
- Default values
- Field constraints

**Example:**
```python
class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    plant_id: int
    template_id: Optional[int] = None

class WorkflowResponse(BaseModel):
    id: int
    name: str
    status: str
    progress_percentage: int

    class Config:
        from_attributes = True  # Enable from_orm()
```

---

## Modular Design

### Recent Modularization (Week 12-15)

Following clean code principles, large monolithic files have been split into focused modules:

#### 1. **CER Module** (was 1,141 lines, now 6 focused modules)

```
cer/
├── __init__.py          # Router aggregation
├── crud.py              # CER CRUD operations (110 lines, 5 endpoints)
└── members.py           # Member management (167 lines, 6 endpoints)
# Additional modules: participation.py, compliance.py, documents.py, plants.py
```

**Benefits:**
- Easier navigation and maintenance
- Reduced merge conflicts
- Clear separation of concerns
- Better parallel development

#### 2. **Workflows Module** (was 561 lines, now 3 modules)

```
workflows/
├── __init__.py          # Router aggregation
├── crud.py              # Workflow CRUD (5 endpoints, 257 lines)
└── templates.py         # Template management (6 endpoints, 258 lines)
```

**Key Improvement:** Eliminated 100+ lines of manual dict construction by using Pydantic schemas

#### 3. **Workflow Phases Module** (was 481 lines, now 3 modules)

```
workflow_phases/
├── __init__.py
├── details.py           # Phase details (1 endpoint, 152 lines)
├── updates.py           # Status/assignment (2 endpoints, 198 lines)
└── attachments.py       # Documents/comments (2 endpoints, 174 lines)
```

#### 4. **Assets Module** (was 411 lines, now 5 modules)

```
assets/
├── __init__.py
├── types.py             # Asset type management (2 endpoints)
├── crud.py              # Asset CRUD (5 endpoints)
├── strings.py           # String configuration (6 endpoints)
└── bulk.py              # Bulk import (2 endpoints)
```

### BaseService Pattern

All services now inherit from `BaseService` which provides 9 common utilities:

```python
class BaseService:
    """Base class with common database operations"""

    # Filtering
    @staticmethod
    def _apply_tenant_filter(query, model, tenant_id)
    @staticmethod
    def _apply_deleted_filter(query, model)

    # CRUD
    @staticmethod
    def _get_by_id(db, model, id, tenant_id)
    @staticmethod
    def _get_all(db, model, tenant_id)
    @staticmethod
    def _soft_delete(db, instance, user_id)

    # Utilities
    @staticmethod
    def _paginate(query, skip, limit)
    @staticmethod
    def _count(db, model, tenant_id)
    @staticmethod
    def _exists(db, model, id, tenant_id)
    @staticmethod
    def _bulk_update(db, instances)
```

---

## Database Architecture

### Multi-Tenant Design

Every table includes a `tenant_id` column for data isolation:

```sql
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,  -- Multi-tenant isolation
    name VARCHAR(200) NOT NULL,
    ...
    deleted_at TIMESTAMP,        -- Soft delete

    INDEX idx_workflows_tenant (tenant_id)
);
```

### Soft Delete Pattern

All entities support soft deletion for data recovery and audit:

```python
# Soft delete
workflow.deleted_at = datetime.utcnow()
workflow.updated_by = user_id

# Query excludes soft-deleted
query.filter(Model.deleted_at.is_(None))
```

### Key Relationships

```
Tenant
  ├── Users
  ├── Plants
  │   ├── Assets (panels, inverters, batteries)
  │   ├── StringConfigurations
  │   └── Workflows
  ├── CERs (Renewable Energy Communities)
  │   ├── CERMembers
  │   ├── CERPlants
  │   └── ParticipationRequests
  ├── Workflows
  │   └── WorkflowPhases
  │       ├── Documents
  │       └── Comments (in phase_data JSON)
  └── ComplianceRecords
      └── Documents
```

See [Database Schema](./database-schema.md) for detailed schema documentation.

---

## API Design

### RESTful Conventions

- `GET /api/v1/workflows` - List workflows
- `GET /api/v1/workflows/{id}` - Get workflow detail
- `POST /api/v1/workflows` - Create workflow
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow (soft delete)

### Response Format

**Success Response:**
```json
{
  "id": 1,
  "name": "Solar Panel Installation",
  "status": "in_progress",
  "progress_percentage": 60,
  "phases": [...]
}
```

**Error Response:**
```json
{
  "detail": "Workflow not found"
}
```

### Pagination

```
GET /api/v1/workflows?skip=0&limit=20
```

### Filtering

```
GET /api/v1/workflows?status=in_progress&plant_id=5
```

### Auto-Generated Documentation

FastAPI automatically generates:
- **OpenAPI Schema:** `/openapi.json`
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

---

## Security

### Authentication

**JWT Token-Based Authentication:**

```python
from app.core.security import get_current_active_user

@router.get("/protected")
async def protected_route(
    current_user: TokenData = Depends(get_current_active_user)
):
    return {"user": current_user.email}
```

### Authorization

**Role-Based Access Control (RBAC):**

```python
def get_current_admin_user(
    current_user: TokenData = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

### Tenant Isolation

**Automatic tenant filtering in all queries:**

```python
# Every service call includes tenant_id
workflow = workflow_service.get_workflow(db, workflow_id, current_user.tenant_id)
```

### Password Security

- **Bcrypt hashing** with salt
- **Minimum password requirements** enforced
- **No plaintext storage**

---

## Recent Improvements

### Week 13: Pydantic Schema Migration (January 2025)

**Problem:** 15 endpoints used `response_model=dict` with manual dict construction (200+ lines of code duplication)

**Solution:** Created 13 new Pydantic schemas and migrated all endpoints

**Results:**
- ✅ Eliminated 200+ lines of manual dict construction
- ✅ Full type safety across all workflow endpoints
- ✅ Automatic OpenAPI documentation
- ✅ Better IDE autocomplete and type checking
- ✅ Runtime validation of all responses

**Example Before:**
```python
@router.get("/{id}", response_model=dict)
async def get_workflow(...):
    # 100+ lines of manual dict construction
    return {
        "id": workflow.id,
        "name": workflow.name,
        # ... 100 more lines
    }
```

**Example After:**
```python
@router.get("/{id}", response_model=WorkflowDetailResponse)
async def get_workflow(...):
    # Pydantic handles everything
    return WorkflowDetailResponse.from_orm(workflow)
```

### Week 12-13: Service Layer Refactoring

**Problem:** 8 complex service functions with cyclomatic complexity > 15

**Solution:** Extracted 41 helper methods, created BaseService class

**Results:**
- ✅ 62% average complexity reduction
- ✅ 47% overall C901 warning reduction
- ✅ 41 new testable units
- ✅ Improved code maintainability

### Week 12-13: File Modularization

**Problem:** Large monolithic files (cer.py: 1,141 lines, workflows.py: 561 lines)

**Solution:** Split into focused modules by domain responsibility

**Results:**
- ✅ Better code organization
- ✅ Easier navigation and maintenance
- ✅ Reduced merge conflicts
- ✅ Enabled parallel development
- ✅ Backward compatible via `__init__.py` aggregation

---

## Best Practices

### 1. **Always Use Pydantic Schemas**
```python
# ✅ Good - Type safe
@router.post("/", response_model=WorkflowResponse)
async def create(data: WorkflowCreate):
    return WorkflowResponse.from_orm(workflow)

# ❌ Bad - No validation
@router.post("/", response_model=dict)
async def create(data: dict):
    return {"id": workflow.id}
```

### 2. **Leverage BaseService**
```python
# ✅ Good - Reuse common logic
class MyService(BaseService):
    @staticmethod
    def get(db, id, tenant_id):
        return BaseService._get_by_id(db, Model, id, tenant_id)

# ❌ Bad - Duplicate query logic
class MyService:
    @staticmethod
    def get(db, id, tenant_id):
        return db.query(Model).filter(...).first()
```

### 3. **Keep Endpoints Thin**
```python
# ✅ Good - Endpoint orchestrates, service implements
@router.post("/")
async def create(data: Create):
    return service.create(db, data, tenant_id)

# ❌ Bad - Business logic in endpoint
@router.post("/")
async def create(data: dict):
    # 50 lines of business logic
```

### 4. **Use Dependency Injection**
```python
# ✅ Good - Dependencies injected
async def endpoint(
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    pass
```

---

## Performance Considerations

### Database Queries

- **Use eager loading** for relationships: `.options(joinedload(Model.relationship))`
- **Add database indexes** on frequently queried fields (tenant_id, created_at)
- **Use pagination** for large result sets
- **Avoid N+1 queries** with proper eager loading

### Caching

- **Redis caching** for frequently accessed data
- **Response caching** for expensive computations
- **Connection pooling** for database connections

### Async Operations

- **Use async/await** for I/O-bound operations
- **Background tasks** for long-running operations (Celery)
- **Batch processing** for bulk operations

---

## Related Documentation

- [Database Schema](./database-schema.md)
- [API Endpoint Reference](../api/endpoint-reference.md)
- [Multi-Tenant Design](./multi-tenant-design.md)
- [Security Guide](./security.md)
- [Deployment Guide](../deployment/gcp-deployment.md)

---

**Last Updated:** January 2025
**Version:** 2.0.0
**Maintained By:** SentricS2 Development Team
