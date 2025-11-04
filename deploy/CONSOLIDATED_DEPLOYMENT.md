# Kronos EAM Consolidated - Complete GCP Deployment Guide

Complete deployment guide for the consolidated version to a **NEW dedicated GCP project**.

## Overview

This guide deploys the consolidated Kronos EAM to a **separate GCP project** (not overwriting existing projects). The database initialization is designed to work with authenticated users - seed data is linked to the user who authenticates on the cloud application.

## Key Features

- ✅ **New Dedicated Project**: Creates `kronos-eam-consolidated-YYYYMMDD`
- ✅ **Database Initialization**: Uses dump files for schema and seed data
- ✅ **User-Linked Data**: Seed data is connected to authenticated users
- ✅ **Secure**: No password hashes in dumps, proper authentication flow

## Complete Deployment Workflow

### Step 0: Test Docker Images Locally (Recommended)

**IMPORTANT**: Test Docker images locally before deploying to catch errors early!

```bash
cd kronos-eam-consolidated

# Test both images
./test-docker-builds.sh

# Or test individually
cd backend && ./test-docker-image.sh
cd ../frontend && export API_URL="http://localhost:8000/api/v1" && ./test-docker-image.sh
```

See [`PRE_DEPLOYMENT_CHECKLIST.md`](./PRE_DEPLOYMENT_CHECKLIST.md) for details.

### Step 1: Setup New GCP Project

```bash
cd kronos-eam-consolidated/deploy

# Set project ID (or use auto-generated)
export GCP_PROJECT_ID="kronos-eam-consolidated-$(date +%Y%m%d)"
export GCP_REGION="europe-west1"

# Run setup (creates NEW project)
./gcp-setup-consolidated.sh
```

This creates:
- ✅ New GCP project
- ✅ Cloud SQL instance (PostgreSQL 15)
- ✅ Service accounts with proper permissions
- ✅ Secret Manager secrets
- ✅ Artifact Registry repository
- ✅ Cloud Storage buckets

### Step 2: Generate Database Dumps

```bash
cd ../backend

# Set your local database URL (with existing seed data)
export DATABASE_URL="postgresql://user:pass@localhost/kronos_eam"

# Generate dumps
python scripts/dump_all.py
```

This creates:
- `schema_dump_*.sql` - Database structure
- `seed_data_dump_*.sql` - Seed data (excluding sensitive auth data)
- `safe_user_seed_*.sql` - Users with placeholder passwords

### Step 3: Upload Dumps to Cloud Storage

```bash
cd ../deploy

# Upload dumps to GCS
./gcp-upload-dumps-consolidated.sh
```

This uploads to: `gs://{PROJECT_ID}-db-init/`

### Step 4: Initialize Database

```bash
# Initialize database from dumps
./gcp-init-db-consolidated.sh
```

This:
- ✅ Enables PostGIS extension
- ✅ Imports schema from GCS
- ✅ Imports seed data from GCS
- ✅ Prompts before importing users (optional)

### Step 5: Deploy Application

```bash
# Deploy backend and frontend
./gcp-deploy-consolidated.sh
# Select option 3
```

This will:
- ✅ Build Docker images
- ✅ Push to Artifact Registry
- ✅ Import database dumps (if available)
- ✅ Run Alembic migrations
- ✅ Deploy to Cloud Run

### Step 6: Seed Authenticated Data

**IMPORTANT**: After deployment, seed data should be linked to the authenticated user.

#### Option A: Using the Seed Script (Recommended)

After the first user logs in to the cloud application:

```bash
# Connect to Cloud SQL or use Cloud SQL Proxy
# Then run:

cd backend
python scripts/seed_authenticated_data.py \
    --user-email "admin@yourcompany.com" \
    --user-name "Admin User" \
    --user-password "SecurePassword123!" \
    --user-role "Admin" \
    --tenant-id "your-tenant-id" \
    --tenant-name "Your Company"
```

This creates:
- ✅ Tenant (if not exists)
- ✅ User account (authenticated user)
- ✅ Sites, Plants, Assets (linked to this user)
- ✅ All data properly associated with tenant and user

#### Option B: Manual via API

After logging in, use the API to create data, which will automatically link to the authenticated user's tenant.

## Authentication Flow

### Initial Setup

1. **Deploy application** → Database initialized with schema
2. **First user registration** → Creates tenant and user
3. **Seed authenticated data** → Links all data to this user/tenant

### User Authentication

The application uses JWT authentication:
- Users authenticate via `/api/v1/auth/login`
- JWT token contains `tenant_id` and `user_id`
- All API requests automatically filter by `tenant_id`
- Seed data script links data to the authenticated user

## Project Structure

