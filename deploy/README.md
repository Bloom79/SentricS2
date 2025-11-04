# Kronos EAM - GCP Deployment

This directory contains all scripts and configuration files for deploying Kronos EAM to Google Cloud Platform.

## Quick Start

### 1. Initial Setup (One-time)

```bash
cd deploy
export GCP_PROJECT_ID="kronos-eam-prod-20250802"  # Or your project ID
./gcp-setup.sh
```

### 2. Deploy Application

```bash
./gcp-deploy.sh
```

Select option 3 to deploy both backend and frontend.

## Files

- **`gcp-setup.sh`** - One-time infrastructure setup (Cloud SQL, service accounts, secrets)
- **`gcp-deploy.sh`** - Deploy backend and/or frontend to Cloud Run
- **`DEPLOYMENT_GUIDE.md`** - Comprehensive deployment documentation

## Project Structure

```
kronos-eam-consolidated/
├── backend/
│   ├── Dockerfile           # Backend container image
│   └── cloudbuild.yaml      # Cloud Build configuration
├── frontend/
│   ├── Dockerfile           # Frontend container image
│   ├── nginx.conf          # Nginx configuration
│   └── cloudbuild.yaml     # Cloud Build configuration
└── deploy/
    ├── gcp-setup.sh        # Infrastructure setup
    ├── gcp-deploy.sh       # Deployment script
    └── DEPLOYMENT_GUIDE.md  # Full documentation
```

## Prerequisites

1. Google Cloud Account with billing enabled
2. `gcloud` CLI installed and authenticated
3. Access to the GCP project

## Configuration

Update these variables in the scripts or export them:

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="europe-west1"
export GCP_ZONE="europe-west1-b"
```

## More Information

See [`DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md) for detailed instructions, troubleshooting, and best practices.

