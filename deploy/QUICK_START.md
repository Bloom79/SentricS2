# Quick Start - GCP Deployment

## Current Directory Issue

If you're in `~/sentrics/deploy`, you need to navigate to the consolidated project:

```bash
cd ~/sentrics/kronos-eam-consolidated/deploy
```

## Deployment Commands

### Step 1: Set Project ID
```bash
export GCP_PROJECT_ID="kronos-eam-consolidated-$(date +%Y%m%d)"
echo "Project ID: $GCP_PROJECT_ID"
```

### Step 2: Setup GCP Infrastructure
```bash
./gcp-setup-consolidated.sh
```

Answer 'y' to prompts to create the project and infrastructure.

### Step 3: Deploy Application
```bash
./gcp-deploy-consolidated.sh
```

Select option `3` to deploy both backend and frontend.

## All Available Scripts

- `gcp-setup-consolidated.sh` - Creates new GCP project and infrastructure
- `gcp-upload-dumps-consolidated.sh` - Uploads database dumps to GCS
- `gcp-init-db-consolidated.sh` - Initializes Cloud SQL database
- `gcp-deploy-consolidated.sh` - Deploys backend and frontend
- `DEPLOY_NOW.sh` - One-command deployment (if you have everything ready)

## Verify Scripts Exist

```bash
cd ~/sentrics/kronos-eam-consolidated/deploy
ls -la *.sh
```

You should see all the deployment scripts listed.