```
New GCP Project: kronos-eam-consolidated-YYYYMMDD
├── Cloud SQL
│   └── kronos-db (PostgreSQL 15)
│       └── kronos_eam database
├── Cloud Run Services
│   ├── kronos-eam-api (Backend)
│   └── kronos-eam-frontend (Frontend)
├── Artifact Registry
│   └── kronos-eam (Docker images)
├── Cloud Storage
│   ├── {PROJECT_ID}-db-init (Dump files)
│   └── {PROJECT_ID}-storage (App storage)
└── Secret Manager
    ├── database-url
    ├── jwt-secret
    └── redis-url
```

## Environment Variables

### Backend (Cloud Run)

Set via Secret Manager:
- `DATABASE_URL` - Cloud SQL connection string
- `JWT_SECRET_KEY` - JWT signing key
- `REDIS_URL` - Redis connection (optional)

Set via environment:
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`

### Frontend (Cloud Run)

Set via substitution:
- `REACT_APP_API_URL` - Backend API URL

## Database Initialization Details

### Schema Import

The schema is imported from `schema.sql` which contains:
- All table definitions
- Indexes
- Foreign keys
- PostGIS extensions

### Seed Data Import

Seed data is imported from `seed_data.sql` which contains:
- ✅ Sites
- ✅ Plants
- ✅ Assets
- ✅ Workflows
- ✅ Documents
- ✅ Compliance records
- ❌ **NO** user passwords
- ❌ **NO** MFA secrets

### User Management

Users are handled separately:
1. **Initial user**: Created via registration or seed script
2. **Password**: Set securely via seed script or API
3. **Tenant linkage**: All data linked to user's tenant

## Post-Deployment Steps

### 1. Verify Deployment

```bash
# Get service URLs
BACKEND_URL=$(gcloud run services describe kronos-eam-api \
    --region=europe-west1 \
    --format="value(status.url)")

FRONTEND_URL=$(gcloud run services describe kronos-eam-frontend \
    --region=europe-west1 \
    --format="value(status.url)")

echo "Backend: ${BACKEND_URL}"
echo "Frontend: ${FRONTEND_URL}"

# Test health
curl ${BACKEND_URL}/health
```

### 2. Create First User

**Option A: Via API**

```bash
curl -X POST ${BACKEND_URL}/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "SecurePassword123!",
    "name": "Admin User"
  }'
```

**Option B: Via Seed Script**

```bash
cd backend
python scripts/seed_authenticated_data.py \
    --user-email "admin@yourcompany.com" \
    --user-name "Admin User" \
    --user-password "SecurePassword123!" \
    --user-role "Admin"
```

### 3. Seed Data for Authenticated User

After creating the user, seed data linked to them:

```bash
cd backend

# Set Cloud SQL connection
export DATABASE_URL="postgresql://kronos:PASSWORD@/kronos_eam?host=/cloudsql/PROJECT:REGION:kronos-db"

# Seed data (already linked to user)
python scripts/seed_authenticated_data.py \
    --user-email "admin@yourcompany.com" \
    --user-name "Admin User" \
    --user-password "SecurePassword123!" \
    --user-role "Admin"
```

This creates sites, plants, and assets linked to the authenticated user.

## Security Considerations

### Authentication

- ✅ Passwords are hashed (bcrypt)
- ✅ JWT tokens used for authentication
- ✅ Multi-tenant isolation via `tenant_id`
- ✅ No password hashes in dumps

### Data Isolation

- ✅ All data filtered by `tenant_id`
- ✅ Users can only access their tenant's data
- ✅ Seed data linked to authenticated user's tenant

### Secrets Management

- ✅ Database passwords in Secret Manager
- ✅ JWT secrets in Secret Manager
- ✅ Never commit secrets to version control

## Troubleshooting

### Database Connection Issues

```bash
# Check Cloud SQL instance
gcloud sql instances describe kronos-db

# Check database exists
gcloud sql databases list --instance=kronos-db

# Test connection
gcloud sql connect kronos-db --user=kronos
```

### Import Failures

```bash
# Check Cloud SQL import operations
gcloud sql operations list --instance=kronos-db --limit=10

# View operation details
gcloud sql operations describe OPERATION_ID --instance=kronos-db
```

### Deployment Issues

```bash
# Check Cloud Build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID

# Check Cloud Run logs
gcloud run services logs read kronos-eam-api --region=europe-west1
```

## Cost Estimation

Monthly costs for the consolidated project:

- **Cloud SQL** (db-f1-micro): ~$10-15/month
- **Cloud Run** (Backend, 1 min instance): ~$30-50/month
- **Cloud Run** (Frontend, scale-to-zero): ~$5-10/month
- **Artifact Registry**: ~$1-2/month
- **Cloud Storage**: ~$1-2/month
- **Secret Manager**: Free (first 6 versions)

**Total**: ~$50-80/month

## Next Steps

1. ✅ Set up custom domain
2. ✅ Configure Cloud CDN
3. ✅ Set up monitoring and alerts
4. ✅ Configure backup schedules
5. ✅ Set up CI/CD pipeline

---

**Last Updated**: January 2025

