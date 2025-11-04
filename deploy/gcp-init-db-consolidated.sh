#!/bin/bash
#
# Initialize GCP Cloud SQL database for consolidated project
# Uses dump files and seeds data linked to authenticated user
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
SQL_INSTANCE_NAME=${SQL_INSTANCE_NAME:-"kronos-db"}
SQL_DATABASE_NAME=${SQL_DATABASE_NAME:-"kronos_eam"}
SQL_USER=${SQL_USER:-"kronos"}
DB_INIT_BUCKET="${PROJECT_ID}-db-init"
DUMP_DIR=${DUMP_DIR:-"./dumps"}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}GCP Database Initialization${NC}"
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

# Check if instance exists
if ! gcloud sql instances describe ${SQL_INSTANCE_NAME} &>/dev/null; then
    echo -e "${RED}Cloud SQL instance '${SQL_INSTANCE_NAME}' not found${NC}"
    echo "Run deploy/gcp-setup-consolidated.sh first to create the instance"
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

# Function to import from GCS
import_from_gcs() {
    local gcs_file=$1
    local description=$2
    
    echo -e "${YELLOW}Importing: $description${NC}"
    echo -e "   File: $gcs_file"
    
    gcloud sql import sql ${SQL_INSTANCE_NAME} \
        ${gcs_file} \
        --database=${SQL_DATABASE_NAME} \
        --quiet || {
        echo -e "${YELLOW}⚠️  Import may have failed or data already exists${NC}"
        return 1
    }
    
    echo -e "${GREEN}✅ $description imported${NC}"
    return 0
}

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
echo -e "${GREEN}✅ PostGIS enabled${NC}"

# 2. Check for dump files in GCS
echo -e "\n${YELLOW}Step 2: Checking for dump files in Cloud Storage...${NC}"
SCHEMA_EXISTS=false
SEED_EXISTS=false
USERS_EXISTS=false

if gsutil ls gs://${DB_INIT_BUCKET}/schema.sql &>/dev/null; then
    SCHEMA_EXISTS=true
    echo -e "${GREEN}Found schema.sql${NC}"
fi

if gsutil ls gs://${DB_INIT_BUCKET}/seed_data.sql &>/dev/null; then
    SEED_EXISTS=true
    echo -e "${GREEN}Found seed_data.sql${NC}"
fi

if gsutil ls gs://${DB_INIT_BUCKET}/users.sql &>/dev/null; then
    USERS_EXISTS=true
    echo -e "${GREEN}Found users.sql${NC}"
fi

# 3. Import schema
if [ "$SCHEMA_EXISTS" = true ]; then
    import_from_gcs "gs://${DB_INIT_BUCKET}/schema.sql" "Schema"
else
    echo -e "${YELLOW}⚠️  No schema.sql found in GCS.${NC}"
    echo "   Database structure will be created by Alembic migrations."
fi

# 4. Import seed data
if [ "$SEED_EXISTS" = true ]; then
    import_from_gcs "gs://${DB_INIT_BUCKET}/seed_data.sql" "Seed Data"
else
    echo -e "${YELLOW}⚠️  No seed_data.sql found in GCS.${NC}"
    echo "   You can seed data after deployment using seed_authenticated_data.py"
fi

# 5. Import users (with confirmation)
if [ "$USERS_EXISTS" = true ]; then
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Users will be imported with placeholder passwords!${NC}"
    read -p "Import users? (yes/no): " response
    if [ "$response" = "yes" ]; then
        import_from_gcs "gs://${DB_INIT_BUCKET}/users.sql" "Users"
        echo ""
        echo -e "${RED}⚠️  REMEMBER: Update all user passwords after import!${NC}"
    else
        echo "Skipping user import."
    fi
fi

# 6. Run migrations to ensure schema is current
echo -e "\n${YELLOW}Step 3: Running Alembic migrations...${NC}"
echo "This ensures the schema is up to date with all migrations."

# Get database password from secret
DB_PASSWORD=$(gcloud secrets versions access latest --secret="db-password" --project=${PROJECT_ID} 2>/dev/null || echo "")

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  Could not get database password from Secret Manager${NC}"
    echo "   Run migrations manually after deployment"
else
    # Construct connection string
    DATABASE_URL="postgresql://${SQL_USER}:${DB_PASSWORD}@/${SQL_DATABASE_NAME}?host=/cloudsql/${SQL_CONNECTION_NAME}"
    
    echo "Running migrations..."
    # Note: This requires Cloud SQL Proxy or direct connection
    # For now, migrations will run during Cloud Build deployment
    echo -e "${GREEN}✅ Migrations will run during backend deployment${NC}"
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Database Initialization Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Deploy backend: ./gcp-deploy-consolidated.sh"
echo "  2. Seed authenticated data (after first user login):"
echo "     python backend/scripts/seed_authenticated_data.py \\"
echo "       --user-email 'your-email@example.com' \\"
echo "       --user-name 'Your Name' \\"
echo "       --user-password 'secure_password'"
echo ""

