#!/bin/bash
#
# Initialize GCP Cloud SQL database using dump files
# This script uploads and executes schema and seed data dumps
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"kronos-eam-prod-20250802"}
REGION=${GCP_REGION:-"europe-west1"}
SQL_INSTANCE_NAME=${SQL_INSTANCE_NAME:-"kronos-db"}
SQL_DATABASE_NAME=${SQL_DATABASE_NAME:-"kronos_eam"}
SQL_USER=${SQL_USER:-"kronos"}
DUMP_DIR=${DUMP_DIR:-"./dumps"}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}GCP Database Initialization${NC}"
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

# Check if instance exists
if ! gcloud sql instances describe ${SQL_INSTANCE_NAME} &>/dev/null; then
    echo -e "${RED}Cloud SQL instance '${SQL_INSTANCE_NAME}' not found${NC}"
    echo "Run deploy/gcp-setup.sh first to create the instance"
    exit 1
fi

# Get Cloud SQL connection name
SQL_CONNECTION_NAME=$(gcloud sql instances describe ${SQL_INSTANCE_NAME} --format="value(connectionName)")
echo -e "${GREEN}Found Cloud SQL instance: ${SQL_CONNECTION_NAME}${NC}"

# Check if database exists
if ! gcloud sql databases describe ${SQL_DATABASE_NAME} --instance=${SQL_INSTANCE_NAME} &>/dev/null; then
    echo -e "${YELLOW}Creating database ${SQL_DATABASE_NAME}...${NC}"
    gcloud sql databases create ${SQL_DATABASE_NAME} --instance=${SQL_INSTANCE_NAME}
    echo -e "${GREEN}Database created${NC}"
fi

# Function to execute SQL file
execute_sql_file() {
    local file=$1
    local description=$2
    
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}⚠️  File not found: $file${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Executing: $description${NC}"
    echo -e "   File: $file"
    
    # Use Cloud SQL Proxy or direct connection
    # For Cloud SQL, we'll use gcloud sql connect or Cloud SQL Proxy
    
    # Option 1: Using Cloud SQL Proxy (if available)
    if command -v cloud-sql-proxy &> /dev/null; then
        echo "   Using Cloud SQL Proxy..."
        cloud-sql-proxy ${SQL_CONNECTION_NAME} &
        PROXY_PID=$!
        sleep 3
        
        # Execute SQL
        PGPASSWORD=$(gcloud secrets versions access latest --secret="db-password" 2>/dev/null || echo "") \
        psql -h 127.0.0.1 -p 5432 -U ${SQL_USER} -d ${SQL_DATABASE_NAME} -f "$file" || {
            kill $PROXY_PID 2>/dev/null || true
            return 1
        }
        
        kill $PROXY_PID 2>/dev/null || true
    else
        # Option 2: Upload to Cloud Storage and import
        echo "   Uploading to Cloud Storage..."
        
        BUCKET_NAME="${PROJECT_ID}-db-init"
        
        # Create bucket if it doesn't exist
        if ! gsutil ls -b gs://${BUCKET_NAME} &>/dev/null; then
            gsutil mb -l ${REGION} gs://${BUCKET_NAME}
        fi
        
        # Upload file
        FILE_NAME=$(basename "$file")
        gsutil cp "$file" gs://${BUCKET_NAME}/${FILE_NAME}
        
        # Import using gcloud sql import
        echo "   Importing to Cloud SQL..."
        gcloud sql import sql ${SQL_INSTANCE_NAME} \
            gs://${BUCKET_NAME}/${FILE_NAME} \
            --database=${SQL_DATABASE_NAME} \
            --quiet || {
            echo -e "${RED}Import failed${NC}"
            return 1
        }
        
        # Clean up
        gsutil rm gs://${BUCKET_NAME}/${FILE_NAME}
    fi
    
    echo -e "${GREEN}✅ $description complete${NC}"
    return 0
}

# Create dump directory if it doesn't exist
mkdir -p "${DUMP_DIR}"

# Check if dump files exist
SCHEMA_FILE=$(ls -t ${DUMP_DIR}/schema_dump_*.sql 2>/dev/null | head -1)
SEED_FILE=$(ls -t ${DUMP_DIR}/seed_data_dump_*.sql 2>/dev/null | head -1)
USER_FILE=$(ls -t ${DUMP_DIR}/safe_user_seed_*.sql 2>/dev/null | head -1)

if [ -z "$SCHEMA_FILE" ] && [ -z "$SEED_FILE" ]; then
    echo -e "${YELLOW}No dump files found in ${DUMP_DIR}${NC}"
    echo "Generating dumps from local database..."
    
    # Check if we can connect to local database
    if [ -z "$DATABASE_URL" ]; then
        echo -e "${RED}DATABASE_URL not set. Cannot generate dumps.${NC}"
        echo "Please:"
        echo "  1. Set DATABASE_URL to your local database"
        echo "  2. Run: python backend/scripts/dump_all.py"
        echo "  3. Run this script again"
        exit 1
    fi
    
    cd backend
    python scripts/dump_all.py
    cd ..
    
    # Move dumps to dump directory
    mv backend/schema_dump_*.sql ${DUMP_DIR}/ 2>/dev/null || true
    mv backend/seed_data_dump_*.sql ${DUMP_DIR}/ 2>/dev/null || true
    mv backend/safe_user_seed_*.sql ${DUMP_DIR}/ 2>/dev/null || true
    
    SCHEMA_FILE=$(ls -t ${DUMP_DIR}/schema_dump_*.sql 2>/dev/null | head -1)
    SEED_FILE=$(ls -t ${DUMP_DIR}/seed_data_dump_*.sql 2>/dev/null | head -1)
    USER_FILE=$(ls -t ${DUMP_DIR}/safe_user_seed_*.sql 2>/dev/null | head -1)
fi

# Initialize database
echo ""
echo -e "${BLUE}Initializing database...${NC}"
echo ""

# 1. Enable PostGIS extension
echo -e "${YELLOW}Step 1: Enabling PostGIS extension...${NC}"
gcloud sql databases execute-sql ${SQL_INSTANCE_NAME} \
    --database=${SQL_DATABASE_NAME} \
    --sql="CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS postgis_topology;" \
    --quiet || echo "PostGIS may already be enabled"

# 2. Import schema
if [ -n "$SCHEMA_FILE" ]; then
    execute_sql_file "$SCHEMA_FILE" "Schema"
else
    echo -e "${YELLOW}⚠️  No schema file found. Skipping schema import.${NC}"
    echo "   Database structure should be created by Alembic migrations."
fi

# 3. Import seed data
if [ -n "$SEED_FILE" ]; then
    execute_sql_file "$SEED_FILE" "Seed Data"
else
    echo -e "${YELLOW}⚠️  No seed data file found. Skipping seed data import.${NC}"
fi

# 4. Import users (with confirmation)
if [ -n "$USER_FILE" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Users will be imported with placeholder passwords!${NC}"
    read -p "Import users? (yes/no): " response
    if [ "$response" = "yes" ]; then
        execute_sql_file "$USER_FILE" "Users"
        echo ""
        echo -e "${RED}⚠️  REMEMBER: Update all user passwords after import!${NC}"
    else
        echo "Skipping user import."
    fi
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Database Initialization Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Verify database: gcloud sql databases list --instance=${SQL_INSTANCE_NAME}"
echo "  2. Run migrations: alembic upgrade head (if needed)"
echo "  3. Update user passwords (if users were imported)"
echo ""

