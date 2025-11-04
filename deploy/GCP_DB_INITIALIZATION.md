# GCP Database Initialization Guide

Complete guide for initializing Cloud SQL database using dump files.

## Overview

This guide covers three methods to initialize your GCP Cloud SQL database:
1. **Automated**: Using Cloud Build (recommended for CI/CD)
2. **Semi-automated**: Using shell scripts
3. **Manual**: Using gcloud commands directly

## Prerequisites

1. GCP project set up (`gcp-setup.sh` completed)
2. Cloud SQL instance created
3. Dump files generated (or will be generated automatically)

## Method 1: Automated (Recommended)

### Step 1: Generate Dumps Locally

```bash
cd kronos-eam-consolidated/backend

# Set your local database URL
export DATABASE_URL="postgresql://user:pass@localhost/kronos_eam"

# Generate dumps
python scripts/dump_all.py
```

This creates:
- `schema_dump_YYYYMMDD_HHMMSS.sql`
- `seed_data_dump_YYYYMMDD_HHMMSS.sql`
- `safe_user_seed_YYYYMMDD_HHMMSS.sql`

### Step 2: Upload Dumps to Cloud Storage

```bash
cd kronos-eam-consolidated/deploy
export GCP_PROJECT_ID="kronos-eam-prod-20250802"

# Upload dumps to GCS
./gcp-upload-dumps.sh
```

This will:
- Create a Cloud Storage bucket: `{PROJECT_ID}-db-init`
- Upload schema.sql, seed_data.sql, and users.sql

### Step 3: Initialize Database

The Cloud Build process will automatically:
1. Check for dump files in GCS
2. Import schema if found
3. Import seed data if found
4. Run Alembic migrations to ensure schema is current

Or manually trigger:

```bash
# Import dumps manually
./gcp-init-db.sh
```

## Method 2: Semi-Automated Scripts

### Quick Start

```bash
cd kronos-eam-consolidated/deploy

# 1. Generate dumps (if not already done)
cd ../backend
python scripts/dump_all.py
cd ../deploy

# 2. Upload to GCS
./gcp-upload-dumps.sh

# 3. Initialize database
./gcp-init-db.sh
```

### What the Scripts Do

#### `gcp-upload-dumps.sh`
- Creates Cloud Storage bucket if needed
- Uploads dump files to GCS
- Prepares files for Cloud SQL import

#### `gcp-init-db.sh`
- Checks Cloud SQL instance exists
- Creates database if needed
- Enables PostGIS extension
- Imports schema from GCS
- Imports seed data from GCS
- Prompts before importing users

## Method 3: Manual Process

### Step 1: Create Cloud Storage Bucket

```bash
export PROJECT_ID="kronos-eam-prod-20250802"
export REGION="europe-west1"

gsutil mb -l ${REGION} gs://${PROJECT_ID}-db-init
```

### Step 2: Upload Dump Files

```bash
# Upload schema
gsutil cp schema_dump_*.sql gs://${PROJECT_ID}-db-init/schema.sql

# Upload seed data
gsutil cp seed_data_dump_*.sql gs://${PROJECT_ID}-db-init/seed_data.sql

# Upload users (optional)
gsutil cp safe_user_seed_*.sql gs://${PROJECT_ID}-db-init/users.sql
```

### Step 3: Enable PostGIS

```bash
gcloud sql databases execute-sql kronos-db \
    --database=kronos_eam \
    --sql="CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS postgis_topology;"
```

### Step 4: Import Schema

```bash
gcloud sql import sql kronos-db \
    gs://${PROJECT_ID}-db-init/schema.sql \
    --database=kronos_eam
```

### Step 5: Import Seed Data

```bash
gcloud sql import sql kronos-db \
    gs://${PROJECT_ID}-db-init/seed_data.sql \
    --database=kronos_eam
```

### Step 6: Import Users (Optional)

```bash
# ⚠️ Remember: Users will have placeholder passwords!
gcloud sql import sql kronos-db \
    gs://${PROJECT_ID}-db-init/users.sql \
    --database=kronos_eam

# Update passwords after import
```

## Using Python Script

You can also use the Python script directly:

