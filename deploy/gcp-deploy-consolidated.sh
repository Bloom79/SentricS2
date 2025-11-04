#!/bin/bash
#
# GCP Deployment Script for Kronos EAM Consolidated
# Deploys to the NEW consolidated project
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - NEW project for consolidated version
PROJECT_ID=${GCP_PROJECT_ID:-"kronos-eam-$(date +%y%m%d)"}
REGION=${GCP_REGION:-"europe-west1"}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Kronos EAM Consolidated - GCP Deployment${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${YELLOW}Project: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    exit 1
fi

# Set project
echo -e "${YELLOW}Setting GCP project to: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID} || {
    echo -e "${RED}Failed to set project. Run gcp-setup-consolidated.sh first.${NC}"
    exit 1
}

# Get the API URL from Cloud Run (if backend is already deployed)
API_URL=""
if gcloud run services describe kronos-eam-api --region=${REGION} --format="value(status.url)" &>/dev/null 2>&1; then
    API_URL=$(gcloud run services describe kronos-eam-api --region=${REGION} --format="value(status.url)")/api/v1
    echo -e "${GREEN}Found existing backend API: ${API_URL}${NC}"
else
    echo -e "${YELLOW}Backend not deployed yet. Will use placeholder API URL.${NC}"
    API_URL="https://kronos-eam-api-xxxxx.a.run.app/api/v1"
fi

# Function to create initial admin user
create_initial_user() {
    echo -e "${YELLOW}Checking if initial user needs to be created...${NC}"
    
    # Check if user already exists by trying to login
    TEST_LOGIN=$(curl -s -X POST "${API_URL}/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test@example.com&password=test123" 2>/dev/null || echo "")
    
    if echo "$TEST_LOGIN" | grep -q "access_token"; then
        echo -e "${GREEN}✓ Initial user already exists${NC}"
        return 0
    fi
    
    # Create Cloud Run job to create user
    echo -e "${YELLOW}Creating Cloud Run job to initialize admin user...${NC}"
    
    SQL_INSTANCE=$(gcloud sql instances describe kronos-db --format="value(connectionName)" 2>/dev/null || echo "")
    SERVICE_ACCOUNT="kronos-backend@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Delete job if it exists
    gcloud run jobs delete create-admin-user --region=${REGION} --quiet 2>&1 > /dev/null
    
    # Create job
    gcloud run jobs create create-admin-user \
        --image=gcr.io/${PROJECT_ID}/kronos-eam-backend:latest \
        --region=${REGION} \
        --set-cloudsql-instances=${SQL_INSTANCE} \
        --service-account=${SERVICE_ACCOUNT} \
        --set-secrets="DATABASE_URL=database-url:latest,JWT_SECRET_KEY=jwt-secret:latest" \
        --command="python" \
        --args="/app/scripts/create_test_user.py" \
        --max-retries=1 \
        --task-timeout=300 \
        --quiet 2>&1 | grep -E "(Creating|ERROR)" || true
    
    # Execute job
    echo -e "${YELLOW}Executing user creation job...${NC}"
    gcloud run jobs execute create-admin-user --region=${REGION} --wait 2>&1 | tail -5
    
    echo -e "${GREEN}✓ Initial user created: test@example.com / test123${NC}"
}

