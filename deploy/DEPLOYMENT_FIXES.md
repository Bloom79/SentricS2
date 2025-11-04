# Deployment Fixes Summary

This document summarizes all the fixes applied to ensure smooth deployment without manual intervention.

## Issues Fixed

### 1. Database Password in Secret Manager
**Problem**: The `database-url` secret was being created without a password, causing "no password supplied" errors.

**Fix**: 
- Modified `gcp-setup-consolidated.sh` to properly store the database password when creating the Cloud SQL instance
- Added logic to verify and update the secret if it's missing a password
- Password is now properly included in the `DATABASE_URL` connection string

**Files Modified**:
- `deploy/gcp-setup-consolidated.sh` (lines 172-244)

### 2. Frontend API URL Configuration
**Problem**: Frontend was using `REACT_APP_API_URL` but the project uses Vite, which requires `VITE_API_URL`.

**Fix**:
- Updated `frontend/Dockerfile` to use `VITE_API_URL` instead of `REACT_APP_API_URL`
- Updated `frontend/cloudbuild.yaml` to pass `VITE_API_URL` as build argument

**Files Modified**:
- `frontend/Dockerfile`
- `frontend/cloudbuild.yaml`

### 3. Backend CORS Configuration
**Problem**: CORS origins were not properly configured, causing CORS errors when frontend tried to connect to backend.

**Fix**:
- Improved CORS validator in `backend/app/core/config.py` to handle JSON array format, comma-separated strings, and single values
- Updated `backend/cloudbuild.yaml` to set CORS origins as JSON array: `["https://frontend-url"]`
- Added automatic CORS update in `gcp-deploy-consolidated.sh` after frontend deployment

**Files Modified**:
- `backend/app/core/config.py` (CORS validator function)
- `backend/cloudbuild.yaml` (CORS env var)
- `deploy/gcp-deploy-consolidated.sh` (automatic CORS update)

### 4. Initial Admin User Creation
**Problem**: No users existed in the database after deployment, making it impossible to log in.

**Fix**:
- Added `create_initial_user()` function in `gcp-deploy-consolidated.sh`
- Automatically creates a Cloud Run job to initialize admin user after backend deployment
- Uses existing `scripts/create_test_user.py` script
- Checks if user already exists before creating

**Files Modified**:
- `deploy/gcp-deploy-consolidated.sh` (user creation function)

### 5. Deployment Flow Improvements
**Problem**: Deployment script didn't handle all edge cases and didn't provide clear next steps.

**Fix**:
- Added proper waiting periods after deployments
- Added automatic CORS updates after frontend deployment
- Added user creation step after backend deployment
- Improved final output with login credentials and URLs

**Files Modified**:
- `deploy/gcp-deploy-consolidated.sh`

## Default Login Credentials

After deployment, you can log in with:
- **Email**: `test@example.com`
- **Password**: `test123`

⚠️ **Important**: Change this password after first login in production!

## Deployment Steps

1. **Setup Infrastructure**:
   ```bash
   cd deploy
   ./gcp-setup-consolidated.sh
   ```

2. **Deploy Application**:
   ```bash
   ./gcp-deploy-consolidated.sh
   # Choose option 3 (Both Backend and Frontend)
   ```

3. **Access Application**:
   - The script will output the frontend URL
   - Log in with the credentials above

## What Happens Automatically

1. ✅ Database password is properly stored in Secret Manager
2. ✅ Backend is deployed with correct CORS configuration
3. ✅ Frontend is built with correct API URL (`VITE_API_URL`)
4. ✅ CORS is automatically updated after frontend deployment
5. ✅ Initial admin user is created automatically
6. ✅ Login credentials are displayed at the end

## Verification

After deployment, verify everything works:

```bash
# Check backend health
curl https://kronos-eam-api-xxxxx.a.run.app/docs

# Test login
curl -X POST https://kronos-eam-api-xxxxx.a.run.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

## Troubleshooting

### Database Connection Issues
If you see "no password supplied" errors:
1. Check the `database-url` secret: `gcloud secrets versions access latest --secret=database-url`
2. Verify it includes a password: should contain `kronos:PASSWORD@`
3. If missing, run setup script again (it will detect and fix)

### CORS Issues
If frontend can't connect to backend:
1. Check CORS env var: `gcloud run services describe kronos-eam-api --format="value(spec.template.spec.containers[0].env)"`
2. Should contain: `BACKEND_CORS_ORIGINS=["https://frontend-url"]`
3. Redeploy frontend to trigger CORS update

### User Creation Issues
If login fails with "user not found":
1. Check if Cloud Run job exists: `gcloud run jobs list --region=europe-west1`
2. Execute manually: `gcloud run jobs execute create-admin-user --region=europe-west1 --wait`
3. Check logs: `gcloud logging read "resource.type=cloud_run_job" --limit=50`

## Files Changed Summary

- `deploy/gcp-setup-consolidated.sh` - Fixed database password handling
- `deploy/gcp-deploy-consolidated.sh` - Added CORS updates and user creation
- `backend/app/core/config.py` - Improved CORS validator
- `backend/cloudbuild.yaml` - Added CORS env var
- `frontend/Dockerfile` - Changed to VITE_API_URL
- `frontend/cloudbuild.yaml` - Changed to VITE_API_URL

