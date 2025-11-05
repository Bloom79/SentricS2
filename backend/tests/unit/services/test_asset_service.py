"""
Unit tests for AssetService

Tests asset management operations.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.asset_service import AssetService
from app.schemas.asset import AssetCreate, AssetUpdate, AssetTypeCreate
from app.models.asset import Asset, AssetType
from app.models.plant import Plant
from app.models.tenant import Tenant
from app.models.user import User


class TestAssetService:
    """Test suite for AssetService"""

    def test_create_asset_type_success(
        self,
        db_session: Session,
        test_tenant: Tenant
    ):
        """Test successful asset type creation"""
        # Arrange
        asset_type_data = AssetTypeCreate(
            name="Wind Turbine",
            category="generation",
            description="Wind energy generator",
            technical_specs={
                "rated_power_kw": 3000,
                "rotor_diameter_m": 112,
                "hub_height_m": 94
            }
        )

        # Act
        asset_type = AssetService.create_asset_type(
            db_session,
            asset_type_data,
            test_tenant.id
        )

        # Assert
        assert asset_type.id is not None
        assert asset_type.name == "Wind Turbine"
        assert asset_type.category == "generation"
        assert asset_type.technical_specs["rated_power_kw"] == 3000

    def test_list_asset_types(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_asset_type: AssetType
    ):
        """Test listing asset types"""
        # Act
        asset_types = AssetService.list_asset_types(
            db_session,
            test_tenant.id
        )

        # Assert
        assert len(asset_types) >= 1
        assert asset_types[0].tenant_id == test_tenant.id

    def test_create_asset_success(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_plant: Plant,
        test_asset_type: AssetType,
        test_user: User
    ):
        """Test successful asset creation"""
        # Arrange
        asset_data = AssetCreate(
            plant_id=test_plant.id,
            asset_type_id=test_asset_type.id,
            name="Solar Panel #2",
            serial_number="SP-2024-002",
            status="operational",
            manufacturer="SunPower",
            model="MAXEON 3",
            installation_date="2024-01-20"
        )

        # Act
        asset = AssetService.create_asset(
            db_session,
            asset_data,
            test_tenant.id,
            test_user.id
        )

        # Assert
        assert asset.id is not None
        assert asset.name == "Solar Panel #2"
        assert asset.serial_number == "SP-2024-002"
        assert asset.plant_id == test_plant.id
        assert asset.asset_type_id == test_asset_type.id
        assert asset.tenant_id == test_tenant.id

    def test_get_asset_success(
        self,
        db_session: Session,
        test_asset: Asset
    ):
        """Test retrieving an asset by ID"""
        # Act
        asset = AssetService.get_asset(
            db_session,
            test_asset.id,
            test_asset.tenant_id
        )

        # Assert
        assert asset is not None
        assert asset.id == test_asset.id
        assert asset.name == test_asset.name

    def test_list_plant_assets(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_plant: Plant,
        test_asset: Asset
    ):
        """Test listing assets for a specific plant"""
        # Act
        assets = AssetService.list_plant_assets(
            db_session,
            test_plant.id,
            test_tenant.id
        )

        # Assert
        assert len(assets) >= 1
        assert all(a.plant_id == test_plant.id for a in assets)

    def test_update_asset_success(
        self,
        db_session: Session,
        test_asset: Asset,
        test_user: User
    ):
        """Test successful asset update"""
        # Arrange
        update_data = AssetUpdate(
            name="Updated Panel Name",
            status="maintenance"
        )

        # Act
        updated_asset = AssetService.update_asset(
            db_session,
            test_asset.id,
            update_data,
            test_asset.tenant_id,
            test_user.id
        )

        # Assert
        assert updated_asset is not None
        assert updated_asset.name == "Updated Panel Name"
        assert updated_asset.status == "maintenance"
        assert updated_asset.serial_number == test_asset.serial_number  # Unchanged

    def test_delete_asset_success(
        self,
        db_session: Session,
        test_asset: Asset,
        test_user: User
    ):
        """Test successful asset deletion (soft delete)"""
        # Act
        result = AssetService.delete_asset(
            db_session,
            test_asset.id,
            test_asset.tenant_id,
            test_user.id
        )

        # Assert
        assert result is True

        # Verify soft delete
        deleted_asset = db_session.query(Asset).filter(Asset.id == test_asset.id).first()
        assert deleted_asset.deleted_at is not None

    def test_asset_tenant_isolation(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_asset: Asset
    ):
        """Test that assets are isolated by tenant"""
        # Create second tenant
        tenant2 = Tenant(id="tenant-2", name="Tenant 2", is_active=True)
        db_session.add(tenant2)
        db_session.commit()

        # Act - Try to access tenant 1's asset with tenant 2's ID
        result = AssetService.get_asset(db_session, test_asset.id, tenant2.id)

        # Assert
        assert result is None
