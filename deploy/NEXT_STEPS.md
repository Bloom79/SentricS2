# Next Steps After Setup

## Setup Complete! ✅

Your GCP infrastructure is ready:
- **Project**: kronos-eam-251031
- **Cloud SQL**: kronos-db (PostgreSQL 15)
- **Region**: europe-west1

## Deployment Steps

### Option A: Deploy Without Database Dumps (Recommended for First Time)

If you don't have existing data to migrate, just deploy:

```bash
cd ~/sentrics/kronos-eam-consolidated/deploy
export GCP_PROJECT_ID='kronos-eam-251031'

# Deploy application (will run migrations automatically)
./gcp-deploy-consolidated.sh
# Select option 3 (Both backend and frontend)
```

### Option B: Deploy With Database Dumps (If You Have Local Data)

If you have a local database with data you want to migrate:

```bash
cd ~/sentrics/kronos-eam-consolidated/deploy
export GCP_PROJECT_ID='kronos-eam-251031'

# 1. Generate dumps from local database
cd ../backend
export DATABASE_URL="postgresql://user:pass@localhost/kronos_eam"
python scripts/dump_all.py

# 2. Upload dumps to GCS
cd ../deploy
./gcp-upload-dumps-consolidated.sh

# 3. Initialize database from dumps
./gcp-init-db-consolidated.sh

# 4. Deploy application
./gcp-deploy-consolidated.sh
# Select option 3 (Both backend and frontend)
```

## After Deployment

### 1. Seed Authenticated Data

After the first user logs in, seed data linked to that user:

```bash
cd ~/sentrics/kronos-eam-consolidated/backend

# Connect to Cloud SQL (use Cloud SQL Proxy or direct connection)
export DATABASE_URL="postgresql://kronos:PASSWORD@/kronos_eam?host=/cloudsql/kronos-eam-251031:europe-west1:kronos-db"

python scripts/seed_authenticated_data.py \
    --user-email "admin@yourcompany.com" \
    --user-name "Admin User" \
    --user-password "SecurePassword123!" \
    --user-role "Admin"
```

### 2. Get Service URLs

```bash
gcloud run services list --project=kronos-eam-251031 --region=europe-west1
```

### 3. Access Your Application

- **Frontend**: https://kronos-eam-frontend-xxxxx.a.run.app
- **Backend API**: https://kronos-eam-api-xxxxx.a.run.app/api/v1

## Quick Deploy (All Steps)

If you want to deploy everything at once:

```bash
cd ~/sentrics/kronos-eam-consolidated/deploy
export GCP_PROJECT_ID='kronos-eam-251031'
./gcp-deploy-consolidated.sh
# Select option 3
```

The deployment will:
- Build Docker images
- Push to Artifact Registry
- Run database migrations (if no dumps)
- Deploy to Cloud Run
- Configure networking

---

**Ready to deploy?** Run: `./gcp-deploy-consolidated.sh` and select option 3!