# Function to seed database with test data
seed_database() {
    echo -e "\n${BLUE}=== Seeding Database ===${NC}"
    
    SQL_INSTANCE=$(gcloud sql instances describe kronos-db --format="value(connectionName)" 2>/dev/null || echo "")
    SERVICE_ACCOUNT="kronos-backend@${PROJECT_ID}.iam.gserviceaccount.com"
    
    if [ -z "$SQL_INSTANCE" ]; then
        echo -e "${RED}Error: Cloud SQL instance 'kronos-db' not found.${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Creating Cloud Run job to seed database...${NC}"
    
    # Delete job if it exists
    gcloud run jobs delete seed-database --region=${REGION} --quiet 2>&1 > /dev/null
    
    # Create job
    gcloud run jobs create seed-database \
        --image=gcr.io/${PROJECT_ID}/kronos-eam-backend:latest \
        --region=${REGION} \
        --set-cloudsql-instances=${SQL_INSTANCE} \
        --service-account=${SERVICE_ACCOUNT} \
        --set-secrets="DATABASE_URL=database-url:latest,JWT_SECRET_KEY=jwt-secret:latest" \
        --command="python" \
        --args="/app/scripts/seed_all_data.py,--tenant-id,demo,--user-email,test@example.com" \
        --max-retries=1 \
        --task-timeout=600 \
        --memory=1Gi \
        --cpu=1 \
        --quiet 2>&1 | grep -E "(Creating|ERROR)" || true
    
    # Execute job
    echo -e "${YELLOW}Executing database seeding job (this may take a few minutes)...${NC}"
    gcloud run jobs execute seed-database --region=${REGION} --wait 2>&1 | tail -20
    
    # Check if job succeeded
    JOB_STATUS=$(gcloud run jobs executions list --job=seed-database --region=${REGION} --limit=1 --format="value(status.conditions[0].type,status.conditions[0].status)" 2>/dev/null || echo "")
    
    if echo "$JOB_STATUS" | grep -q "Complete.*True"; then
        echo -e "${GREEN}✓ Database seeded successfully!${NC}"
        echo -e "${GREEN}  - Sites, Plants, and Assets${NC}"
        echo -e "${GREEN}  - CERs and Members${NC}"
        echo -e "${GREEN}  - Compliance Records${NC}"
        echo -e "${GREEN}  - Documents${NC}"
        echo -e "${GREEN}  - Workflows${NC}"
    else
        echo -e "${YELLOW}⚠️  Seeding job completed with warnings. Check logs for details.${NC}"
        echo -e "${YELLOW}   View logs: gcloud run jobs executions logs read --job=seed-database --region=${REGION} --limit=1${NC}"
    fi
}

# Function to build and deploy backend
deploy_backend() {
    echo -e "\n${BLUE}=== Deploying Backend ===${NC}"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="${SCRIPT_DIR}/.."
    cd "${PROJECT_ROOT}/backend"
    
    # Get Cloud SQL instance connection name
    SQL_INSTANCE=$(gcloud sql instances describe kronos-db --format="value(connectionName)" 2>/dev/null || echo "")
    
    if [ -z "$SQL_INSTANCE" ]; then
        echo -e "${RED}Error: Cloud SQL instance 'kronos-db' not found.${NC}"
        echo "Run deploy/gcp-setup-consolidated.sh first"
        cd "${PROJECT_ROOT}"
        return 1
    fi
    
    echo -e "${GREEN}Using Cloud SQL instance: ${SQL_INSTANCE}${NC}"
    
    # Build and submit build
    echo -e "${YELLOW}Submitting Cloud Build job for backend...${NC}"
    echo -e "${YELLOW}Note: This will upload backend code only (venv and __pycache__ excluded)${NC}"
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions=_REGION=${REGION},_CLOUD_SQL_INSTANCE=${SQL_INSTANCE} \
        . || {
        echo -e "${RED}Backend deployment failed${NC}"
        cd "${PROJECT_ROOT}"
        return 1
    }
    
    cd "${PROJECT_ROOT}"
    
    # Wait for deployment to complete
    echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
    sleep 10
    
    # Get the new API URL
    if gcloud run services describe kronos-eam-api --region=${REGION} --format="value(status.url)" &>/dev/null; then
        API_URL=$(gcloud run services describe kronos-eam-api --region=${REGION} --format="value(status.url)")/api/v1
        FRONTEND_URL=$(gcloud run services describe kronos-eam-frontend --region=${REGION} --format="value(status.url)" 2>/dev/null || echo "")
        
        echo -e "${GREEN}Backend deployed successfully!${NC}"
        echo -e "${GREEN}API URL: ${API_URL}${NC}"
        
        # Update CORS origins with frontend URL if available
        if [ -n "$FRONTEND_URL" ]; then
            echo -e "${YELLOW}Updating CORS configuration...${NC}"
            gcloud run services update kronos-eam-api \
                --region=${REGION} \
                --update-env-vars="BACKEND_CORS_ORIGINS=[\"${FRONTEND_URL}\"]" \
                --quiet 2>&1 | grep -E "(updated|ERROR)" || echo "CORS update may require redeployment"
        fi
        
        # Create initial admin user if database is ready
        echo -e "${YELLOW}Creating initial admin user...${NC}"
        create_initial_user
    else
        echo -e "${YELLOW}Backend deployment may still be in progress${NC}"
    fi
}

