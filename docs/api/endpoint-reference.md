# API Endpoint Reference - SentricS2

**Base URL:** `http://localhost:8000/api/v1` (development)
**Production URL:** `https://your-domain.com/api/v1`

**API Documentation:** `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Sites](#sites)
3. [Plants](#plants)
4. [CER (Renewable Energy Communities)](#cer-renewable-energy-communities)
5. [Energy Management](#energy-management)
6. [Billing & Financial](#billing--financial)
7. [Assets](#assets)
8. [Workflows](#workflows)
9. [Workflow Phases](#workflow-phases)
10. [Documents](#documents)
11. [Compliance](#compliance)
12. [Dashboard](#dashboard)
13. [Common Patterns](#common-patterns)

---

## Authentication

**Base Path:** `/api/v1/auth`

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "organization_name": "My Company"
}
```

### Get Current User

```http
GET /auth/me
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "tenant_id": "tenant_abc123",
  "role": "admin",
  "is_active": true
}
```

### Refresh Token

```http
POST /auth/refresh
Authorization: Bearer {refresh_token}
```

---

## Sites

**Base Path:** `/api/v1/sites`

Sites represent physical locations that can contain multiple plants.

### List Sites

```http
GET /sites?skip=0&limit=20
Authorization: Bearer {token}
```

### Create Site

```http
POST /sites
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Solar Farm North",
  "address": "Via Roma 123, Milano",
  "coordinates": {
    "latitude": 45.4642,
    "longitude": 9.1900
  }
}
```

### Get Site

```http
GET /sites/{site_id}
Authorization: Bearer {token}
```

### Update Site

```http
PUT /sites/{site_id}
Authorization: Bearer {token}
```

### Delete Site

```http
DELETE /sites/{site_id}
Authorization: Bearer {token}
```

---

## Plants

**Base Path:** `/api/v1/plants`

Plants represent renewable energy installations (solar, wind, etc.).

### List Plants

```http
GET /plants?skip=0&limit=20&site_id=5&type=solar
Authorization: Bearer {token}
```

**Query Parameters:**
- `skip` (int): Pagination offset
- `limit` (int): Items per page (max 100)
- `site_id` (int): Filter by site
- `type` (string): Filter by plant type (solar, wind, hydro, biomass)
- `status` (string): Filter by status

### Create Plant

```http
POST /plants
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Solar Plant Alpha",
  "plant_type": "solar",
  "site_id": 5,
  "capacity_kw": 500.0,
  "status": "operational",
  "installation_date": "2024-01-15",
  "coordinates": {
    "latitude": 45.4642,
    "longitude": 9.1900
  }
}
```

### Get Plant

```http
GET /plants/{plant_id}
Authorization: Bearer {token}
```

**Response includes:**
- Plant details
- Associated assets
- Energy production stats
- Compliance status

### Update Plant

```http
PUT /plants/{plant_id}
Authorization: Bearer {token}
```

### Delete Plant

```http
DELETE /plants/{plant_id}
Authorization: Bearer {token}
```

**Note:** Soft delete - plant is marked as deleted but data retained

### Get Plant Performance

