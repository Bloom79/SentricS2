# Database Schema - SentricS2

**Database:** PostgreSQL 15+ with PostGIS extension
**ORM:** SQLAlchemy 2.0
**Migrations:** Alembic

---

## Table of Contents

1. [Overview](#overview)
2. [Multi-Tenant Architecture](#multi-tenant-architecture)
3. [Core Entities](#core-entities)
4. [Entity Relationship Diagram](#entity-relationship-diagram)
5. [Table Schemas](#table-schemas)
6. [Indexes & Performance](#indexes--performance)
7. [Soft Delete Pattern](#soft-delete-pattern)
8. [Geographic Data (PostGIS)](#geographic-data-postgis)

---

## Overview

The SentricS2 database follows these design principles:

- **Multi-Tenant Isolation:** Every table includes `tenant_id` for data segregation
- **Soft Deletes:** Records are marked as deleted, not physically removed
- **Audit Fields:** Created/updated timestamps and user tracking on all entities
- **Type Safety:** PostgreSQL enums for status fields
- **Geographic Support:** PostGIS for location-based features (CER boundaries)
- **JSON Flexibility:** JSONB fields for dynamic/extended data

---

## Multi-Tenant Architecture

### Tenant Isolation

Every table (except `tenants` and `users`) includes:

```sql
tenant_id VARCHAR NOT NULL,
INDEX idx_{table}_tenant (tenant_id)
```

### Enforcement

Tenant isolation is enforced at:
1. **Application Layer:** All queries filtered by `tenant_id`
2. **Database Layer:** Indexes on tenant_id for performance
3. **Service Layer:** BaseService methods include tenant filtering

```python
# Every service query includes tenant filtering
query = query.filter(Model.tenant_id == tenant_id)
```

---

## Core Entities

### 1. Tenants & Users

```
tenants
  └── users (Many)
```

**Tenant:** Organization using the platform
**User:** Individual user within a tenant

### 2. Sites & Plants

```
sites
  └── plants (Many)
      ├── assets (Many)
      ├── workflows (Many)
      └── plant_layouts (Many)
```

**Site:** Physical location
**Plant:** Renewable energy installation at a site
**Asset:** Equipment within a plant (panels, inverters, etc.)

### 3. CER (Community Energy Resources)

```
cer
  ├── cer_members (Many)
  │   └── cer_member_assets (Many)
  ├── cer_plants (Many) - Links to plants
  ├── participation_requests (Many)
  └── energy_transactions (Many)
```

**CER:** Renewable Energy Community
**CER Member:** Individual or organization member
**CER Plant:** Plant contributing to the community

### 4. Workflows & Compliance

```
workflows
  └── workflow_phases (Many)
      ├── documents (Many)
      └── comments (in phase_data JSONB)

compliance_records
  └── documents (Many)
```

**Workflow:** Multi-phase regulatory process
**Workflow Phase:** Individual step in a workflow
**Compliance Record:** Regulatory requirement tracking

### 5. Financial

```
billing_accounts
  ├── billing_transactions (Many)
  ├── billing_statements (Many)
  └── billing_invoices (Many)
```

---

## Entity Relationship Diagram

```
┌─────────────┐
│   Tenants   │
└──────┬──────┘
       │
       ├──────────────┬───────────────┬───────────────┬──────────────┐
       │              │               │               │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│    Users    │ │   Sites    │ │    CER     │ │ Workflows  │ │ Billing  │
└─────────────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────────┘
                       │               │              │
                 ┌─────▼──────┐  ┌────▼──────┐ ┌─────▼──────┐
                 │   Plants   │  │ Members   │ │  Phases    │
                 └──────┬─────┘  └───────────┘ └────────────┘
                        │
                  ┌─────▼──────┐
                  │   Assets   │
                  └────────────┘
```

---

## Table Schemas

### tenants

**Purpose:** Organizations using the platform

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR | PRIMARY KEY | Unique tenant identifier (UUID) |
| name | VARCHAR(200) | NOT NULL | Organization name |
| subscription_tier | VARCHAR(50) | | Subscription level |
| is_active | BOOLEAN | DEFAULT true | Account status |
| created_at | TIMESTAMP | | Creation timestamp |
| updated_at | TIMESTAMP | | Last update timestamp |

**Indexes:**
- PRIMARY KEY (id)

---

### users

**Purpose:** User accounts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | User ID |
| tenant_id | VARCHAR | FK(tenants.id) | Associated tenant |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| hashed_password | VARCHAR | NOT NULL | Bcrypt hash |
| full_name | VARCHAR(200) | | Display name |
| role | VARCHAR(50) | DEFAULT 'user' | User role (admin, user) |
| is_active | BOOLEAN | DEFAULT true | Account status |
| created_at | TIMESTAMP | | Registration date |
| updated_at | TIMESTAMP | | Last update |

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE INDEX idx_users_email (email)
- INDEX idx_users_tenant (tenant_id)

**Relationships:**
- tenant → tenants (Many-to-One)

---

### sites

**Purpose:** Physical locations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Site ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| name | VARCHAR(200) | NOT NULL | Site name |
| address | TEXT | | Physical address |
| city | VARCHAR(100) | | City |
| province | VARCHAR(100) | | Province/State |
| postal_code | VARCHAR(20) | | ZIP/Postal code |
| country | VARCHAR(100) | DEFAULT 'Italy' | Country |
| coordinates | GEOMETRY(Point) | | Geographic location (PostGIS) |
| site_data | JSONB | | Additional metadata |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | Creator user |
| updated_by | INTEGER | FK(users.id) | Last updater |
| deleted_at | TIMESTAMP | | Soft delete timestamp |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_sites_tenant (tenant_id)
- SPATIAL INDEX idx_sites_coordinates (coordinates) using GIST
- INDEX idx_sites_deleted (deleted_at)

---

### plants

**Purpose:** Renewable energy installations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Plant ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| site_id | INTEGER | FK(sites.id) | Associated site |
| name | VARCHAR(200) | NOT NULL | Plant name |
| plant_type | VARCHAR(50) | NOT NULL | solar, wind, hydro, biomass |
| capacity_kw | NUMERIC(10,2) | | Installed capacity |
| status | VARCHAR(50) | | operational, maintenance, offline |
| installation_date | DATE | | Installation date |
| commissioning_date | DATE | | Start of operations |
| coordinates | GEOMETRY(Point) | | GPS location |
| technical_specs | JSONB | | Technical specifications |
| performance_data | JSONB | | Performance metrics |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | |
| updated_by | INTEGER | FK(users.id) | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_plants_tenant (tenant_id)
- INDEX idx_plants_site (site_id)
- INDEX idx_plants_type (plant_type)
- INDEX idx_plants_status (status)
- SPATIAL INDEX idx_plants_coordinates (coordinates) using GIST

**Relationships:**
- site → sites (Many-to-One)
- assets → assets (One-to-Many)
- workflows → workflows (One-to-Many)

---

### assets

**Purpose:** Physical equipment (panels, inverters, batteries, etc.)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Asset ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| plant_id | INTEGER | FK(plants.id) | Associated plant |
| asset_type | VARCHAR(50) | NOT NULL | panel, inverter, battery, etc. |
| name | VARCHAR(200) | NOT NULL | Asset name/identifier |
| serial_number | VARCHAR(100) | | Manufacturer serial |
| manufacturer | VARCHAR(100) | | Manufacturer name |
| model | VARCHAR(100) | | Model number |
| installation_date | DATE | | Install date |
| status | VARCHAR(50) | | operational, maintenance, failed |
| power_rating_w | NUMERIC(10,2) | | Power rating in watts |
| specifications | JSONB | | Technical specs |
| location_data | JSONB | | Physical location info |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | |
| updated_by | INTEGER | FK(users.id) | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_assets_tenant (tenant_id)
- INDEX idx_assets_plant (plant_id)
- INDEX idx_assets_type (asset_type)
- INDEX idx_assets_serial (serial_number)

**Relationships:**
- plant → plants (Many-to-One)
- string_configurations → plant_layouts (Many-to-Many via JSONB)

---

### cer (Renewable Energy Communities)

**Purpose:** Community Energy Resources

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | CER ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| name | VARCHAR(200) | NOT NULL | CER name |
| registration_number | VARCHAR(100) | UNIQUE | Official registration |
| status | VARCHAR(50) | | active, pending, inactive |
| legal_form | VARCHAR(100) | | association, cooperative, etc. |
| tax_code | VARCHAR(20) | | Italian tax code (C.F.) |
| vat_number | VARCHAR(20) | | VAT number if applicable |
| geographic_boundary | GEOMETRY(Polygon) | | Service area (PostGIS) |
| cer_data | JSONB | | Additional CER data |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | |
| updated_by | INTEGER | FK(users.id) | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_cer_tenant (tenant_id)
- INDEX idx_cer_registration (registration_number)
- SPATIAL INDEX idx_cer_boundary (geographic_boundary) using GIST

**Relationships:**
- members → cer_members (One-to-Many)
- plants → plants via cer_plants (Many-to-Many)
- transactions → energy_transactions (One-to-Many)

---

### cer_members

**Purpose:** CER community members

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Member ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| cer_id | INTEGER | FK(cer.id) | Associated CER |
| name | VARCHAR(200) | NOT NULL | Member name |
| type | VARCHAR(50) | | consumer, producer, prosumer |
| tax_code | VARCHAR(20) | | Italian tax code |
| pod_code | VARCHAR(50) | | POD (Point of Delivery) code |
| annual_consumption_kwh | NUMERIC(10,2) | | Estimated annual consumption |
| connection_point_address | TEXT | | Meter location |
| technical_info | JSONB | | Technical details |
| status | VARCHAR(50) | | active, pending, inactive |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | |
| updated_by | INTEGER | FK(users.id) | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_cer_members_tenant (tenant_id)
- INDEX idx_cer_members_cer (cer_id)
- INDEX idx_cer_members_pod (pod_code)

**Relationships:**
- cer → cer (Many-to-One)
- assets → cer_member_assets (One-to-Many)

---

### workflows

**Purpose:** Multi-phase regulatory processes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Workflow ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| plant_id | INTEGER | FK(plants.id) | Associated plant |
| template_id | INTEGER | FK(workflow_templates.id) | Source template |
| name | VARCHAR(200) | NOT NULL | Workflow name |
| workflow_type | ENUM | NOT NULL | authorization, compliance, etc. |
| status | ENUM | | draft, in_progress, completed |
| current_phase | VARCHAR(200) | | Current phase name |
| progress_percentage | INTEGER | DEFAULT 0 | Completion % |
| start_date | DATE | | Actual start |
| target_end_date | DATE | | Target completion |
| completed_date | DATE | | Actual completion |
| workflow_data | JSONB | | Additional data |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | |
| updated_by | INTEGER | FK(users.id) | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_workflows_tenant (tenant_id)
- INDEX idx_workflows_plant (plant_id)
- INDEX idx_workflows_status (status)
- INDEX idx_workflows_type (workflow_type)

**Enums:**
```sql
CREATE TYPE workflow_status AS ENUM ('draft', 'in_progress', 'completed', 'cancelled');
CREATE TYPE workflow_type AS ENUM ('authorization', 'compliance', 'installation', 'maintenance');
```

**Relationships:**
- plant → plants (Many-to-One)
- template → workflow_templates (Many-to-One)
- phases → workflow_phases (One-to-Many)

---

### workflow_phases

**Purpose:** Individual steps within workflows

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Phase ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| workflow_id | INTEGER | FK(workflows.id) | Parent workflow |
| name | VARCHAR(200) | NOT NULL | Phase name |
| description | TEXT | | Phase description |
| order | INTEGER | NOT NULL | Sequence order |
| status | VARCHAR(50) | | pending, in_progress, completed |
| due_date | DATE | | Expected completion |
| completed_date | DATE | | Actual completion |
| estimated_days | INTEGER | | Duration estimate |
| required_documents | JSONB | | Required document types |
| official_form_fields | JSONB | | Form field definitions |
| portal_url | VARCHAR(500) | | External portal URL |
| portal_login_url | VARCHAR(500) | | Portal login URL |
| submission_method | VARCHAR(100) | | online, paper, email |
| regulatory_deadline | DATE | | Legal deadline |
| deadline_type | VARCHAR(50) | | hard, soft |
| cost_amount | NUMERIC(10,2) | | Associated costs |
| cost_description | TEXT | | Cost breakdown |
| payment_method | VARCHAR(100) | | Payment method |
| requires_human_auth | BOOLEAN | DEFAULT false | Manual authorization needed |
| requires_site_inspection | BOOLEAN | DEFAULT false | Inspection required |
| checklist_items | JSONB | | Checklist |
| instructions | TEXT | | Instructions |
| phase_data | JSONB | | Dynamic data (documents, comments) |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | |
| updated_by | INTEGER | FK(users.id) | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_workflow_phases_tenant (tenant_id)
- INDEX idx_workflow_phases_workflow (workflow_id)
- INDEX idx_workflow_phases_status (status)
- INDEX idx_workflow_phases_order (workflow_id, order)

**JSONB Fields:**

`phase_data` structure:
```json
{
  "documents": [
    {"document_id": 123, "name": "form.pdf", "uploaded_at": "..."}
  ],
  "comments": [
    {"id": 1, "text": "Comment", "author": "user@example.com", "timestamp": "..."}
  ],
  "assigned_to": 5,
  "form_data": {...}
}
```

**Relationships:**
- workflow → workflows (Many-to-One)
- documents → documents (One-to-Many via phase_data JSONB)

---

### documents

**Purpose:** Centralized document storage

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Document ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| name | VARCHAR(500) | NOT NULL | File name |
| document_type | VARCHAR(100) | NOT NULL | Document category |
| file_type | VARCHAR(50) | | MIME type |
| file_size | BIGINT | | Size in bytes |
| file_path | VARCHAR(1000) | | Storage path/URL |
| description | TEXT | | Document description |
| plant_id | INTEGER | FK(plants.id) | Associated plant |
| compliance_record_id | INTEGER | FK(compliance_records.id) | Associated compliance |
| document_data | JSONB | | Additional metadata |
| created_at | TIMESTAMP | | Upload timestamp |
| updated_at | TIMESTAMP | | Last update |
| created_by | INTEGER | FK(users.id) | Uploader |
| updated_by | INTEGER | FK(users.id) | Last editor |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_documents_tenant (tenant_id)
- INDEX idx_documents_plant (plant_id)
- INDEX idx_documents_type (document_type)

---

### compliance_records

**Purpose:** Regulatory compliance tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Record ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| plant_id | INTEGER | FK(plants.id) | Associated plant |
| cer_id | INTEGER | FK(cer.id) | Associated CER |
| requirement_type | VARCHAR(100) | NOT NULL | Type of requirement |
| authority | VARCHAR(100) | | Regulatory authority (GSE, Terna) |
| status | VARCHAR(50) | | pending, submitted, approved |
| deadline | DATE | | Compliance deadline |
| submission_date | DATE | | Date submitted |
| approval_date | DATE | | Date approved |
| compliance_data | JSONB | | Additional data |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | |
| updated_by | INTEGER | FK(users.id) | |
| deleted_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_compliance_tenant (tenant_id)
- INDEX idx_compliance_plant (plant_id)
- INDEX idx_compliance_cer (cer_id)
- INDEX idx_compliance_status (status)
- INDEX idx_compliance_deadline (deadline)

---

### billing_accounts

**Purpose:** CER member billing accounts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Account ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| cer_id | INTEGER | FK(cer.id) | Associated CER |
| member_id | INTEGER | FK(cer_members.id) | Associated member |
| account_number | VARCHAR(50) | UNIQUE | Unique account number |
| balance | NUMERIC(10,2) | DEFAULT 0 | Current balance |
| status | VARCHAR(50) | | active, suspended, closed |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |
| deleted_at | TIMESTAMP | | |

---

### billing_transactions

**Purpose:** Financial transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Transaction ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| account_id | INTEGER | FK(billing_accounts.id) | Associated account |
| transaction_type | VARCHAR(50) | | credit, debit, incentive |
| amount | NUMERIC(10,2) | NOT NULL | Transaction amount |
| description | TEXT | | Transaction details |
| reference_number | VARCHAR(100) | | External reference |
| transaction_date | DATE | NOT NULL | Transaction date |
| status | VARCHAR(50) | | pending, completed, failed |
| transaction_data | JSONB | | Additional metadata |
| created_at | TIMESTAMP | | |
| created_by | INTEGER | FK(users.id) | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_billing_transactions_tenant (tenant_id)
- INDEX idx_billing_transactions_account (account_id)
- INDEX idx_billing_transactions_date (transaction_date)

---

### energy_transactions

**Purpose:** Energy production/consumption records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Transaction ID |
| tenant_id | VARCHAR | NOT NULL | Tenant isolation |
| cer_id | INTEGER | FK(cer.id) | Associated CER |
| transaction_date | TIMESTAMP | NOT NULL | Transaction timestamp |
| production_kwh | NUMERIC(10,3) | | Energy produced |
| consumption_kwh | NUMERIC(10,3) | | Energy consumed |
| shared_energy_kwh | NUMERIC(10,3) | | Shared within CER |
| grid_export_kwh | NUMERIC(10,3) | | Exported to grid |
| grid_import_kwh | NUMERIC(10,3) | | Imported from grid |
| hourly_data | JSONB | | Hourly breakdown |
| created_at | TIMESTAMP | | |

**Indexes:**
- PRIMARY KEY (id)
- INDEX idx_energy_transactions_tenant (tenant_id)
- INDEX idx_energy_transactions_cer (cer_id)
- INDEX idx_energy_transactions_date (transaction_date)

---

## Indexes & Performance

### Primary Indexes

Every table has:
- **Primary Key:** Automatic B-tree index
- **Tenant ID:** Index for multi-tenant filtering
- **Deleted At:** Index for soft delete filtering

### Foreign Key Indexes

All foreign keys are automatically indexed for join performance.

### Composite Indexes

```sql
-- Workflow phases ordered by workflow and sequence
CREATE INDEX idx_workflow_phases_order ON workflow_phases (workflow_id, order);

-- Recent documents by plant
CREATE INDEX idx_documents_plant_date ON documents (plant_id, created_at DESC);

-- Active compliance by deadline
CREATE INDEX idx_compliance_active ON compliance_records (tenant_id, status, deadline)
  WHERE deleted_at IS NULL;
```

### Spatial Indexes (PostGIS)

```sql
-- Geographic queries for sites and plants
CREATE INDEX idx_sites_coordinates ON sites USING GIST (coordinates);
CREATE INDEX idx_plants_coordinates ON plants USING GIST (coordinates);

-- CER geographic boundaries
CREATE INDEX idx_cer_boundary ON cer USING GIST (geographic_boundary);
```

---

## Soft Delete Pattern

### Implementation

All entities use soft delete:
```sql
deleted_at TIMESTAMP DEFAULT NULL
```

### Querying

Active records only:
```sql
SELECT * FROM plants
WHERE tenant_id = 'tenant_abc'
  AND deleted_at IS NULL;
```

### Service Layer

```python
class BaseService:
    @staticmethod
    def _apply_deleted_filter(query, model):
        """Apply soft delete filter"""
        return query.filter(model.deleted_at.is_(None))
```

### Benefits

- **Data Recovery:** Restore deleted records
- **Audit Trail:** Maintain historical data
- **Referential Integrity:** Preserve relationships
- **Compliance:** Meet data retention requirements

---

## Geographic Data (PostGIS)

### PostGIS Extension

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

### Geographic Columns

**Point Data (sites, plants):**
```sql
coordinates GEOMETRY(Point, 4326)
```

**Polygon Data (CER boundaries):**
```sql
geographic_boundary GEOMETRY(Polygon, 4326)
```

### Spatial Queries

**Find plants within CER boundary:**
```sql
SELECT p.*
FROM plants p
JOIN cer c ON ST_Within(p.coordinates, c.geographic_boundary)
WHERE c.id = 5;
```

**Find nearest plants to a point:**
```sql
SELECT *
FROM plants
WHERE tenant_id = 'tenant_abc'
ORDER BY ST_Distance(coordinates, ST_MakePoint(9.1900, 45.4642))
LIMIT 10;
```

---

## Migrations

### Alembic Migrations

Located in `/backend/alembic/versions/`

**Create Migration:**
```bash
alembic revision --autogenerate -m "Add new field to plants"
```

**Apply Migrations:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```

### Migration Best Practices

1. **Always review auto-generated migrations**
2. **Test migrations on development database first**
3. **Include both upgrade and downgrade logic**
4. **Use transactions for data migrations**
5. **Backup production database before applying**

---

## Related Documentation

- [Backend Architecture](./backend-architecture.md)
- [Multi-Tenant Design](./multi-tenant-design.md)
- [API Endpoints](../api/endpoint-reference.md)

---

**Last Updated:** January 2025
**Database Version:** PostgreSQL 15.x + PostGIS 3.x
**Schema Version:** See latest Alembic migration