```bash
cd backend

# Import from GCS
python scripts/init_gcp_db.py \
    --schema gs://${PROJECT_ID}-db-init/schema.sql \
    --seed gs://${PROJECT_ID}-db-init/seed_data.sql \
    --users gs://${PROJECT_ID}-db-init/users.sql \
    --instance kronos-db \
    --database kronos_eam \
    --enable-postgis

# Or import from local files (if using Cloud SQL Proxy)
python scripts/init_gcp_db.py \
    --schema ./dumps/schema_dump_20250101.sql \
    --seed ./dumps/seed_data_dump_20250101.sql \
    --users ./dumps/safe_user_seed_20250101.sql \
    --enable-postgis
```

## Cloud Build Integration

The `cloudbuild.yaml` is configured to automatically:
1. Check for dump files in GCS bucket `{PROJECT_ID}-db-init`
2. Import schema.sql if present
3. Import seed_data.sql if present
4. Run Alembic migrations to ensure schema is current

This happens automatically during deployment, so you only need to:
1. Upload dumps once
2. Deploy - initialization happens automatically

## Post-Import Steps

### 1. Verify Database

```bash
# List databases
gcloud sql databases list --instance=kronos-db

# Check tables
gcloud sql databases execute-sql kronos-db \
    --database=kronos_eam \
    --sql="SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
```

### 2. Update User Passwords

**CRITICAL**: If you imported users, update passwords immediately:

```python
# Connect to Cloud SQL and update passwords
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash

db = next(get_db())
for user in db.query(User).all():
    # Set secure password
    user.password_hash = get_password_hash("your_secure_password")
db.commit()
```

Or using SQL:

```sql
-- Update password hash for a user
-- Use: python -c "from app.core.security import get_password_hash; print(get_password_hash('password'))"
UPDATE users SET password_hash = '$2b$12$...' WHERE email = 'user@example.com';
```

### 3. Run Migrations (if needed)

```bash
# If you only imported schema, run migrations to ensure everything is current
cd backend
alembic upgrade head
```

## Troubleshooting

### Import Fails with "Permission Denied"

```bash
# Grant Cloud SQL import permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/cloudsql.admin"
```

### PostGIS Extension Fails

```bash
# Enable PostGIS manually
gcloud sql databases execute-sql kronos-db \
    --database=kronos_eam \
    --sql="CREATE EXTENSION IF NOT EXISTS postgis;"
```

### Dump Files Not Found

The scripts will automatically generate dumps if:
- `DATABASE_URL` environment variable is set
- Local database is accessible
- Python scripts can run

Otherwise, generate manually:
```bash
cd backend
export DATABASE_URL="postgresql://user:pass@localhost/kronos_eam"
python scripts/dump_all.py
```

### Foreign Key Violations

If you get foreign key violations:
1. Check import order (schema → seed data → users)
2. Verify tenant data exists before dependent data
3. Review dump files for missing dependencies

## Security Best Practices

1. ✅ **Never commit dump files** with real user data to version control
2. ✅ **Use safe user seeds** with placeholder passwords
3. ✅ **Update passwords immediately** after import
4. ✅ **Restrict GCS bucket access** to Cloud SQL service account
5. ✅ **Clean up dump files** from GCS after import
6. ✅ **Review dump contents** before importing to production

## Automated Workflow

For production deployments, use this workflow:

```bash
# 1. Initial setup (one-time)
./deploy/gcp-setup.sh

# 2. Generate dumps from staging/dev database
cd backend
python scripts/dump_all.py

# 3. Upload dumps
cd ../deploy
./gcp-upload-dumps.sh

# 4. Deploy (automatically imports dumps)
./gcp-deploy.sh

# 5. Update user passwords
# (manual step - use secure method)
```

## File Locations

- **Dump Scripts**: `backend/scripts/dump_*.py`
- **Import Scripts**: `backend/scripts/init_gcp_db.py`
- **Deployment Scripts**: `deploy/gcp-*.sh`
- **Cloud Build Config**: `backend/cloudbuild.yaml`
- **GCS Bucket**: `gs://{PROJECT_ID}-db-init/`

---

**Last Updated**: January 2025

