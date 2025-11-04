# Testing Docker Images Before Deployment

Test Docker images locally before deploying to GCP to catch errors early and save deployment time.

## Quick Test

Test both images at once:

```bash
cd kronos-eam-consolidated
./test-docker-builds.sh
```

## Individual Tests

### Test Backend Image

```bash
cd backend

# Option 1: With local database
export DATABASE_URL="postgresql://user:pass@localhost/kronos_eam"
./test-docker-image.sh

# Option 2: Without database (will test build only)
./test-docker-image.sh
```

**What it tests:**
- ✅ Docker image builds successfully
- ✅ Container starts correctly
- ✅ Health endpoint responds
- ✅ API endpoints are accessible
- ✅ No critical errors in logs

### Test Frontend Image

```bash
cd frontend

# Set backend API URL (if backend is running locally)
export API_URL="http://localhost:8000/api/v1"

./test-docker-image.sh
```

**What it tests:**
- ✅ Docker image builds successfully
- ✅ Nginx serves static files
- ✅ Health endpoint works
- ✅ React app is bundled correctly
- ✅ API URL is correctly embedded

## Test Process

### 1. Backend Test

The backend test script:
1. Builds the Docker image
2. Starts a container
3. Waits for health endpoint
4. Tests key endpoints
5. Checks logs for errors
6. Keeps container running for manual testing

**Expected output:**
```
✅ Image built successfully
✅ Container started
✅ Service is ready!
✅ Health endpoint works
✅ No critical errors found
```

### 2. Frontend Test

The frontend test script:
1. Builds the Docker image with API URL
2. Starts a container
3. Waits for nginx to be ready
4. Tests serving static files
5. Verifies React app is bundled
6. Checks logs for errors

**Expected output:**
```
✅ Image built successfully
✅ Container started
✅ Service is ready!
✅ Static assets work
✅ React app verified
```

## Manual Testing

After the automated tests, manually verify:

### Backend

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Check logs
docker logs -f kronos-backend-test
```

### Frontend

```bash
# Open in browser
open http://localhost:8080

# Check if API calls work (if backend is running)
# Check browser console for errors
```

## Troubleshooting

### Backend Build Fails

**Error**: `ModuleNotFoundError` or `ImportError`
- **Fix**: Check `requirements.txt` includes all dependencies
- **Fix**: Verify Python version matches (3.11)

**Error**: `Database connection failed`
- **Fix**: For local testing, ensure database is running
- **Fix**: Check `DATABASE_URL` format
- **Note**: Tests will still run without database (migrations will fail)

### Frontend Build Fails

**Error**: `npm ci` fails
- **Fix**: Check `package.json` and `package-lock.json` are in sync
- **Fix**: Run `npm install` locally first

**Error**: `npm run build` fails
- **Fix**: Check for TypeScript errors: `npm run build` locally
- **Fix**: Verify all imports are correct

**Error**: API URL not set correctly
- **Fix**: Check `REACT_APP_API_URL` build argument
- **Fix**: Verify it's used in `vite.config.ts` or build config

### Container Fails to Start

**Error**: Port already in use
- **Fix**: Stop existing containers: `docker stop kronos-backend-test kronos-frontend-test`
- **Fix**: Change ports in test script

**Error**: Health check fails
- **Fix**: Check application logs: `docker logs kronos-backend-test`
- **Fix**: Verify application starts correctly
- **Fix**: Check health endpoint exists: `/health`

## Pre-Deployment Checklist

Before deploying to GCP, verify:

- [ ] Backend image builds without errors
- [ ] Backend container starts and health check passes
- [ ] Backend API endpoints respond correctly
- [ ] Frontend image builds without errors
- [ ] Frontend container serves static files
- [ ] Frontend can reach backend API (if testing integration)
- [ ] No critical errors in container logs
- [ ] Image sizes are reasonable (< 1GB each)
- [ ] Environment variables are correctly set

## Integration Testing

Test both containers together:

```bash
# Terminal 1: Start backend
cd backend
./test-docker-image.sh

# Terminal 2: Start frontend (after backend is ready)
cd frontend
export API_URL="http://localhost:8000/api/v1"
./test-docker-image.sh

# Terminal 3: Test integration
curl http://localhost:8080
# Open browser: http://localhost:8080
```

## Cleanup

After testing:

```bash
# Stop and remove test containers
docker stop kronos-backend-test kronos-frontend-test
docker rm kronos-backend-test kronos-frontend-test

# Remove test images (optional)
docker rmi kronos-eam-backend-test kronos-eam-frontend-test
```

## CI/CD Integration

You can add these tests to your CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Test Backend Docker Image
  run: |
    cd backend
    ./test-docker-image.sh

- name: Test Frontend Docker Image
  run: |
    cd frontend
    export API_URL="http://localhost:8000/api/v1"
    ./test-docker-image.sh
```

## Next Steps

After successful local tests:

1. ✅ Verify images work locally
2. ✅ Deploy to GCP: `./deploy/gcp-deploy-consolidated.sh`
3. ✅ Monitor Cloud Build logs
4. ✅ Verify deployment in GCP Console

---

**Last Updated**: January 2025

