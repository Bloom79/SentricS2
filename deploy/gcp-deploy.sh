#!/bin/bash
#
# GCP Deployment Script for Kronos EAM Consolidated
# This script deploys both backend and frontend to Google Cloud Platform
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Update these for your project
PROJECT_ID=${GCP_PROJECT_ID:-"kronos-eam-prod-20250802"}
REGION=${GCP_REGION:-"europe-west1"}
ZONE=${GCP_ZONE:-"europe-west1-b"}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Kronos EAM - GCP Deployment${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}Not logged in to GCP. Please authenticate:${NC}"
    gcloud auth login
fi

# Set project
echo -e "${YELLOW}Setting GCP project to: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID} || {
    echo -e "${RED}Failed to set project. Please check your project ID.${NC}"
    exit 1
}

# Get the API URL from Cloud Run (if backend is already deployed)
API_URL=""
if gcloud run services describe kronos-eam-api --region=${REGION} --format="value(status.url)" &>/dev/null; then
    API_URL=$(gcloud run services describe kronos-eam-api --region=${REGION} --format="value(status.url)")/api/v1
    echo -e "${GREEN}Found existing backend API: ${API_URL}${NC}"
else
    echo -e "${YELLOW}Backend not deployed yet. Will use placeholder API URL.${NC}"
    API_URL="https://kronos-eam-api-xxxxx.a.run.app/api/v1"
fi

# Function to build and deploy backend
deploy_backend() {
    echo -e "\n${BLUE}=== Deploying Backend ===${NC}"
    
    cd backend
    
    # Get Cloud SQL instance connection name
    SQL_INSTANCE=$(gcloud sql instances describe kronos-db --format="value(connectionName)" 2>/dev/null || echo "")
    
    if [ -z "$SQL_INSTANCE" ]; then
        echo -e "${YELLOW}Warning: Cloud SQL instance 'kronos-db' not found.${NC}"
        echo "Please create it first or update the connection name in cloudbuild.yaml"
        SQL_INSTANCE="${PROJECT_ID}:${REGION}:kronos-db"
    fi
    
    # Build and submit build
    echo -e "${YELLOW}Submitting Cloud Build job for backend...${NC}"
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions=_REGION=${REGION},_CLOUD_SQL_INSTANCE=${SQL_INSTANCE} \
        . || {
        echo -e "${RED}Backend deployment failed${NC}"
        cd ..
        return 1
    }
    
    cd ..
    
    # Get the new API URL
    sleep 5
    API_URL=$(gcloud run services describe kronos-eam-api --region=${REGION} --format="value(status.url)")/api/v1
    echo -e "${GREEN}Backend deployed successfully!${NC}"
    echo -e "${GREEN}API URL: ${API_URL}${NC}"
}

# Function to build and deploy frontend
deploy_frontend() {
    echo -e "\n${BLUE}=== Deploying Frontend ===${NC}"
    
    cd frontend
    
    # Update API URL in cloudbuild.yaml if backend is deployed
    if [ -n "$API_URL" ] && [ "$API_URL" != "https://kronos-eam-api-xxxxx.a.run.app/api/v1" ]; then
        echo -e "${YELLOW}Using API URL: ${API_URL}${NC}"
    fi
    
    # Build and submit build
    echo -e "${YELLOW}Submitting Cloud Build job for frontend...${NC}"
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions=_REGION=${REGION},_API_URL=${API_URL} \
        . || {
        echo -e "${RED}Frontend deployment failed${NC}"
        cd ..
        return 1
    }
    
    cd ..
    
    FRONTEND_URL=$(gcloud run services describe kronos-eam-frontend --region=${REGION} --format="value(status.url)")
    echo -e "${GREEN}Frontend deployed successfully!${NC}"
    echo -e "${GREEN}Frontend URL: ${FRONTEND_URL}${NC}"
}

# Main deployment flow
echo -e "${YELLOW}What would you like to deploy?${NC}"
echo "1) Backend only"
echo "2) Frontend only"
echo "3) Both (Backend first, then Frontend)"
read -p "Enter choice [1-3]: " choice

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
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Backend API: ${API_URL}"
if [ -n "$FRONTEND_URL" ]; then
    echo "Frontend: ${FRONTEND_URL}"
fi

