#!/bin/bash
# Complete startup script for Kronos EAM
# Handles: containers, database setup, migrations, seed data, and services
# Usage: ./start-services.sh [--skip-seed] [--skip-frontend]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse arguments
SKIP_SEED=false
SKIP_FRONTEND=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-seed)
            SKIP_SEED=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-seed] [--skip-frontend]"
            exit 1
            ;;
    esac
done

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Kronos EAM - Complete Setup${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/7] Checking prerequisites...${NC}"
if ! command -v podman &> /dev/null; then
    echo -e "${RED}❌ Podman not found. Please install Podman first.${NC}"
    exit 1
fi
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Step 2: Activate virtual environment
echo -e "${YELLOW}[2/7] Activating virtual environment...${NC}"
source venv/bin/activate
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing/updating dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi
echo ""

# Step 3: Start containers
echo -e "${YELLOW}[3/7] Starting containers (Podman)...${NC}"

# Pull images if needed
echo -e "${YELLOW}  Pulling images...${NC}"
podman pull -q docker.io/postgis/postgis:15-3.3 > /dev/null 2>&1 || true
podman pull -q docker.io/redis:7-alpine > /dev/null 2>&1 || true

# Start database container
echo -e "${YELLOW}  Starting PostgreSQL with PostGIS...${NC}"
podman run -d \
  --name kronos-eam-db \
  --replace \
  -e POSTGRES_DB=kronos_eam \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v kronos_eam_postgres_data:/var/lib/postgresql/data:Z \
  docker.io/postgis/postgis:15-3.3 > /dev/null 2>&1 || true

# Start Redis container
echo -e "${YELLOW}  Starting Redis...${NC}"
podman run -d \
  --name kronos-eam-redis \
  --replace \
  -p 6379:6379 \
  -v kronos_eam_redis_data:/data:Z \
  docker.io/redis:7-alpine > /dev/null 2>&1 || true

# Wait for database to be ready (with better checks)
echo -e "${YELLOW}  Waiting for database to be ready...${NC}"
DB_READY=false
for i in {1..90}; do
    # Check if container is running
    if ! podman ps --format "{{.Names}}" | grep -q "^kronos-eam-db$"; then
        echo -e "${RED}❌ Database container stopped unexpectedly${NC}"
        podman logs kronos-eam-db --tail 20
        exit 1
    fi
    
    # Check if PostgreSQL is accepting connections
    if podman exec kronos-eam-db pg_isready -U postgres > /dev/null 2>&1; then
        # Additional check: try to connect and run a simple query
        if podman exec kronos-eam-db psql -U postgres -d kronos_eam -c "SELECT 1;" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Database is ready${NC}"
            DB_READY=true
            break
        fi
    fi
    
    if [ $i -eq 90 ]; then
        echo -e "${RED}❌ Database failed to start after 90 seconds${NC}"
        echo -e "${YELLOW}Database logs:${NC}"
        podman logs kronos-eam-db --tail 30
        exit 1
    fi
    
    if [ $((i % 10)) -eq 0 ]; then
        echo -e "${YELLOW}    Still waiting... (${i}/90)${NC}"
    fi
    sleep 1
done

# Give database a bit more time to fully initialize
if [ "$DB_READY" = true ]; then
    echo -e "${YELLOW}  Allowing database to fully initialize...${NC}"
    sleep 3
fi
echo ""

# Step 4: Initialize database
echo -e "${YELLOW}[4/7] Initializing database...${NC}"

