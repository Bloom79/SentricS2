#!/bin/bash
#
# Upload database dumps to Cloud Storage for consolidated project
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration - NEW project
PROJECT_ID=${GCP_PROJECT_ID:-"kronos-eam-$(date +%y%m%d)"}
REGION=${GCP_REGION:-"europe-west1"}
BUCKET_NAME="${PROJECT_ID}-db-init"
DUMP_DIR=${DUMP_DIR:-"./dumps"}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Upload Database Dumps to GCP${NC}"
echo -e "${BLUE}Project: ${PROJECT_ID}${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    exit 1
fi

# Set project
gcloud config set project ${PROJECT_ID} || {
    echo -e "${RED}Failed to set project${NC}"
    exit 1
}

# Create bucket if it doesn't exist
echo -e "${YELLOW}Checking Cloud Storage bucket...${NC}"
if ! gsutil ls -b gs://${BUCKET_NAME} &>/dev/null; then
    echo "Creating bucket: ${BUCKET_NAME}"
    gsutil mb -l ${REGION} gs://${BUCKET_NAME}
    echo -e "${GREEN}Bucket created${NC}"
else
    echo -e "${GREEN}Bucket exists${NC}"
fi

# Check for dump files
if [ ! -d "$DUMP_DIR" ]; then
    echo -e "${YELLOW}Dump directory not found: ${DUMP_DIR}${NC}"
    echo "Creating dumps from local database..."
    
    if [ -z "$DATABASE_URL" ]; then
        echo -e "${RED}DATABASE_URL not set. Cannot generate dumps.${NC}"
        echo ""
        echo "To generate dumps:"
        echo "  1. Set DATABASE_URL to your local database"
        echo "  2. Run: cd backend && python scripts/dump_all.py"
        echo "  3. Run this script again"
        exit 1
    fi
    
    mkdir -p ${DUMP_DIR}
    cd backend
    python scripts/dump_all.py
    cd ..
    
    # Move dumps
    mv backend/schema_dump_*.sql ${DUMP_DIR}/ 2>/dev/null || true
    mv backend/seed_data_dump_*.sql ${DUMP_DIR}/ 2>/dev/null || true
    mv backend/safe_user_seed_*.sql ${DUMP_DIR}/ 2>/dev/null || true
fi

# Upload files
echo ""
echo -e "${YELLOW}Uploading dump files...${NC}"

SCHEMA_FILE=$(ls -t ${DUMP_DIR}/schema_dump_*.sql 2>/dev/null | head -1)
SEED_FILE=$(ls -t ${DUMP_DIR}/seed_data_dump_*.sql 2>/dev/null | head -1)
USER_FILE=$(ls -t ${DUMP_DIR}/safe_user_seed_*.sql 2>/dev/null | head -1)

if [ -z "$SCHEMA_FILE" ] && [ -z "$SEED_FILE" ] && [ -z "$USER_FILE" ]; then
    echo -e "${RED}No dump files found in ${DUMP_DIR}${NC}"
    exit 1
fi

UPLOADED=0

if [ -n "$SCHEMA_FILE" ]; then
    echo "  Uploading schema: $(basename $SCHEMA_FILE)"
    gsutil cp "$SCHEMA_FILE" gs://${BUCKET_NAME}/schema.sql
    echo -e "  ${GREEN}✅ Schema uploaded${NC}"
    UPLOADED=$((UPLOADED + 1))
fi

if [ -n "$SEED_FILE" ]; then
    echo "  Uploading seed data: $(basename $SEED_FILE)"
    gsutil cp "$SEED_FILE" gs://${BUCKET_NAME}/seed_data.sql
    echo -e "  ${GREEN}✅ Seed data uploaded${NC}"
    UPLOADED=$((UPLOADED + 1))
fi

if [ -n "$USER_FILE" ]; then
    echo "  Uploading user seed: $(basename $USER_FILE)"
    gsutil cp "$USER_FILE" gs://${BUCKET_NAME}/users.sql
    echo -e "  ${GREEN}✅ User seed uploaded${NC}"
    UPLOADED=$((UPLOADED + 1))
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Upload Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Uploaded ${UPLOADED} file(s) to: gs://${BUCKET_NAME}/"
echo ""
echo "Next steps:"
echo "  1. Initialize database: ./gcp-init-db-consolidated.sh"
echo "  2. Deploy application: ./gcp-deploy-consolidated.sh"
echo ""

