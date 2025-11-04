#!/bin/bash
#
# Google Cloud Platform Setup Script for Kronos EAM Consolidated
# This script sets up all necessary GCP resources from scratch
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"kronos-eam-prod-20250802"}
REGION=${GCP_REGION:-"europe-west1"}
ZONE=${GCP_ZONE:-"europe-west1-b"}
SQL_INSTANCE_NAME="kronos-db"
SQL_DATABASE_NAME="kronos_eam"
SQL_USER="kronos"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Kronos EAM - GCP Infrastructure Setup${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Function to check if user wants to proceed
confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Setup cancelled.${NC}"
        exit 1
    fi
}

# 1. Authenticate and set project
echo -e "\n${YELLOW}Step 1: Setting up GCP project${NC}"
echo "Current project: $(gcloud config get-value project 2>/dev/null || echo 'None')"
confirm "Do you want to use project ${PROJECT_ID}?"

# Check if project exists
if ! gcloud projects describe ${PROJECT_ID} &>/dev/null; then
    echo -e "${YELLOW}Project ${PROJECT_ID} does not exist.${NC}"
    confirm "Do you want to create it?"
    gcloud projects create ${PROJECT_ID} --name="Kronos EAM Production"
    echo -e "${GREEN}Project created${NC}"
fi

gcloud config set project ${PROJECT_ID}
echo -e "${GREEN}Project set to ${PROJECT_ID}${NC}"

# 2. Enable required APIs
echo -e "\n${YELLOW}Step 2: Enabling required APIs${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    sqladmin.googleapis.com \
    compute.googleapis.com \
    secretmanager.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    --project=${PROJECT_ID} || {
    echo -e "${RED}Failed to enable APIs. Check your permissions.${NC}"
    exit 1
}
echo -e "${GREEN}APIs enabled${NC}"

# 3. Create service accounts
echo -e "\n${YELLOW}Step 3: Creating service accounts${NC}"

# Backend service account
if ! gcloud iam service-accounts describe kronos-backend@${PROJECT_ID}.iam.gserviceaccount.com &>/dev/null; then
    gcloud iam service-accounts create kronos-backend \
        --display-name="Kronos EAM Backend Service Account" \
        --project=${PROJECT_ID}
    echo -e "${GREEN}Created backend service account${NC}"
else
    echo -e "${YELLOW}Backend service account already exists${NC}"
fi

# Grant permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:kronos-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:kronos-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

echo -e "${GREEN}Service account permissions granted${NC}"

# 4. Create Cloud SQL instance
echo -e "\n${YELLOW}Step 4: Creating Cloud SQL instance${NC}"
if ! gcloud sql instances describe ${SQL_INSTANCE_NAME} &>/dev/null; then
    confirm "Create Cloud SQL instance ${SQL_INSTANCE_NAME}? (This will incur costs)"
    
    # Generate random password
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    gcloud sql instances create ${SQL_INSTANCE_NAME} \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=${REGION} \
        --root-password=${DB_PASSWORD} \
        --storage-type=SSD \
        --storage-size=10GB \
        --backup-start-time=03:00 \
        --enable-bin-log \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=4 \
        --deletion-protection \
        --project=${PROJECT_ID} || {
        echo -e "${RED}Failed to create SQL instance${NC}"
        exit 1
    }
    
    echo -e "${GREEN}Cloud SQL instance created${NC}"
    echo -e "${YELLOW}Root password: ${DB_PASSWORD}${NC}"
    echo -e "${YELLOW}Save this password securely!${NC}"
    
    # Create database
    gcloud sql databases create ${SQL_DATABASE_NAME} \
        --instance=${SQL_INSTANCE_NAME} \
        --project=${PROJECT_ID}
    
    # Create user
    gcloud sql users create ${SQL_USER} \
        --instance=${SQL_INSTANCE_NAME} \
        --password=${DB_PASSWORD} \
        --project=${PROJECT_ID}
    
    echo -e "${GREEN}Database and user created${NC}"
else
    echo -e "${YELLOW}Cloud SQL instance already exists${NC}"
fi

# 5. Create secrets in Secret Manager
echo -e "\n${YELLOW}Step 5: Setting up secrets${NC}"

# Get SQL connection name
SQL_CONNECTION_NAME=$(gcloud sql instances describe ${SQL_INSTANCE_NAME} --format="value(connectionName)")

# Generate secrets if they don't exist
if ! gcloud secrets describe database-url --project=${PROJECT_ID} &>/dev/null; then
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    DATABASE_URL="postgresql://${SQL_USER}:${DB_PASSWORD}@/${SQL_DATABASE_NAME}?host=/cloudsql/${SQL_CONNECTION_NAME}"
    
    echo -n "${DATABASE_URL}" | gcloud secrets create database-url \
        --data-file=- \
        --project=${PROJECT_ID} || true
    
    echo -e "${GREEN}Created database-url secret${NC}"
else
    echo -e "${YELLOW}database-url secret already exists${NC}"
fi

if ! gcloud secrets describe jwt-secret --project=${PROJECT_ID} &>/dev/null; then
    JWT_SECRET=$(openssl rand -base64 64)
    echo -n "${JWT_SECRET}" | gcloud secrets create jwt-secret \
        --data-file=- \
        --project=${PROJECT_ID} || true
    
    echo -e "${GREEN}Created jwt-secret${NC}"
else
    echo -e "${YELLOW}jwt-secret already exists${NC}"
fi

if ! gcloud secrets describe redis-url --project=${PROJECT_ID} &>/dev/null; then
    echo -n "redis://localhost:6379/0" | gcloud secrets create redis-url \
        --data-file=- \
        --project=${PROJECT_ID} || true
    
    echo -e "${GREEN}Created redis-url secret${NC}"
else
    echo -e "${YELLOW}redis-url secret already exists${NC}"
fi

# 6. Create Artifact Registry repository
echo -e "\n${YELLOW}Step 6: Creating Artifact Registry repository${NC}"
if ! gcloud artifacts repositories describe kronos-eam --location=${REGION} --project=${PROJECT_ID} &>/dev/null; then
    gcloud artifacts repositories create kronos-eam \
        --repository-format=docker \
        --location=${REGION} \
        --description="Kronos EAM Docker images" \
        --project=${PROJECT_ID} || {
        echo -e "${YELLOW}Repository may already exist${NC}"
    }
    echo -e "${GREEN}Artifact Registry repository created${NC}"
else
    echo -e "${YELLOW}Artifact Registry repository already exists${NC}"
fi

# 7. Configure Cloud Build
echo -e "\n${YELLOW}Step 7: Configuring Cloud Build${NC}"
# Grant Cloud Build service account necessary permissions
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

echo -e "${GREEN}Cloud Build configured${NC}"

# Summary
echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "SQL Instance: ${SQL_INSTANCE_NAME}"
echo "SQL Connection: ${SQL_CONNECTION_NAME}"
echo ""
echo "Next steps:"
echo "1. Update cloudbuild.yaml files with your SQL connection name"
echo "2. Run: ./deploy/gcp-deploy.sh"
echo ""