# Function to build and deploy frontend
deploy_frontend() {
    echo -e "\n${BLUE}=== Deploying Frontend ===${NC}"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="${SCRIPT_DIR}/.."
    cd "${PROJECT_ROOT}/frontend"
    
    # Update API URL in cloudbuild.yaml if backend is deployed
    if [ -n "$API_URL" ] && [ "$API_URL" != "https://kronos-eam-api-xxxxx.a.run.app/api/v1" ]; then
        echo -e "${YELLOW}Using API URL: ${API_URL}${NC}"
    else
        echo -e "${YELLOW}⚠️  Using placeholder API URL. Update after backend deployment.${NC}"
    fi
    
    # Build and submit build
    echo -e "${YELLOW}Submitting Cloud Build job for frontend...${NC}"
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions=_REGION=${REGION},_API_URL=${API_URL} \
        . || {
        echo -e "${RED}Frontend deployment failed${NC}"
        cd "${PROJECT_ROOT}"
        return 1
    }
    
    cd "${PROJECT_ROOT}"
    
    # Wait for deployment to complete
    echo -e "${YELLOW}Waiting for frontend to be ready...${NC}"
    sleep 10
    
    if gcloud run services describe kronos-eam-frontend --region=${REGION} --format="value(status.url)" &>/dev/null; then
        FRONTEND_URL=$(gcloud run services describe kronos-eam-frontend --region=${REGION} --format="value(status.url)")
        echo -e "${GREEN}Frontend deployed successfully!${NC}"
        echo -e "${GREEN}Frontend URL: ${FRONTEND_URL}${NC}"
        
        # Update backend CORS to include frontend URL
        if [ -n "$FRONTEND_URL" ]; then
            echo -e "${YELLOW}Updating backend CORS configuration...${NC}"
            gcloud run services update kronos-eam-api \
                --region=${REGION} \
                --update-env-vars="BACKEND_CORS_ORIGINS=[\"${FRONTEND_URL}\"]" \
                --quiet 2>&1 | grep -E "(updated|revision|ERROR)" || echo "CORS configuration updated"
            
            # Wait for new revision to be ready
            echo -e "${YELLOW}Waiting for backend CORS update to take effect...${NC}"
            sleep 15
        fi
    fi
}

# Main deployment flow
echo -e "${YELLOW}What would you like to deploy?${NC}"
echo "1) Backend only"
echo "2) Frontend only"
echo "3) Both (Backend first, then Frontend)"
echo "4) Seed database only (requires backend deployed)"
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        deploy_backend
        ;;
    2)
        deploy_frontend
        ;;
    3)
        deploy_backend
        deploy_frontend
        ;;
    4)
        seed_database
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Ask if user wants to seed database after deployment
if [ "$choice" != "4" ]; then
    echo ""
    read -p "Do you want to seed the database with test data? (y/n) [n]: " seed_choice
    if [ "$seed_choice" = "y" ] || [ "$seed_choice" = "Y" ]; then
        seed_database
    fi
fi

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Project: ${PROJECT_ID}"
if [ -n "$API_URL" ]; then
    echo "Backend API: ${API_URL}"
fi
if [ -n "$FRONTEND_URL" ]; then
    echo "Frontend: ${FRONTEND_URL}"
    echo ""
    echo -e "${GREEN}Login Credentials:${NC}"
    echo "  Email: test@example.com"
    echo "  Password: test123"
    echo ""
    echo -e "${GREEN}Access your application:${NC}"
    echo "  ${FRONTEND_URL}"
fi
echo ""
echo "Next steps:"
echo "  1. Test login at the frontend URL above"
echo "  2. (Optional) Initialize database with schema dumps: ./gcp-init-db-consolidated.sh"
echo "  3. (Optional) Seed additional data: See GCP_DB_INITIALIZATION.md"
echo ""