```http
GET /plants/{plant_id}/performance?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

---

## CER (Renewable Energy Communities)

**Base Path:** `/api/v1/cer`

Manage Renewable Energy Communities (Comunità Energetiche Rinnovabili).

### CER CRUD Operations

#### List CERs

```http
GET /cer?skip=0&limit=20&status=active
Authorization: Bearer {token}
```

#### Create CER

```http
POST /cer
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "CER Milano Nord",
  "registration_number": "CER-2024-001",
  "status": "active",
  "legal_form": "association",
  "tax_code": "12345678901",
  "geographic_boundary": {
    "type": "Polygon",
    "coordinates": [[...]]
  }
}
```

#### Get CER Details

```http
GET /cer/{cer_id}
Authorization: Bearer {token}
```

**Response includes:**
- CER details
- Member count
- Linked plants
- Energy sharing statistics
- Compliance status

#### Update CER

```http
PUT /cer/{cer_id}
Authorization: Bearer {token}
```

#### Delete CER

```http
DELETE /cer/{cer_id}
Authorization: Bearer {token}
```

### Member Management

#### List Members

```http
GET /cer/{cer_id}/members?skip=0&limit=20&type=consumer
Authorization: Bearer {token}
```

**Query Parameters:**
- `type`: Filter by member type (consumer, producer, prosumer)
- `status`: Filter by status (active, pending, inactive)

#### Add Member

```http
POST /cer/{cer_id}/members
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Mario Rossi",
  "type": "consumer",
  "tax_code": "RSSMRA80A01F205X",
  "pod_code": "IT001E12345678",
  "annual_consumption_kwh": 3000.0,
  "connection_point_address": "Via Roma 10, Milano"
}
```

#### Get Member Details

```http
GET /cer/{cer_id}/members/{member_id}
Authorization: Bearer {token}
```

#### Update Member

```http
PUT /cer/{cer_id}/members/{member_id}
Authorization: Bearer {token}
```

#### Delete Member

```http
DELETE /cer/{cer_id}/members/{member_id}
Authorization: Bearer {token}
```

#### Get Member Statistics

```http
GET /cer/{cer_id}/members/{member_id}/stats?year=2024&month=1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "member_id": 10,
  "period": "2024-01",
  "consumption_kwh": 250.5,
  "shared_energy_kwh": 180.2,
  "self_consumed_kwh": 70.3,
  "grid_purchased_kwh": 70.3,
  "savings_euro": 54.06,
  "incentive_earned_euro": 18.02
}
```

### Plant Linking

#### Link Plant to CER

```http
POST /cer/{cer_id}/plants/{plant_id}
Authorization: Bearer {token}
```

#### Unlink Plant from CER

```http
DELETE /cer/{cer_id}/plants/{plant_id}
Authorization: Bearer {token}
```

#### List CER Plants

```http
GET /cer/{cer_id}/plants
Authorization: Bearer {token}
```

### Compliance & Documents

#### Get CER Compliance Status

```http
GET /cer/{cer_id}/compliance
Authorization: Bearer {token}
```

#### Get Required Documents

```http
GET /cer/{cer_id}/documents/required
Authorization: Bearer {token}
```

---

## Energy Management

**Base Path:** `/api/v1/energy`

Manage energy production, consumption, and sharing for CER.

### Calculate Shared Energy

```http
POST /energy/calculate-sharing
Authorization: Bearer {token}
Content-Type: application/json

{
  "cer_id": 5,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Response:**
```json
{
  "cer_id": 5,
  "period": "2024-01",
  "total_production_kwh": 15000.0,
  "total_consumption_kwh": 12000.0,
  "shared_energy_kwh": 10000.0,
  "grid_export_kwh": 5000.0,
  "grid_import_kwh": 7000.0,
  "members": [
    {
      "member_id": 10,
      "allocated_shared_kwh": 2000.0,
      "incentive_euro": 200.0
    }
  ]
}
```

### Record Energy Transaction

```http
POST /energy/transactions
Authorization: Bearer {token}
Content-Type: application/json

{
  "cer_id": 5,
  "transaction_date": "2024-01-15T14:30:00Z",
  "production_kwh": 500.0,
  "consumption_kwh": 420.0,
  "hourly_data": {...}
}
```

### Get Energy Transactions

```http
GET /energy/transactions?cer_id=5&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

---

## Billing & Financial

**Base Path:** `/api/v1/billing`

Manage CER billing, invoices, and financial transactions.

### Create Billing Transaction

```http
POST /billing/transactions
Authorization: Bearer {token}
Content-Type: application/json

{
  "cer_id": 5,
  "member_id": 10,
  "transaction_type": "incentive",
  "amount": 54.06,
  "description": "January 2024 energy sharing incentive",
  "transaction_date": "2024-02-01"
}
```

### List Transactions

```http
GET /billing/transactions?cer_id=5&member_id=10&start_date=2024-01-01
Authorization: Bearer {token}
```

### Get Member Balance

```http
GET /billing/balance/{member_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "member_id": 10,
  "current_balance": 324.36,
  "total_credits": 500.00,
  "total_debits": 175.64,
  "last_transaction_date": "2024-01-31T23:59:59Z"
}
```

### Generate Invoice

```http
POST /billing/invoices
Authorization: Bearer {token}
Content-Type: application/json

{
  "cer_id": 5,
  "member_id": 10,
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "invoice_type": "incentive_payment"
}
```

---

## Assets

**Base Path:** `/api/v1/assets`

Manage physical assets (panels, inverters, batteries, etc.).

### Asset Types

#### List Asset Types

```http
GET /assets/types
Authorization: Bearer {token}
```

#### Create Asset Type

```http
POST /assets/types
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Solar Panel",
  "category": "generation",
  "manufacturer": "SunPower",
  "model": "Maxeon 3",
  "specifications": {
    "power_rating_w": 400,
    "efficiency": 22.6,
    "warranty_years": 25
  }
}
```

### Asset CRUD

#### List Assets

```http
GET /assets?plant_id=5&category=generation&skip=0&limit=20
Authorization: Bearer {token}
```

#### Create Asset

```http
POST /assets
Authorization: Bearer {token}
Content-Type: application/json

