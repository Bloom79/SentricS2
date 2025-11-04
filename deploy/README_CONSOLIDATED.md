# Kronos EAM Consolidated - GCP Deployment

This directory contains deployment scripts for the **consolidated version** to a **NEW dedicated GCP project**.

## Quick Start

### 0. Test Docker Images (Recommended)

**Test images locally before deploying to avoid errors:**

```bash
cd kronos-eam-consolidated
./test-docker-builds.sh
```

See [`PRE_DEPLOYMENT_CHECKLIST.md`](./PRE_DEPLOYMENT_CHECKLIST.md) for details.

### 1. Setup New Project

```bash
cd deploy
export GCP_PROJECT_ID="kronos-eam-consolidated-$(date +%Y%m%d)"
./gcp-setup-consolidated.sh
```

### 2. Generate & Upload Dumps

```bash
# Generate dumps from local database
cd ../backend
export DATABASE_URL="postgresql://user:pass@localhost/kronos_eam"
python scripts/dump_all.py

# Upload to GCS
cd ../deploy
./gcp-upload-dumps-consolidated.sh
```

### 3. Initialize Database

```bash
./gcp-init-db-consolidated.sh
```

### 4. Deploy Application

```bash
./gcp-deploy-consolidated.sh
# Select option 3 (Both)
```

### 5. Seed Authenticated Data

After deployment, seed data linked to authenticated user:

```bash
cd ../backend
python scripts/seed_authenticated_data.py \
    --user-email "admin@yourcompany.com" \
    --user-name "Admin User" \
    --user-password "SecurePassword123!" \
    --user-role "Admin"
```

## Scripts

- **`gcp-setup-consolidated.sh`** - Creates NEW GCP project and infrastructure
- **`gcp-upload-dumps-consolidated.sh`** - Uploads dumps to Cloud Storage
- **`gcp-init-db-consolidated.sh`** - Initializes Cloud SQL from dumps
- **`gcp-deploy-consolidated.sh`** - Deploys backend and frontend

## Key Differences from Old Project

1. **Separate Project**: Uses `kronos-eam-consolidated-YYYYMMDD` (not overwriting old project)
2. **User-Linked Data**: Seed data is connected to authenticated users
3. **Secure Initialization**: No password hashes in dumps
4. **Automated Flow**: Cloud Build automatically imports dumps during deployment

## Documentation

- [`CONSOLIDATED_DEPLOYMENT.md`](./CONSOLIDATED_DEPLOYMENT.md) - Complete deployment guide
- [`GCP_DB_INITIALIZATION.md`](./GCP_DB_INITIALIZATION.md) - Database initialization details
- [`DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md) - General deployment guide

## Important Notes

⚠️ **Project Isolation**: This creates a NEW project, separate from existing ones.

⚠️ **User Authentication**: Seed data should be linked to authenticated users via `seed_authenticated_data.py`.

⚠️ **Passwords**: User passwords are NOT in dumps. Set them via seed script or API.

