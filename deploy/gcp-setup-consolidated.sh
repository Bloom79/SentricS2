#!/bin/bash
#
# Google Cloud Platform Setup Script for Kronos EAM Consolidated
# Creates a NEW dedicated project for the consolidated version
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - NEW project for consolidated version
# GCP project IDs must be 6-30 characters, lowercase letters, digits, or hyphens
PROJECT_ID=${GCP_PROJECT_ID:-"kronos-eam-$(date +%y%m%d)"}
REGION=${GCP_REGION:-"europe-west1"}
ZONE=${GCP_ZONE:-"europe-west1-b"}
SQL_INSTANCE_NAME="kronos-db"
SQL_DATABASE_NAME="kronos_eam"
SQL_USER="kronos"
BACKEND_SERVICE_NAME="kronos-eam-api"
FRONTEND_SERVICE_NAME="kronos-eam-frontend"
BUCKET_NAME="${PROJECT_ID}-storage"
DB_INIT_BUCKET="${PROJECT_ID}-db-init"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Kronos EAM Consolidated - GCP Setup${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${YELLOW}This will create a NEW GCP project: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
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

# 1. Create or use project
echo -e "\n${YELLOW}Step 1: Creating/Using GCP project${NC}"
echo "Project ID: ${PROJECT_ID}"

# Check if project exists
if gcloud projects describe ${PROJECT_ID} &>/dev/null; then
    echo -e "${GREEN}Project ${PROJECT_ID} already exists${NC}"
    confirm "Do you want to use this existing project?"
else
    confirm "Create new project ${PROJECT_ID}?"
    echo "Creating project..."
    gcloud projects create ${PROJECT_ID} --name="Kronos EAM Consolidated" || {
        echo -e "${RED}Failed to create project. It may already exist or name is taken.${NC}"
        echo "Try setting a different PROJECT_ID:"
        echo "  export GCP_PROJECT_ID='kronos-eam-consolidated-$(date +%Y%m%d)'"
        exit 1
    }
    echo -e "${GREEN}Project created${NC}"
fi

gcloud config set project ${PROJECT_ID}
echo -e "${GREEN}Project set to ${PROJECT_ID}${NC}"

# 2. Enable billing (required for Cloud SQL)
echo -e "\n${YELLOW}Step 2: Billing${NC}"
# Skip billing check - user should have linked it manually
echo -e "${YELLOW}⚠️  Billing check skipped.${NC}"
echo "Please ensure billing is linked at: https://console.cloud.google.com/billing?project=${PROJECT_ID}"
echo -e "${GREEN}Continuing with setup...${NC}"
echo ""

# 3. Enable required APIs
echo -e "\n${YELLOW}Step 3: Enabling required APIs${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    sqladmin.googleapis.com \
    compute.googleapis.com \
    secretmanager.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    storage.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    --project=${PROJECT_ID} || {
    echo -e "${RED}Failed to enable APIs. Check your permissions.${NC}"
    exit 1
}
echo -e "${GREEN}APIs enabled${NC}"

# 4. Create service accounts
echo -e "\n${YELLOW}Step 4: Creating service accounts${NC}"

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
    --condition=None --quiet

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:kronos-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None --quiet

echo -e "${GREEN}Service account permissions granted${NC}"

# 5. Create Cloud SQL instance
echo -e "\n${YELLOW}Step 5: Creating Cloud SQL instance${NC}"
if ! gcloud sql instances describe ${SQL_INSTANCE_NAME} &>/dev/null; then
    confirm "Create Cloud SQL instance ${SQL_INSTANCE_NAME}? (This will incur costs ~$10-15/month)"
    
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
    
    # Create user with the same password
    gcloud sql users create ${SQL_USER} \
        --instance=${SQL_INSTANCE_NAME} \
        --password=${DB_PASSWORD} \
        --project=${PROJECT_ID}
    
    echo -e "${GREEN}Database and user created${NC}"
    
    # Store password temporarily for secret creation
    echo "${DB_PASSWORD}" > /tmp/db_password_${PROJECT_ID}.txt
    chmod 600 /tmp/db_password_${PROJECT_ID}.txt
else
    echo -e "${YELLOW}Cloud SQL instance already exists${NC}"
    # If instance exists but password file doesn't, we'll generate a new password
    if [ ! -f "/tmp/db_password_${PROJECT_ID}.txt" ]; then
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        echo -e "${YELLOW}Resetting database user password...${NC}"
        gcloud sql users set-password ${SQL_USER} \
            --instance=${SQL_INSTANCE_NAME} \
            --password=${DB_PASSWORD} \
            --project=${PROJECT_ID} || true
        echo "${DB_PASSWORD}" > /tmp/db_password_${PROJECT_ID}.txt
        chmod 600 /tmp/db_password_${PROJECT_ID}.txt
    else
        DB_PASSWORD=$(cat /tmp/db_password_${PROJECT_ID}.txt)
    fi
fi

# 6. Create secrets in Secret Manager
echo -e "\n${YELLOW}Step 6: Setting up secrets${NC}"

