# Authentication Fix for GCP Deployment

## Problem
You're authenticated as a service account (`kronos-deploy@...`) which cannot create projects. You need to authenticate as a user account.

## Solution

### Option 1: Authenticate as User Account (Recommended)

```bash
# List current accounts
gcloud auth list

# Authenticate as your user account
gcloud auth login

# Set the user account as active
gcloud config set account YOUR_EMAIL@gmail.com

# Verify
gcloud auth list
```

### Option 2: Use Application Default Credentials

```bash
# Login with application default credentials
gcloud auth application-default login

# Verify
gcloud auth list
```

### Option 3: Use Service Account Key (if you have admin access)

If you have a service account key file with project creation permissions:

```bash
gcloud auth activate-service-account --key-file=/path/to/key.json
```

## After Authentication

Once authenticated as a user account with proper permissions:

```bash
cd ~/sentrics/kronos-eam-consolidated/deploy
export GCP_PROJECT_ID="kronos-eam-$(date +%y%m%d)"
./gcp-setup-consolidated.sh
```

## Required Permissions

Your user account needs these permissions:
- `resourcemanager.projects.create` - To create projects
- `billing.accounts.get` - To check billing
- `billing.accounts.list` - To list billing accounts
- `serviceusage.services.enable` - To enable APIs
- And other standard GCP permissions

## Verify Permissions

```bash
# Check if you can create projects
gcloud projects create test-project-$(date +%s) --name="Test Project"
# (Delete it immediately if it works)
```

