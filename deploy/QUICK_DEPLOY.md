# Quick Deployment Guide

## Prerequisites
- GCP account with billing enabled
- `gcloud` CLI installed and authenticated
- Project permissions: Owner or Editor

## One-Command Deployment

```bash
cd deploy

# Step 1: Setup infrastructure (one-time)
./gcp-setup-consolidated.sh

# Step 2: Deploy application
export GCP_PROJECT_ID='your-project-id'  # From step 1 output
./gcp-deploy-consolidated.sh
# Choose option 3 (Both Backend and Frontend)
```

## What Gets Fixed Automatically

✅ **Database Password**: Properly stored in Secret Manager  
✅ **CORS Configuration**: Automatically updated after frontend deployment  
✅ **API URL**: Frontend correctly configured with `VITE_API_URL`  
✅ **Initial User**: Admin user created automatically  
✅ **Service Accounts**: All permissions configured  

## Default Credentials

After deployment:
- **Email**: `test@example.com`
- **Password**: `test123`

## Troubleshooting

### Database Connection Error
```bash
# Check secret
gcloud secrets versions access latest --secret=database-url

# Should contain: postgresql://kronos:PASSWORD@/...
# If missing password, re-run setup script
```

### CORS Error
```bash
# Check CORS config
gcloud run services describe kronos-eam-api \
  --format="value(spec.template.spec.containers[0].env)" \
  | grep CORS

# Should contain frontend URL
```

### User Not Found
```bash
# Create user manually
gcloud run jobs execute create-admin-user \
  --region=europe-west1 \
  --wait
```

## Files Updated

All fixes are now in:
- `deploy/gcp-setup-consolidated.sh` - Infrastructure setup
- `deploy/gcp-deploy-consolidated.sh` - Application deployment
- `backend/app/core/config.py` - CORS validator
- `frontend/Dockerfile` - Vite API URL
- `frontend/cloudbuild.yaml` - Build configuration
- `backend/cloudbuild.yaml` - CORS env vars

See `DEPLOYMENT_FIXES.md` for detailed explanation of all changes.

