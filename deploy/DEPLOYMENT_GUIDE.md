# Kronos EAM Consolidated - GCP Deployment Guide

Complete guide for deploying Kronos EAM to Google Cloud Platform.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured
3. **Docker** (for local testing)
4. **Access to the GCP project** (`kronos-eam-prod-20250802` or your project)

## Quick Start

### 1. Initial Setup (One-time)

```bash
cd kronos-eam-consolidated/deploy

# Set your GCP project ID
export GCP_PROJECT_ID="kronos-eam-prod-20250802"
export GCP_REGION="europe-west1"

# Run the setup script
./gcp-setup.sh
```

This will:
- ✅ Set up your GCP project
- ✅ Enable all required APIs
- ✅ Create Cloud SQL instance (PostgreSQL)
- ✅ Create service accounts with proper permissions
- ✅ Set up Secret Manager with required secrets
- ✅ Create Artifact Registry repository

### 2. Deploy Application

```bash
# Deploy both backend and frontend
./gcp-deploy.sh

# Or deploy individually:
# Backend only
./gcp-deploy.sh  # Select option 1

# Frontend only (after backend is deployed)
./gcp-deploy.sh  # Select option 2
```

## Manual Deployment

If you prefer to deploy manually:

### Backend Deployment

```bash
cd kronos-eam-consolidated/backend

# Get your Cloud SQL connection name
SQL_INSTANCE=$(gcloud sql instances describe kronos-db --format="value(connectionName)")

# Submit build
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION=europe-west1,_CLOUD_SQL_INSTANCE=${SQL_INSTANCE} \
    .
```

### Frontend Deployment

```bash
cd kronos-eam-consolidated/frontend

# Get backend API URL
API_URL=$(gcloud run services describe kronos-eam-api --region=europe-west1 --format="value(status.url)")/api/v1

# Submit build
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION=europe-west1,_API_URL=${API_URL} \
    .
```

## Configuration

### Environment Variables

The backend uses Secret Manager for sensitive data:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT token signing key
- `REDIS_URL` - Redis connection string (optional)

These are automatically injected from Secret Manager during deployment.

### Cloud SQL Connection

The backend connects to Cloud SQL using Unix socket:
```
postgresql://kronos:PASSWORD@/kronos_eam?host=/cloudsql/PROJECT:REGION:INSTANCE
```

Make sure the Cloud SQL instance connection name matches in `cloudbuild.yaml`.

### Frontend API URL

Update the `_API_URL` substitution in `frontend/cloudbuild.yaml` with your actual backend URL after first deployment.

## Infrastructure Details

### Cloud Run Services

#### Backend (`kronos-eam-api`)
- **Region**: europe-west1
- **Memory**: 2Gi
- **CPU**: 2 vCPU
- **Min Instances**: 1 (always warm)
- **Max Instances**: 10
- **Port**: 8000
- **Timeout**: 300s

#### Frontend (`kronos-eam-frontend`)
- **Region**: europe-west1
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Min Instances**: 0 (scales to zero)
- **Max Instances**: 10
- **Port**: 80
- **Timeout**: 60s

### Cloud SQL

- **Instance**: `kronos-db`
- **Version**: PostgreSQL 15
- **Tier**: db-f1-micro (can be upgraded)
- **Storage**: 10GB SSD
- **Backups**: Daily at 3:00 AM
- **High Availability**: Disabled by default

### Service Accounts

- **kronos-backend@PROJECT_ID.iam.gserviceaccount.com**
  - Roles: `cloudsql.client`, `secretmanager.secretAccessor`

## Database Initialization

### Option 1: Using Dump Files (Recommended)

The database can be initialized using dump files:

```bash
# 1. Generate dumps from local database
cd backend
python scripts/dump_all.py

# 2. Upload dumps to GCS
cd ../deploy
./gcp-upload-dumps.sh

# 3. Initialize database (or let Cloud Build do it automatically)
./gcp-init-db.sh
```

See [`GCP_DB_INITIALIZATION.md`](./GCP_DB_INITIALIZATION.md) for detailed instructions.

### Option 2: Using Migrations Only

If you prefer to use migrations only:

```bash
# Connect to Cloud SQL
gcloud sql connect kronos-db --user=kronos

# Run migrations
cd backend
alembic upgrade head
```

**Note**: Cloud Build automatically runs migrations after importing dumps (if available).

## Monitoring & Logs

### View Logs

```bash
# Backend logs
gcloud run services logs read kronos-eam-api --region=europe-west1

# Frontend logs
gcloud run services logs read kronos-eam-frontend --region=europe-west1

# Cloud Build logs
gcloud builds list --limit=10
```

### Health Checks

- Backend: `https://YOUR-API-URL/health`
- Frontend: `https://YOUR-FRONTEND-URL/health`

## Troubleshooting

### Common Issues

1. **Build fails with "permission denied"**
   ```bash
   # Grant Cloud Build permissions
   PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
   gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
       --role="roles/run.admin"
   ```

2. **Database connection fails**
   - Verify Cloud SQL instance exists: `gcloud sql instances list`
   - Check connection name format: `PROJECT:REGION:INSTANCE`
   - Verify service account has `cloudsql.client` role

3. **Frontend can't reach backend**
   - Update `_API_URL` in `frontend/cloudbuild.yaml`
   - Check CORS settings in backend
   - Verify backend is deployed and accessible

4. **Secrets not found**
   ```bash
   # List secrets
   gcloud secrets list
   
   # Create missing secret
   echo -n "value" | gcloud secrets create secret-name --data-file=-
   ```

### Update Service Configuration

```bash
# Update backend resources
gcloud run services update kronos-eam-api \
    --memory=4Gi \
    --cpu=4 \
    --region=europe-west1

# Update environment variables
gcloud run services update kronos-eam-api \
    --set-env-vars="NEW_VAR=value" \
    --region=europe-west1
```

## Cost Estimation

### Monthly Costs (Approximate)

- **Cloud SQL** (db-f1-micro): ~$10-15/month
- **Cloud Run** (Backend, 1 min instance): ~$30-50/month
- **Cloud Run** (Frontend, scale-to-zero): ~$5-10/month
- **Artifact Registry**: ~$1-2/month
- **Secret Manager**: Free (first 6 versions)
- **Cloud Build**: Pay per build (~$0.003 per build-minute)

**Total**: ~$50-80/month for development/testing

For production, consider:
- Upgrading Cloud SQL tier
- Enabling Cloud SQL high availability
- Using Cloud CDN for frontend
- Setting up monitoring and alerting

## Security Best Practices

1. ✅ **Use Secret Manager** for all sensitive data
2. ✅ **Enable deletion protection** on Cloud SQL
3. ✅ **Use least-privilege IAM** roles
4. ✅ **Enable Cloud Armor** for DDoS protection
5. ✅ **Use Cloud Run authentication** for internal services
6. ✅ **Enable audit logs** for compliance
7. ✅ **Regular security updates** - keep dependencies updated

## Next Steps

1. Set up **custom domain** for your services
2. Configure **Cloud CDN** for frontend
3. Set up **monitoring alerts** in Cloud Monitoring
4. Configure **backup schedules** for Cloud SQL
5. Set up **CI/CD pipeline** with GitHub Actions
6. Enable **Cloud Armor** for security

## Support

For issues or questions:
1. Check Cloud Build logs: `gcloud builds list`
2. Check Cloud Run logs: `gcloud run services logs read`
3. Review this guide's troubleshooting section
4. Check GCP documentation: https://cloud.google.com/docs

---

**Last Updated**: October 2025
**Version**: 2.0.0

