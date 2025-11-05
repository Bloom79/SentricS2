"""
Unit tests for PlantService

Tests all CRUD operations and business logic for plant management.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.plant_service import PlantService
from app.schemas.plant import PlantCreate, PlantUpdate
from app.models.plant import Plant, PlantStatusEnum, PlantTypeEnum
from app.models.tenant import Tenant
from app.models.user import User


class TestPlantService:
    """Test suite for PlantService"""

    def test_create_plant_success(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test successful plant creation"""
        # Arrange
        plant_data = PlantCreate(
            name="New Solar Plant",
            code="NEW-SOLAR-001",
            power="150 kW",
            power_kw=150.0,
            status=PlantStatusEnum.IN_OPERATION,
            type=PlantTypeEnum.PHOTOVOLTAIC,
            location="Milan, Italy",
            address="Via Milano 456",
            municipality="Milan",
            province="MI",
            region="Lombardy",
            latitude=45.4642,
            longitude=9.1900,
        )

        # Act
        plant = PlantService.create_plant(
            db_session,
            plant_data,
            test_tenant.id,
            test_user.id
        )

        # Assert
        assert plant.id is not None
        assert plant.name == "New Solar Plant"
        assert plant.code == "NEW-SOLAR-001"
        assert plant.power_kw == 150.0
        assert plant.tenant_id == test_tenant.id
        assert plant.created_by == test_user.id
        assert plant.status == PlantStatusEnum.IN_OPERATION
        assert plant.type == PlantTypeEnum.PHOTOVOLTAIC

    def test_create_plant_with_cer(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User,
        test_cer
    ):
        """Test plant creation with CER linkage"""
        # Arrange
        plant_data = PlantCreate(
            name="CER Solar Plant",
            code="CER-SOLAR-001",
            power="200 kW",
            power_kw=200.0,
            status=PlantStatusEnum.IN_OPERATION,
            type=PlantTypeEnum.PHOTOVOLTAIC,
            location="Rome, Italy",
            cer_id=test_cer.id,
        )

        # Act
        plant = PlantService.create_plant(
            db_session,
            plant_data,
            test_tenant.id,
            test_user.id
        )

        # Assert
        assert plant.cer_id == test_cer.id
        assert plant.cer is not None
        assert plant.cer.name == test_cer.name

    def test_get_plant_success(
        self,
        db_session: Session,
        test_plant: Plant
    ):
        """Test retrieving a plant by ID"""
        # Act
        plant = PlantService.get_plant(
            db_session,
            test_plant.id,
            test_plant.tenant_id
        )

        # Assert
        assert plant is not None
        assert plant.id == test_plant.id
        assert plant.name == test_plant.name
        assert plant.code == test_plant.code

    def test_get_plant_not_found(
        self,
        db_session: Session,
        test_tenant: Tenant
    ):
        """Test retrieving non-existent plant returns None"""
        # Act
        plant = PlantService.get_plant(
            db_session,
            99999,
            test_tenant.id
        )

        # Assert
        assert plant is None

    def test_get_plant_wrong_tenant(
        self,
        db_session: Session,
        test_plant: Plant
    ):
        """Test tenant isolation - cannot access other tenant's plants"""
        # Act
        plant = PlantService.get_plant(
            db_session,
            test_plant.id,
            "wrong-tenant-id"
        )

        # Assert
        assert plant is None

    def test_list_plants(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_plant: Plant
    ):
        """Test listing plants with filters"""
        # Act
        plants = PlantService.list_plants(
            db_session,
            test_tenant.id,
            skip=0,
            limit=10
        )

        # Assert
        assert len(plants) >= 1
        assert plants[0].tenant_id == test_tenant.id

    def test_list_plants_filter_by_type(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_plant: Plant
    ):
        """Test filtering plants by type"""
        # Act
        plants = PlantService.list_plants(
            db_session,
            test_tenant.id,
            type=PlantTypeEnum.PHOTOVOLTAIC.value
        )

        # Assert
        assert len(plants) >= 1
        assert all(p.type == PlantTypeEnum.PHOTOVOLTAIC for p in plants)

    def test_list_plants_filter_by_status(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_plant: Plant
    ):
        """Test filtering plants by status"""
        # Act
        plants = PlantService.list_plants(
            db_session,
            test_tenant.id,
            status=PlantStatusEnum.IN_OPERATION.value
        )

        # Assert
        assert len(plants) >= 1
        assert all(p.status == PlantStatusEnum.IN_OPERATION for p in plants)

    def test_update_plant_success(
        self,
        db_session: Session,
        test_plant: Plant,
        test_user: User
    ):
        """Test successful plant update"""
        # Arrange
        update_data = PlantUpdate(
            name="Updated Plant Name",
            power_kw=250.0,
        )

        # Act
        updated_plant = PlantService.update_plant(
            db_session,
            test_plant.id,
            update_data,
            test_plant.tenant_id,
            test_user.id
        )

        # Assert
        assert updated_plant is not None
        assert updated_plant.name == "Updated Plant Name"
        assert updated_plant.power_kw == 250.0
        assert updated_plant.code == test_plant.code  # Unchanged
        assert updated_plant.updated_by == test_user.id

    def test_update_plant_not_found(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test updating non-existent plant returns None"""
        # Arrange
        update_data = PlantUpdate(name="New Name")

        # Act
        result = PlantService.update_plant(
            db_session,
            99999,
            update_data,
            test_tenant.id,
            test_user.id
        )

        # Assert
        assert result is None

    def test_delete_plant_success(
        self,
        db_session: Session,
        test_plant: Plant,
        test_user: User
    ):
        """Test successful plant deletion (soft delete)"""
        # Act
        result = PlantService.delete_plant(
            db_session,
            test_plant.id,
            test_plant.tenant_id,
            test_user.id
        )

        # Assert
        assert result is True

        # Verify soft delete
        deleted_plant = db_session.query(Plant).filter(Plant.id == test_plant.id).first()
        assert deleted_plant.deleted_at is not None
        assert deleted_plant.deleted_by == test_user.id

    def test_delete_plant_not_found(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test deleting non-existent plant returns False"""
        # Act
        result = PlantService.delete_plant(
            db_session,
            99999,
            test_tenant.id,
            test_user.id
        )

        # Assert
        assert result is False

    def test_get_plant_stats(
        self,
        db_session: Session,
        test_plant: Plant,
        test_asset
    ):
        """Test getting plant statistics"""
        # Act
        stats = PlantService.get_plant_stats(
            db_session,
            test_plant.id,
            test_plant.tenant_id
        )

        # Assert
        assert stats is not None
        assert stats["plant_id"] == test_plant.id
        assert stats["total_assets"] >= 1
        assert stats["operational_assets"] >= 1
        assert stats["total_capacity_kw"] == test_plant.power_kw
        assert "cer_linked" in stats

    def test_get_plant_stats_not_found(
        self,
        db_session: Session,
        test_tenant: Tenant
    ):
        """Test getting stats for non-existent plant returns empty dict"""
        # Act
        stats = PlantService.get_plant_stats(
            db_session,
            99999,
            test_tenant.id
        )

        # Assert
        assert stats == {}

    def test_plant_tenant_isolation(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test that plants are isolated by tenant"""
        # Arrange - Create plant for tenant 1
        plant1 = PlantService.create_plant(
            db_session,
            PlantCreate(
                name="Tenant 1 Plant",
                code="T1-PLANT-001",
                power_kw=100.0,
                status=PlantStatusEnum.IN_OPERATION,
                type=PlantTypeEnum.PHOTOVOLTAIC,
            ),
            test_tenant.id,
            test_user.id
        )

        # Create second tenant
        tenant2 = Tenant(id="tenant-2", name="Tenant 2", is_active=True)
        db_session.add(tenant2)
        db_session.commit()

        # Act - Try to access tenant 1's plant with tenant 2's ID
        result = PlantService.get_plant(db_session, plant1.id, tenant2.id)

        # Assert
        assert result is None

        # Verify tenant 2 can't see tenant 1's plants in list
        tenant2_plants = PlantService.list_plants(db_session, tenant2.id)
        assert len(tenant2_plants) == 0