# Get SQL connection name
SQL_CONNECTION_NAME=$(gcloud sql instances describe ${SQL_INSTANCE_NAME} --format="value(connectionName)")

# Generate secrets if they don't exist
if ! gcloud secrets describe database-url --project=${PROJECT_ID} &>/dev/null; then
    # Use stored password or generate new one
    if [ -f "/tmp/db_password_${PROJECT_ID}.txt" ]; then
        DB_PASSWORD=$(cat /tmp/db_password_${PROJECT_ID}.txt)
    else
        # Generate new password and update user
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        echo -e "${YELLOW}Setting database user password...${NC}"
        gcloud sql users set-password ${SQL_USER} \
            --instance=${SQL_INSTANCE_NAME} \
            --password=${DB_PASSWORD} \
            --project=${PROJECT_ID} || true
        echo "${DB_PASSWORD}" > /tmp/db_password_${PROJECT_ID}.txt
        chmod 600 /tmp/db_password_${PROJECT_ID}.txt
    fi
    
    DATABASE_URL="postgresql://${SQL_USER}:${DB_PASSWORD}@/${SQL_DATABASE_NAME}?host=/cloudsql/${SQL_CONNECTION_NAME}"
    
    echo -n "${DATABASE_URL}" | gcloud secrets create database-url \
        --data-file=- \
        --project=${PROJECT_ID} || true
    
    echo -e "${GREEN}Created database-url secret${NC}"
else
    echo -e "${YELLOW}database-url secret already exists${NC}"
    # Verify the secret has a password, if not update it
    EXISTING_URL=$(gcloud secrets versions access latest --secret=database-url --project=${PROJECT_ID})
    if [[ "$EXISTING_URL" == *":@"* ]] || [[ "$EXISTING_URL" == *":@/"* ]]; then
        echo -e "${YELLOW}⚠️  Secret missing password, updating...${NC}"
        if [ -f "/tmp/db_password_${PROJECT_ID}.txt" ]; then
            DB_PASSWORD=$(cat /tmp/db_password_${PROJECT_ID}.txt)
        else
            DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
            gcloud sql users set-password ${SQL_USER} \
                --instance=${SQL_INSTANCE_NAME} \
                --password=${DB_PASSWORD} \
                --project=${PROJECT_ID} || true
        fi
        DATABASE_URL="postgresql://${SQL_USER}:${DB_PASSWORD}@/${SQL_DATABASE_NAME}?host=/cloudsql/${SQL_CONNECTION_NAME}"
        echo -n "${DATABASE_URL}" | gcloud secrets versions add database-url --data-file=- --project=${PROJECT_ID}
        echo -e "${GREEN}Updated database-url secret with password${NC}"
    fi
fi

# Clean up password file
rm -f /tmp/db_password_${PROJECT_ID}.txt

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

# 7. Create Artifact Registry repository
echo -e "\n${YELLOW}Step 7: Creating Artifact Registry repository${NC}"
if ! gcloud artifacts repositories describe kronos-eam --location=${REGION} --project=${PROJECT_ID} &>/dev/null; then
    gcloud artifacts repositories create kronos-eam \
        --repository-format=docker \
        --location=${REGION} \
        --description="Kronos EAM Consolidated Docker images" \
        --project=${PROJECT_ID} || {
        echo -e "${YELLOW}Repository may already exist${NC}"
    }
    echo -e "${GREEN}Artifact Registry repository created${NC}"
else
    echo -e "${YELLOW}Artifact Registry repository already exists${NC}"
fi

# 8. Create Cloud Storage buckets
echo -e "\n${YELLOW}Step 8: Creating Cloud Storage buckets${NC}"

# DB init bucket
if ! gsutil ls -b gs://${DB_INIT_BUCKET} &>/dev/null; then
    gsutil mb -l ${REGION} gs://${DB_INIT_BUCKET}
    echo -e "${GREEN}Created bucket: ${DB_INIT_BUCKET}${NC}"
else
    echo -e "${YELLOW}Bucket ${DB_INIT_BUCKET} already exists${NC}"
fi

# Storage bucket
if ! gsutil ls -b gs://${BUCKET_NAME} &>/dev/null; then
    gsutil mb -l ${REGION} gs://${BUCKET_NAME}
    echo -e "${GREEN}Created bucket: ${BUCKET_NAME}${NC}"
else
    echo -e "${YELLOW}Bucket ${BUCKET_NAME} already exists${NC}"
fi

# 9. Configure Cloud Build
echo -e "\n${YELLOW}Step 9: Configuring Cloud Build${NC}"
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin" \
    --condition=None --quiet

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None --quiet

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/storage.admin" \
    --condition=None --quiet

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/cloudsql.admin" \
    --condition=None --quiet

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
echo "Database: ${SQL_DATABASE_NAME}"
echo ""
echo "Next steps:"
echo "  1. Export project ID: export GCP_PROJECT_ID='${PROJECT_ID}'"
echo "  2. Generate dumps: cd backend && python scripts/dump_all.py"
echo "  3. Upload dumps: cd deploy && ./gcp-upload-dumps.sh"
echo "  4. Deploy: ./gcp-deploy.sh"
echo ""

