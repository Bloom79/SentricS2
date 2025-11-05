"""
Pytest configuration and shared fixtures
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import Base
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User
from app.models.plant import Plant, PlantStatusEnum, PlantTypeEnum
from app.models.cer import CER, CERStatusEnum
from app.models.asset import Asset, AssetType


# Test database URL
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/sentrics2_test"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    test_engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    yield test_engine

    # Drop all tables after tests
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create a new database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session) -> TestClient:
    """Create test client with database session override"""
    from app.core.database import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_tenant(db_session) -> Tenant:
    """Create a test tenant"""
    tenant = Tenant(
        id="test-tenant",
        name="Test Tenant",
        is_active=True,
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db_session, test_tenant) -> User:
    """Create a test user"""
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        tenant_id=test_tenant.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_plant(db_session, test_tenant, test_user) -> Plant:
    """Create a test plant"""
    plant = Plant(
        tenant_id=test_tenant.id,
        name="Test Solar Plant",
        code="TEST-SOLAR-001",
        power="100 kW",
        power_kw=100.0,
        status=PlantStatusEnum.IN_OPERATION,
        type=PlantTypeEnum.PHOTOVOLTAIC,
        location="Rome, Italy",
        address="Via Roma 123",
        municipality="Rome",
        province="RM",
        region="Lazio",
        latitude=41.9028,
        longitude=12.4964,
        created_by=test_user.id,
    )
    db_session.add(plant)
    db_session.commit()
    db_session.refresh(plant)
    return plant


@pytest.fixture
def test_cer(db_session, test_tenant, test_user) -> CER:
    """Create a test CER"""
    cer = CER(
        tenant_id=test_tenant.id,
        name="Test CER Community",
        code="CER-TEST-001",
        status=CERStatusEnum.ACTIVE,
        legal_entity_type="Associazione",
        creation_date="2024-01-01",
        municipality="Rome",
        province="RM",
        region="Lazio",
        created_by=test_user.id,
    )
    db_session.add(cer)
    db_session.commit()
    db_session.refresh(cer)
    return cer


@pytest.fixture
def test_asset_type(db_session, test_tenant) -> AssetType:
    """Create a test asset type"""
    asset_type = AssetType(
        tenant_id=test_tenant.id,
        name="Solar Panel",
        category="generation",
        description="Photovoltaic solar panel",
        technical_specs={
            "power_wp": 550,
            "efficiency": 21.5,
            "technology": "monocrystalline"
        }
    )
    db_session.add(asset_type)
    db_session.commit()
    db_session.refresh(asset_type)
    return asset_type


@pytest.fixture
def test_asset(db_session, test_tenant, test_plant, test_asset_type, test_user) -> Asset:
    """Create a test asset"""
    asset = Asset(
        tenant_id=test_tenant.id,
        plant_id=test_plant.id,
        asset_type_id=test_asset_type.id,
        name="Solar Panel #1",
        serial_number="SP-2024-001",
        status="operational",
        manufacturer="SunPower",
        model="MAXEON 3",
        installation_date="2024-01-15",
        created_by=test_user.id,
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


@pytest.fixture
def auth_headers(test_user) -> dict:
    """Create authentication headers for API tests"""
    from app.core.security import create_access_token

    access_token = create_access_token(subject=test_user.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    from unittest.mock import patch

    with patch.object(settings, 'ENVIRONMENT', 'testing'):
        with patch.object(settings, 'RATE_LIMIT_ENABLED', False):
            yield settings