{
  "plant_id": 5,
  "asset_type_id": 3,
  "name": "Panel A1",
  "serial_number": "SP-2024-001",
  "installation_date": "2024-01-15",
  "status": "operational",
  "location": "String 1, Position 1"
}
```

#### Get Asset

```http
GET /assets/{asset_id}
Authorization: Bearer {token}
```

#### Update Asset

```http
PUT /assets/{asset_id}
Authorization: Bearer {token}
```

#### Delete Asset

```http
DELETE /assets/{asset_id}
Authorization: Bearer {token}
```

### String Configuration

#### Get String Configuration

```http
GET /assets/strings/{plant_id}
Authorization: Bearer {token}
```

#### Assign Panels to String

```http
POST /assets/strings/assign
Authorization: Bearer {token}
Content-Type: application/json

{
  "plant_id": 5,
  "array_id": 1,
  "string_number": 1,
  "panel_ids": [101, 102, 103, 104]
}
```

### Bulk Import

#### Import Assets from CSV

```http
POST /assets/bulk/import
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: panels.csv
plant_id: 5
asset_type: solar_panel
```

**CSV Format:**
```csv
serial_number,manufacturer,model,power_rating_w,installation_date,string_number
SP-001,SunPower,Maxeon 3,400,2024-01-15,1
SP-002,SunPower,Maxeon 3,400,2024-01-15,1
```

---

## Workflows

**Base Path:** `/api/v1/workflows`

Manage regulatory workflows and approval processes.

### Workflow CRUD

#### List Workflows

```http
GET /workflows?plant_id=5&status=in_progress&skip=0&limit=20
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": 10,
    "name": "Solar Installation Approval",
    "plant_id": 5,
    "status": "in_progress",
    "progress_percentage": 60,
    "current_phase": "Technical Review",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

#### Get Workflow Details

```http
GET /workflows/{workflow_id}
Authorization: Bearer {token}
```

**Response includes:**
- Workflow details
- All phases with status
- Associated documents
- Compliance requirements
- Timeline and deadlines

#### Create Workflow

```http
POST /workflows
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "New Plant Authorization",
  "plant_id": 5,
  "template_id": 2,
  "workflow_type": "authorization",
  "priority": "high"
}
```

#### Update Workflow

```http
PUT /workflows/{workflow_id}
Authorization: Bearer {token}
```

#### Complete Workflow

```http
POST /workflows/{workflow_id}/complete
Authorization: Bearer {token}
```

### Workflow Templates

#### List Templates

```http
GET /workflows/templates?category=authorization
Authorization: Bearer {token}
```

#### Get Template

```http
GET /workflows/templates/{template_id}
Authorization: Bearer {token}
```

#### Create Workflow from Template

```http
POST /workflows/templates/{template_id}/create-workflow
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "My Custom Workflow",
  "plant_id": 5,
  "custom_phases": [...]
}
```

---

## Workflow Phases

**Base Path:** `/api/v1/workflows`

Manage individual phases within workflows.

### Phase Details

#### Get Phase Detail

```http
GET /workflows/{workflow_id}/phases/{phase_id}
Authorization: Bearer {token}
```

**Response includes:**
- Phase details
- Required documents
- Checklist items
- Portal information
- Cost information
- Deadlines

### Phase Updates

#### Update Phase Status

```http
PUT /workflows/{workflow_id}/phases/{phase_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "completed",
  "notes": "Documents submitted successfully",
  "form_data": {
    "protocol_number": "PROTO-2024-001",
    "submission_date": "2024-01-15"
  }
}
```

**Response:**
```json
{
  "id": 15,
  "status": "completed",
  "completed_date": "2024-01-15T14:30:00Z",
  "workflow_progress": 75,
  "workflow_status": "in_progress"
}
```

#### Assign Phase

```http
PUT /workflows/{workflow_id}/phases/{phase_id}/assign
Authorization: Bearer {token}
Content-Type: application/json

{
  "assignee_id": 5
}
```

