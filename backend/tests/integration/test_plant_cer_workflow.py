"""
Integration tests for Plant-CER workflow

Tests the complete flow of creating plants, linking to CERs,
and managing the relationship.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.plant_service import PlantService
from app.services.cer_service import CERService
from app.schemas.plant import PlantCreate
from app.schemas.cer import CERCreate
from app.models.plant import PlantStatusEnum, PlantTypeEnum
from app.models.cer import CERStatusEnum
from app.models.tenant import Tenant
from app.models.user import User


class TestPlantCERWorkflow:
    """Integration tests for Plant-CER workflow"""

    def test_complete_cer_plant_workflow(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test complete workflow: Create CER → Create Plant → Link Plant to CER"""
        # Step 1: Create CER
        cer_data = CERCreate(
            name="Integration Test CER",
            code="INT-CER-001",
            status=CERStatusEnum.ACTIVE,
            legal_entity_type="Associazione",
            creation_date="2024-01-01",
            municipality="Rome",
            province="RM",
            region="Lazio"
        )

        cer = CERService.create_cer(
            db_session,
            cer_data,
            test_tenant.id,
            test_user.id
        )

        assert cer.id is not None
        assert cer.total_capacity_kw == 0  # No plants yet

        # Step 2: Create first plant and link to CER
        plant1_data = PlantCreate(
            name="CER Solar Plant 1",
            code="CER-SOLAR-001",
            power="100 kW",
            power_kw=100.0,
            status=PlantStatusEnum.IN_OPERATION,
            type=PlantTypeEnum.PHOTOVOLTAIC,
            location="Rome, Italy",
            cer_id=cer.id
        )

        plant1 = PlantService.create_plant(
            db_session,
            plant1_data,
            test_tenant.id,
            test_user.id
        )

        assert plant1.cer_id == cer.id

        # Verify CER capacity updated
        db_session.refresh(cer)
        assert cer.total_capacity_kw >= 100.0

        # Step 3: Create second plant and link to same CER
        plant2_data = PlantCreate(
            name="CER Solar Plant 2",
            code="CER-SOLAR-002",
            power="150 kW",
            power_kw=150.0,
            status=PlantStatusEnum.IN_OPERATION,
            type=PlantTypeEnum.PHOTOVOLTAIC,
            location="Rome, Italy",
            cer_id=cer.id
        )

        plant2 = PlantService.create_plant(
            db_session,
            plant2_data,
            test_tenant.id,
            test_user.id
        )

        assert plant2.cer_id == cer.id

        # Verify CER capacity includes both plants
        db_session.refresh(cer)
        assert cer.total_capacity_kw >= 250.0

        # Step 4: List all plants in CER
        cer_plants = PlantService.list_plants(
            db_session,
            test_tenant.id,
            cer_id=cer.id
        )

        assert len(cer_plants) == 2
        assert all(p.cer_id == cer.id for p in cer_plants)

        # Step 5: Remove plant from CER
        from app.schemas.plant import PlantUpdate
        updated_plant = PlantService.update_plant(
            db_session,
            plant1.id,
            PlantUpdate(cer_id=None),
            test_tenant.id,
            test_user.id
        )

        assert updated_plant.cer_id is None

        # Verify CER capacity decreased
        db_session.refresh(cer)
        assert cer.total_capacity_kw >= 150.0
        assert cer.total_capacity_kw < 250.0

    def test_cer_member_with_plant_workflow(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test workflow: Create CER → Add Member → Create Plant for Member"""
        # Step 1: Create CER
        cer = CERService.create_cer(
            db_session,
            CERCreate(
                name="Member Test CER",
                code="MEM-CER-001",
                status=CERStatusEnum.ACTIVE,
                legal_entity_type="Associazione"
            ),
            test_tenant.id,
            test_user.id
        )

        # Step 2: Add producer member
        from app.schemas.cer import CERMemberCreate
        member = CERService.add_member(
            db_session,
            cer.id,
            CERMemberCreate(
                member_type="producer",
                pod_code="IT001E12345678",
                name="Producer Member",
                fiscal_code="RSSMRA80A01H501U"
            ),
            test_tenant.id,
            test_user.id
        )

        assert member.id is not None

        # Step 3: Create plant for this producer
        plant = PlantService.create_plant(
            db_session,
            PlantCreate(
                name=f"{member.name} Solar Plant",
                code="PROD-SOLAR-001",
                power_kw=200.0,
                status=PlantStatusEnum.IN_OPERATION,
                type=PlantTypeEnum.PHOTOVOLTAIC,
                location="Rome, Italy",
                cer_id=cer.id
            ),
            test_tenant.id,
            test_user.id
        )

        # Step 4: Verify integration
        db_session.refresh(cer)
        assert cer.total_capacity_kw >= 200.0

        # List members
        members = CERService.list_members(db_session, cer.id, test_tenant.id)
        assert len(members) >= 1

        # List plants
        plants = PlantService.list_plants(db_session, test_tenant.id, cer_id=cer.id)
        assert len(plants) >= 1

    def test_multi_tenant_cer_plant_isolation(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test that CER-Plant relationships are isolated by tenant"""
        # Tenant 1: Create CER and Plant
        cer1 = CERService.create_cer(
            db_session,
            CERCreate(
                name="Tenant 1 CER",
                code="T1-CER",
                status=CERStatusEnum.ACTIVE,
                legal_entity_type="Associazione"
            ),
            test_tenant.id,
            test_user.id
        )

        plant1 = PlantService.create_plant(
            db_session,
            PlantCreate(
                name="Tenant 1 Plant",
                code="T1-PLANT",
                power_kw=100.0,
                status=PlantStatusEnum.IN_OPERATION,
                type=PlantTypeEnum.PHOTOVOLTAIC,
                cer_id=cer1.id
            ),
            test_tenant.id,
            test_user.id
        )

        # Tenant 2: Create tenant, CER, and Plant
        tenant2 = Tenant(id="tenant-2", name="Tenant 2", is_active=True)
        db_session.add(tenant2)
        db_session.commit()

        user2 = User(
            email="user2@example.com",
            hashed_password="hashed",
            tenant_id=tenant2.id,
            is_active=True
        )
        db_session.add(user2)
        db_session.commit()

        cer2 = CERService.create_cer(
            db_session,
            CERCreate(
                name="Tenant 2 CER",
                code="T2-CER",
                status=CERStatusEnum.ACTIVE,
                legal_entity_type="Associazione"
            ),
            tenant2.id,
            user2.id
        )

        # Verify tenant isolation
        # Tenant 2 cannot see tenant 1's CER
        result = CERService.get_cer(db_session, cer1.id, tenant2.id)
        assert result is None

        # Tenant 2 cannot see tenant 1's plant
        result = PlantService.get_plant(db_session, plant1.id, tenant2.id)
        assert result is None

        # Tenant 1's plants don't appear in tenant 2's list
        tenant2_plants = PlantService.list_plants(db_session, tenant2.id)
        assert len(tenant2_plants) == 0

        # Tenant 1's CERs don't appear in tenant 2's list
        tenant2_cers = CERService.list_cers(db_session, tenant2.id)
        assert cer1.id not in [c.id for c in tenant2_cers]