# Check if tables exist
TABLES_EXIST=$(podman exec kronos-eam-db psql -U postgres -d kronos_eam -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name NOT LIKE 'pg_%' AND table_name != 'spatial_ref_sys';" 2>/dev/null || echo "0")

if [ "$TABLES_EXIST" -eq "0" ] || [ -z "$TABLES_EXIST" ]; then
    echo -e "${YELLOW}  Creating database tables...${NC}"
    
    # Retry table creation with better error handling
    MAX_RETRIES=3
    RETRY_COUNT=0
    TABLES_CREATED=false
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if python3 << 'PYTHON_EOF'
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.base import Base
import app.models.user
import app.models.tenant
import app.models.plant
import app.models.site
import app.models.asset
import app.models.cer
import app.models.workflow
import app.models.document
import time

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
print("Connecting to database...")

# Retry connection
for attempt in range(5):
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        break
    except Exception as e:
        if attempt < 4:
            print(f"Connection attempt {attempt + 1} failed, retrying...")
            time.sleep(2)
        else:
            raise

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("✓ Tables created successfully")
PYTHON_EOF
        then
            TABLES_CREATED=true
            echo -e "${GREEN}✓ Database tables created${NC}"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                echo -e "${YELLOW}  Retry ${RETRY_COUNT}/${MAX_RETRIES}...${NC}"
                sleep 3
            else
                echo -e "${RED}❌ Failed to create tables after ${MAX_RETRIES} attempts${NC}"
                exit 1
            fi
        fi
    done
else
    echo -e "${GREEN}✓ Database tables already exist${NC}"
fi
echo ""

# Step 5: Seed test data
if [ "$SKIP_SEED" = false ]; then
    echo -e "${YELLOW}[5/7] Seeding test data...${NC}"
    
    # Check if seed data already exists (check for plants, not just user)
    PLANTS_EXIST=$(podman exec kronos-eam-db psql -U postgres -d kronos_eam -tAc "SELECT COUNT(*) FROM plants WHERE tenant_id = 'demo';" 2>/dev/null || echo "0")
    
    if [ "$PLANTS_EXIST" -eq "0" ] || [ -z "$PLANTS_EXIST" ]; then
        echo -e "${YELLOW}  Creating tenant and user...${NC}"
        python3 << 'PYTHON_EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.tenant import Tenant, TenantStatusEnum
from app.core.security import get_password_hash
from datetime import datetime, timedelta, timezone

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Create tenant if not exists
    tenant = db.query(Tenant).filter(Tenant.id == 'demo').first()
    if not tenant:
        tenant = Tenant(
            id='demo',
            name='Demo Tenant',
            status=TenantStatusEnum.ACTIVE,
            plan='professional',
            plan_expiry=datetime.now(timezone.utc) + timedelta(days=365)
        )
        db.add(tenant)
        db.commit()
        print('✓ Tenant created')
    else:
        print('✓ Tenant already exists')

    # Create user if not exists
    user = db.query(User).filter(User.email == 'test@example.com').first()
    if not user:
        user = User(
            tenant_id='demo',
            name='Test User',
            email='test@example.com',
            password_hash=get_password_hash('test123'),
            role=UserRoleEnum.ADMIN,
            status=UserStatusEnum.ACTIVE,
            email_verified=True
        )
        db.add(user)
        db.commit()
        print('✓ User created')
        print('  Email: test@example.com')
        print('  Password: test123')
    else:
        print('✓ User already exists')
finally:
    db.close()
PYTHON_EOF
        
        # Seed data via direct Python script (more reliable than API)
        echo -e "${YELLOW}  Seeding plants, assets, and other data...${NC}"
        python3 << 'PYTHON_EOF'
import sys
sys.path.insert(0, '/home/bloom/sentrics/kronos-eam-consolidated/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.tenant import Tenant
from app.models.site import Site, SiteTypeEnum
from app.models.plant import Plant, PlantStatusEnum, PlantTypeEnum
from app.models.asset import Asset, AssetType, AssetStatus, ComponentType
from app.core.security import get_password_hash
from datetime import datetime, timedelta, timezone
import json

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get tenant and user
    tenant = db.query(Tenant).filter(Tenant.id == 'demo').first()
    user = db.query(User).filter(User.email == 'test@example.com').first()
    
    if not tenant or not user:
        print('⚠ Tenant or user not found, skipping advanced seeding')
        sys.exit(0)
    
    # Check if sites exist
    sites_count = db.query(Site).filter(Site.tenant_id == 'demo').count()
    if sites_count == 0:
        print('  Creating sites...')
        sites_data = [
            {
                "name": "Solar Park North",
                "code": "SPN-001",
                "site_type": SiteTypeEnum.INDUSTRIAL,
                "status": "active",
                "location": "Northern Italy",
                "city": "Milan",
                "province": "MI",
                "region": "Lombardy",
                "country": "Italy",
                "latitude": 45.4642,
                "longitude": 9.1900,
                "capacity": 5000.0,
                "efficiency": 85.5,
            },
            {
                "name": "Wind Farm Central",
                "code": "WFC-001",
                "site_type": SiteTypeEnum.INDUSTRIAL,
                "status": "active",
                "location": "Central Italy",
                "city": "Rome",
                "province": "RM",
                "region": "Lazio",
                "country": "Italy",
                "latitude": 41.9028,
                "longitude": 12.4964,
                "capacity": 3000.0,
                "efficiency": 78.2,
            },
            {
                "name": "Solar Complex South",
                "code": "SCS-001",
                "site_type": SiteTypeEnum.COMMERCIAL,
                "status": "active",
                "location": "Southern Italy",
                "city": "Naples",
                "province": "NA",
                "region": "Campania",
                "country": "Italy",
                "latitude": 40.8518,
                "longitude": 14.2681,
                "capacity": 2500.0,
                "efficiency": 82.0,
            }
        ]
        
        created_sites = []
        for site_data in sites_data:
            site = Site(tenant_id='demo', **site_data)
            db.add(site)
            db.flush()
            created_sites.append(site)
        db.commit()
        print(f'  ✓ Created {len(created_sites)} sites')
    else:
        print(f'  ✓ Sites already exist ({sites_count})')
        created_sites = db.query(Site).filter(Site.tenant_id == 'demo').all()
    
    # Check if plants exist
    plants_count = db.query(Plant).filter(Plant.tenant_id == 'demo').count()
    if plants_count == 0:
        print('  Creating plants...')
        plants_data = [
            {
                "name": "Solar Array Alpha",
                "code": "PLT-001",
                "power": "2.5 MW",
                "power_kw": 2500.0,
                "status": PlantStatusEnum.IN_OPERATION,
                "type": PlantTypeEnum.PHOTOVOLTAIC,
                "location": "Solar Park North - Zone A",
                "address": "Via Solare 1",
                "municipality": "Milan",
                "province": "MI",
                "region": "Lombardy",
                "latitude": 45.4642,
                "longitude": 9.1900,
                "gse_integration": True,
                "tags": json.dumps(["solar", "renewable", "north"]),
            },
            {
                "name": "Solar Array Beta",
                "code": "PLT-002",
                "power": "1.8 MW",
                "power_kw": 1800.0,
                "status": PlantStatusEnum.IN_OPERATION,
                "type": PlantTypeEnum.PHOTOVOLTAIC,
                "location": "Solar Park North - Zone B",
                "address": "Via Solare 2",
                "municipality": "Milan",
                "province": "MI",
                "region": "Lombardy",
                "latitude": 45.4650,
                "longitude": 9.1910,
                "gse_integration": True,
                "tags": json.dumps(["solar", "renewable"]),
            },
            {
                "name": "Wind Turbine Cluster 1",
                "code": "PLT-003",
                "power": "3.0 MW",
                "power_kw": 3000.0,
                "status": PlantStatusEnum.IN_OPERATION,
                "type": PlantTypeEnum.WIND,
                "location": "Wind Farm Central - Sector 1",
                "address": "Via Vento 10",
                "municipality": "Rome",
                "province": "RM",
                "region": "Lazio",
                "latitude": 41.9028,
                "longitude": 12.4964,
                "tags": json.dumps(["wind", "renewable"]),
            },
            {
                "name": "Solar Farm Gamma",
                "code": "PLT-004",
                "power": "1.2 MW",
                "power_kw": 1200.0,
                "status": PlantStatusEnum.IN_OPERATION,
                "type": PlantTypeEnum.PHOTOVOLTAIC,
                "location": "Solar Complex South - Block 1",
                "address": "Via Sole 5",
                "municipality": "Naples",
                "province": "NA",
                "region": "Campania",
                "latitude": 40.8518,
                "longitude": 14.2681,
                "gse_integration": True,
                "tags": json.dumps(["solar", "south"]),
            },
            {
                "name": "Hydro Plant Delta",
                "code": "PLT-005",
                "power": "5.0 MW",
                "power_kw": 5000.0,
                "status": PlantStatusEnum.IN_OPERATION,
                "type": PlantTypeEnum.HYDROELECTRIC,
                "location": "Central River Station",
                "address": "Via Acqua 20",
                "municipality": "Rome",
                "province": "RM",
                "region": "Lazio",
                "latitude": 41.9100,
                "longitude": 12.5000,
                "tags": json.dumps(["hydro", "renewable"]),
            },
            {
                "name": "Solar Array Epsilon",
                "code": "PLT-006",
                "power": "0.8 MW",
                "power_kw": 800.0,
                "status": PlantStatusEnum.IN_AUTHORIZATION,
                "type": PlantTypeEnum.PHOTOVOLTAIC,
                "location": "Solar Complex South - Block 2",
                "address": "Via Sole 6",
                "municipality": "Naples",
                "province": "NA",
                "region": "Campania",
                "latitude": 40.8520,
                "longitude": 14.2685,
                "tags": json.dumps(["solar", "pending"]),
            }
        ]
        
        created_plants = []
        for plant_data in plants_data:
            plant = Plant(
                tenant_id='demo',
                created_by=user.id,
                **plant_data
            )
            db.add(plant)
            db.flush()
            created_plants.append({"id": plant.id})
        db.commit()
        print(f'  ✓ Created {len(created_plants)} plants')
    else:
        print(f'  ✓ Plants already exist ({plants_count})')
        created_plants = [{"id": p.id} for p in db.query(Plant).filter(Plant.tenant_id == 'demo').all()]
    
    # Check if asset types exist
    asset_types_count = db.query(AssetType).filter(AssetType.tenant_id == 'demo').count()
    if asset_types_count == 0:
        print('  Creating asset types...')
        asset_types_data = [
            {"name": "Solar Panel", "normalized_name": "solar_panel", "description": "Photovoltaic solar panel"},
            {"name": "Inverter", "normalized_name": "inverter", "description": "DC to AC power inverter"},
            {"name": "Battery", "normalized_name": "battery", "description": "Energy storage battery"},
            {"name": "Transformer", "normalized_name": "transformer", "description": "Power transformer"},
        ]
        
        created_asset_types = {}
        for at_data in asset_types_data:
            asset_type = AssetType(tenant_id='demo', **at_data)
            db.add(asset_type)
            db.flush()
            created_asset_types[at_data["normalized_name"]] = asset_type
        db.commit()
        print(f'  ✓ Created {len(created_asset_types)} asset types')
    else:
        print(f'  ✓ Asset types already exist ({asset_types_count})')
        created_asset_types = {at.normalized_name: at for at in db.query(AssetType).filter(AssetType.tenant_id == 'demo').all()}
    
    # Check if assets exist
    assets_count = db.query(Asset).filter(Asset.tenant_id == 'demo').count()
    if assets_count == 0 and created_plants and created_asset_types:
        print('  Creating assets...')
        assets_data = []
        
        # Get plant types
        plants_with_types = db.query(Plant).filter(Plant.tenant_id == 'demo').all()
        plant_id_to_type = {p.id: p.type for p in plants_with_types}
        
        for plant_info in created_plants:
            plant_id = plant_info["id"]
            plant_type = plant_id_to_type.get(plant_id)
            
            if plant_type == PlantTypeEnum.PHOTOVOLTAIC:
                for i in range(1, 4):
                    assets_data.append({
                        "name": f"Panel Array {i}",
                        "plant_id": plant_id,
                        "type_id": created_asset_types["solar_panel"].id,
                        "component_type": ComponentType.PANEL.value,
                        "status": AssetStatus.OPERATIONAL.value,
                        "manufacturer": "SunPower",
                        "model": "SPR-400",
                        "rated_power": 0.4,
                        "voltage": 40.0,
                        "current": 10.0,
                        "efficiency": 22.8,
                        "location": f"Zone {chr(64+i)}",
                        "dynamic_attributes": json.dumps({"power_w": 400, "voltage_v": 40, "current_a": 10, "panels_count": 100}),
                    })
                
                for i in range(1, 3):
                    assets_data.append({
                        "name": f"Inverter {i}",
                        "plant_id": plant_id,
                        "type_id": created_asset_types["inverter"].id,
                        "component_type": ComponentType.INVERTER.value,
                        "status": AssetStatus.OPERATIONAL.value,
                        "manufacturer": "SMA",
                        "model": "Sunny Boy 5000",
                        "rated_power": 5.0,
                        "efficiency": 98.5,
                        "location": f"Inverter Station {i}",
                        "dynamic_attributes": json.dumps({"power_kw": 5.0, "efficiency": 98.5, "mppt_trackers": 2}),
                    })
            elif plant_type == PlantTypeEnum.WIND:
                assets_data.append({
                    "name": "Wind Turbine 1",
                    "plant_id": plant_id,
                    "type_id": created_asset_types["transformer"].id,
                    "component_type": ComponentType.TRANSFORMER.value,
                    "status": AssetStatus.OPERATIONAL.value,
                    "manufacturer": "Vestas",
                    "model": "V150-3.0",
                    "rated_power": 3000.0,
                    "location": "Turbine Field - Position 1",
                    "dynamic_attributes": json.dumps({"power_mw": 3.0, "rotor_diameter_m": 150, "hub_height_m": 105}),
                })
            elif plant_type == PlantTypeEnum.HYDROELECTRIC:
                assets_data.append({
                    "name": "Hydro Generator 1",
                    "plant_id": plant_id,
                    "type_id": created_asset_types["transformer"].id,
                    "component_type": ComponentType.TRANSFORMER.value,
                    "status": AssetStatus.OPERATIONAL.value,
                    "manufacturer": "Andritz",
                    "model": "HydroGen-5000",
                    "rated_power": 5000.0,
                    "efficiency": 92.0,
                    "location": "Main Turbine Hall",
                    "dynamic_attributes": json.dumps({"power_mw": 5.0, "flow_rate_m3s": 50, "head_m": 100}),
                })
        
        for asset_data in assets_data:
            asset = Asset(
                tenant_id='demo',
                created_by=user.id,
                **asset_data
            )
            db.add(asset)
        db.commit()
        print(f'  ✓ Created {len(assets_data)} assets')
    else:
        print(f'  ✓ Assets already exist ({assets_count})')
    
    print('✓ Seed data complete')
except Exception as e:
    print(f'⚠ Error during seeding: {e}')
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
PYTHON_EOF
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Test data seeded successfully${NC}"
        else
            echo -e "${YELLOW}⚠ Some seeding errors occurred (check output above)${NC}"
        fi
    else
        echo -e "${GREEN}✓ Seed data already exists${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}[5/7] Skipping seed data (--skip-seed)${NC}"
    echo ""
fi

# Step 6: Start backend
echo -e "${YELLOW}[6/7] Starting backend server...${NC}"
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo -e "${GREEN}✓ Backend is already running${NC}"
else
    if [ -d "venv" ]; then
        source venv/bin/activate
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
        BACKEND_PID=$!
        echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
        echo "  Logs: tail -f /tmp/backend.log"
        
        # Wait for backend to be ready
        echo -e "${YELLOW}  Waiting for backend to be ready...${NC}"
        for i in {1..30}; do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                echo -e "${GREEN}✓ Backend is ready${NC}"
                break
            fi
            if [ $i -eq 30 ]; then
                echo -e "${RED}⚠ Backend may not be ready yet${NC}"
            fi
            sleep 1
        done
    else
        echo -e "${RED}❌ Virtual environment not found${NC}"
        exit 1
    fi
fi
echo ""

# Step 7: Start frontend
if [ "$SKIP_FRONTEND" = false ]; then
    echo -e "${YELLOW}[7/7] Starting frontend server...${NC}"
    if pgrep -f "vite" > /dev/null; then
        echo -e "${GREEN}✓ Frontend is already running${NC}"
    else
        if [ -d "../frontend" ]; then
            cd ../frontend
            if [ ! -d "node_modules" ]; then
                echo -e "${YELLOW}  Installing frontend dependencies...${NC}"
                npm install > /dev/null 2>&1
            fi
            nohup npm run dev > /tmp/frontend.log 2>&1 &
            FRONTEND_PID=$!
            echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
            echo "  Logs: tail -f /tmp/frontend.log"
            cd "$SCRIPT_DIR"
            
            # Wait for frontend to be ready
            echo -e "${YELLOW}  Waiting for frontend to be ready...${NC}"
            for i in {1..30}; do
                if curl -s http://localhost:3000 > /dev/null 2>&1; then
                    echo -e "${GREEN}✓ Frontend is ready${NC}"
                    break
                fi
                if [ $i -eq 30 ]; then
                    echo -e "${YELLOW}⚠ Frontend may not be ready yet${NC}"
                fi
                sleep 1
            done
        else
            echo -e "${YELLOW}⚠ Frontend directory not found, skipping${NC}"
        fi
    fi
    echo ""
else
    echo -e "${YELLOW}[7/7] Skipping frontend (--skip-frontend)${NC}"
    echo ""
fi

# Summary
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "=== 📊 Service Status ==="
echo ""
echo "📦 Containers:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(kronos|NAME)" || echo "No containers found"
echo ""
echo "🌐 Services:"
echo "  ✅ Frontend:    http://localhost:3000"
echo "  ✅ Backend API: http://localhost:8000"
echo "  ✅ API Docs:    http://localhost:8000/docs"
echo ""
echo "🔐 Default Credentials:"
echo "  Email:    test@example.com"
echo "  Password: test123"
echo ""
echo "📝 Management Commands:"
echo "  Stop:     ./stop-services.sh"
echo "  Logs:     tail -f /tmp/backend.log"
echo "            tail -f /tmp/frontend.log"
echo "            podman logs -f kronos-eam-db"
echo "            podman logs -f kronos-eam-redis"
echo ""
echo "🔄 To restart: ./start-services.sh"
echo ""