### Phase Attachments

#### Upload Document

```http
POST /workflows/{workflow_id}/phases/{phase_id}/documents
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: document.pdf
document_type: authorization_form
description: Signed authorization form
```

**Response:**
```json
{
  "document_id": 25,
  "name": "document.pdf",
  "type": "authorization_form",
  "phase_id": 15,
  "message": "Document uploaded successfully"
}
```

#### Add Comment

```http
POST /workflows/{workflow_id}/phases/{phase_id}/comments
Authorization: Bearer {token}
Content-Type: application/json

{
  "text": "Waiting for technical review approval",
  "type": "note"
}
```

---

## Documents

**Base Path:** `/api/v1/documents`

Centralized document management system.

### List Documents

```http
GET /documents?plant_id=5&document_type=technical&skip=0&limit=20
Authorization: Bearer {token}
```

### Upload Document

```http
POST /documents
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: technical_specs.pdf
document_type: technical_documentation
plant_id: 5
description: Technical specifications for solar panels
```

### Get Document

```http
GET /documents/{document_id}
Authorization: Bearer {token}
```

### Download Document

```http
GET /documents/{document_id}/download
Authorization: Bearer {token}
```

### Update Document Metadata

```http
PUT /documents/{document_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "description": "Updated description",
  "tags": ["technical", "solar", "2024"]
}
```

### Delete Document

```http
DELETE /documents/{document_id}
Authorization: Bearer {token}
```

---

## Compliance

**Base Path:** `/api/v1/compliance`

Track regulatory compliance requirements and deadlines.

### List Compliance Records

```http
GET /compliance?plant_id=5&status=pending&skip=0&limit=20
Authorization: Bearer {token}
```

### Create Compliance Record

```http
POST /compliance
Authorization: Bearer {token}
Content-Type: application/json

{
  "plant_id": 5,
  "requirement_type": "annual_report",
  "authority": "GSE",
  "deadline": "2024-12-31",
  "status": "pending",
  "description": "Annual GSE compliance report"
}
```

### Get Compliance Record

```http
GET /compliance/{record_id}
Authorization: Bearer {token}
```

### Update Compliance Record

```http
PUT /compliance/{record_id}
Authorization: Bearer {token}
```

### Get Compliance Score

```http
GET /compliance/score?plant_id=5
Authorization: Bearer {token}
```

**Response:**
```json
{
  "plant_id": 5,
  "overall_score": 92,
  "total_requirements": 15,
  "completed": 14,
  "pending": 1,
  "overdue": 0,
  "next_deadline": "2024-06-30",
  "next_requirement": "Semi-annual safety inspection"
}
```

---

## Dashboard

**Base Path:** `/api/v1/dashboard`

Get aggregated statistics and analytics.

### Get Dashboard Overview

```http
GET /dashboard/overview
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_plants": 12,
  "total_capacity_kw": 6000.0,
  "active_workflows": 5,
  "pending_compliance": 3,
  "cer_communities": 2,
  "total_members": 45,
  "monthly_production_kwh": 180000.0,
  "compliance_score": 94
}
```

### Get Plant Statistics

```http
GET /dashboard/plants/stats?period=month
Authorization: Bearer {token}
```

### Get CER Statistics

```http
GET /dashboard/cer/stats?cer_id=5&period=month
Authorization: Bearer {token}
```

---

## Common Patterns

### Pagination

All list endpoints support pagination:

```
?skip=0&limit=20
```

- `skip`: Number of records to skip (offset)
- `limit`: Maximum records to return (default: 20, max: 100)

### Filtering

Most list endpoints support filtering:

```
?status=active&type=solar&created_after=2024-01-01
```

### Sorting

```
?sort_by=created_at&sort_order=desc
```

### Error Responses

**400 Bad Request:**
```json
{
  "detail": "Validation error: field 'name' is required"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

### Authentication Header

All protected endpoints require authentication:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Multi-Tenant Isolation

All requests are automatically filtered by the authenticated user's `tenant_id`. Users can only access resources belonging to their tenant.

---

## Rate Limiting

- **Authentication endpoints:** 5 requests per minute
- **Standard endpoints:** 100 requests per minute
- **Bulk operations:** 10 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Interactive Documentation

Visit the following URLs for interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

**Last Updated:** January 2025
**API Version:** 2.0.0
**For Support:** Create an issue on GitHub
