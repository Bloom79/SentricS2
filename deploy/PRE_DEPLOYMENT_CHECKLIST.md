# Pre-Deployment Checklist

Test Docker images locally before deploying to GCP to avoid errors during deployment.

## Quick Test (Recommended)

```bash
cd kronos-eam-consolidated
./test-docker-builds.sh
```

This tests both backend and frontend images.

## Step-by-Step Testing

### 1. Test Backend Image

```bash
cd backend

# With local database (optional)
export DATABASE_URL="postgresql://user:pass@localhost/kronos_eam"
./test-docker-image.sh

# Without database (build test only)
./test-docker-image.sh
```

**Expected:**
- ✅ Image builds successfully
- ✅ Container starts
- ✅ Health endpoint: `http://localhost:8000/health` returns `{"status": "healthy"}`
- ✅ API docs: `http://localhost:8000/docs` accessible
- ✅ No critical errors in logs

### 2. Test Frontend Image

```bash
cd frontend

# Set backend API URL (if backend is running)
export API_URL="http://localhost:8000/api/v1"
./test-docker-image.sh
```

**Expected:**
- ✅ Image builds successfully
- ✅ Container starts
- ✅ Frontend accessible: `http://localhost:8080`
- ✅ Static files served correctly
- ✅ No build errors

### 3. Integration Test

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

## Common Issues & Fixes

### Backend Build Fails

**Issue**: `ModuleNotFoundError`
- **Fix**: Check `requirements.txt` is complete
- **Fix**: Verify Python 3.11 is used

**Issue**: Database connection errors
- **Note**: OK for build testing, database not required
- **Fix**: For full testing, ensure database is running

### Frontend Build Fails

**Issue**: `npm ci` fails
- **Fix**: Run `npm install` locally first
- **Fix**: Check `package-lock.json` is up to date

**Issue**: TypeScript errors
- **Fix**: Run `npm run build` locally to see errors
- **Fix**: Fix TypeScript errors before testing Docker build

**Issue**: API URL not embedded
- **Fix**: Check `REACT_APP_API_URL` is set during build
- **Fix**: Verify `vite.config.ts` uses environment variables

### Container Won't Start

**Issue**: Port already in use
- **Fix**: `docker stop kronos-backend-test kronos-frontend-test`
- **Fix**: Change ports in test scripts

**Issue**: Health check fails
- **Fix**: Check logs: `docker logs kronos-backend-test`
- **Fix**: Verify application starts correctly

## Pre-Deployment Checklist

Before running `gcp-deploy-consolidated.sh`:

- [ ] **Backend Image**
  - [ ] Builds without errors
  - [ ] Container starts successfully
  - [ ] Health endpoint responds
  - [ ] API endpoints work
  - [ ] No critical errors in logs

- [ ] **Frontend Image**
  - [ ] Builds without errors
  - [ ] Container starts successfully
  - [ ] Serves static files
  - [ ] React app loads correctly
  - [ ] API URL is correctly embedded

- [ ] **Integration**
  - [ ] Frontend can reach backend API
  - [ ] Authentication flow works (if testing)
  - [ ] No CORS errors

- [ ] **Image Size**
  - [ ] Backend image < 1GB
  - [ ] Frontend image < 500MB

## Cleanup After Testing

```bash
# Stop test containers
docker stop kronos-backend-test kronos-frontend-test
docker rm kronos-backend-test kronos-frontend-test

# Remove test images (optional)
docker rmi kronos-eam-backend-test kronos-eam-frontend-test
```

## Next Steps

After successful local tests:

1. ✅ Verify all tests pass
2. ✅ Review image sizes
3. ✅ Deploy to GCP: `./gcp-deploy-consolidated.sh`
4. ✅ Monitor Cloud Build logs
5. ✅ Verify deployment in GCP Console

---

**Remember**: Testing locally saves time during GCP deployment!

