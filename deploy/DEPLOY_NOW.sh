#!/bin/bash
#
# Quick Deployment Script
# Deploys Kronos EAM Consolidated to GCP
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID=${GCP_PROJECT_ID:-"kronos-eam-$(date +%y%m%d)"}
REGION=${GCP_REGION:-"europe-west1"}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Kronos EAM Consolidated - Quick Deploy${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${YELLOW}Project: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo ""

# Check prerequisites
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Set project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID} 2>/dev/null || {
    echo -e "${YELLOW}Project ${PROJECT_ID} doesn't exist. Creating it...${NC}"
    echo "Run: cd ${SCRIPT_DIR} && ./gcp-setup-consolidated.sh"
    echo "Or set an existing project: export GCP_PROJECT_ID='your-project-id'"
    exit 1
}

echo -e "${GREEN}✓ Project set${NC}"

# Step 1: Setup (if needed)
echo -e "\n${BLUE}Step 1: Checking GCP infrastructure...${NC}"
if ! gcloud sql instances describe kronos-db --project=${PROJECT_ID} &>/dev/null; then
    echo -e "${YELLOW}Infrastructure not set up. Running setup...${NC}"
    ${SCRIPT_DIR}/gcp-setup-consolidated.sh
else
    echo -e "${GREEN}✓ Infrastructure exists${NC}"
fi

# Step 2: Generate and upload dumps (if local DB available)
echo -e "\n${BLUE}Step 2: Database dumps...${NC}"
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == *"localhost"* ]]; then
    echo -e "${YELLOW}Found local DATABASE_URL. Generating dumps...${NC}"
    cd "${SCRIPT_DIR}/../backend"
    python scripts/dump_all.py || echo "Dump generation failed or skipped"
    cd "${SCRIPT_DIR}"
    ./gcp-upload-dumps-consolidated.sh || echo "Upload failed or skipped"
else
    echo -e "${YELLOW}No local DATABASE_URL found. Skipping dump generation.${NC}"
    echo "Set DATABASE_URL to generate dumps from local database"
fi

# Step 3: Initialize database
echo -e "\n${BLUE}Step 3: Database initialization...${NC}"
${SCRIPT_DIR}/gcp-init-db-consolidated.sh || echo "DB initialization failed or skipped"

# Step 4: Deploy
echo -e "\n${BLUE}Step 4: Deploying application...${NC}"
echo -e "${YELLOW}Deploying backend and frontend...${NC}"
${SCRIPT_DIR}/gcp-deploy-consolidated.sh <<EOF
3
EOF

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Seed authenticated data:"
echo "     cd backend"
echo "     python scripts/seed_authenticated_data.py \\"
echo "       --user-email 'admin@yourcompany.com' \\"
echo "       --user-name 'Admin User' \\"
echo "       --user-password 'SecurePassword123!'"
echo ""
echo "  2. Get service URLs:"
echo "     gcloud run services list --project=${PROJECT_ID}"
echo ""

