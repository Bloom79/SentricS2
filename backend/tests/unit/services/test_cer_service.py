"""
Unit tests for CERService

Tests CER (Community Energy Resource) management operations.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.cer_service import CERService
from app.schemas.cer import CERCreate, CERUpdate, CERMemberCreate
from app.models.cer import CER, CERStatusEnum, CERMember
from app.models.tenant import Tenant
from app.models.user import User


class TestCERService:
    """Test suite for CERService"""

    def test_create_cer_success(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test successful CER creation"""
        # Arrange
        cer_data = CERCreate(
            name="Solar Community Rome",
            code="CER-ROME-001",
            status=CERStatusEnum.ACTIVE,
            legal_entity_type="Associazione",
            creation_date="2024-01-01",
            municipality="Rome",
            province="RM",
            region="Lazio",
            description="Community solar energy project"
        )

        # Act
        cer = CERService.create_cer(
            db_session,
            cer_data,
            test_tenant.id,
            test_user.id
        )

        # Assert
        assert cer.id is not None
        assert cer.name == "Solar Community Rome"
        assert cer.code == "CER-ROME-001"
        assert cer.status == CERStatusEnum.ACTIVE
        assert cer.tenant_id == test_tenant.id
        assert cer.created_by == test_user.id

    def test_get_cer_success(
        self,
        db_session: Session,
        test_cer: CER
    ):
        """Test retrieving a CER by ID"""
        # Act
        cer = CERService.get_cer(
            db_session,
            test_cer.id,
            test_cer.tenant_id
        )

        # Assert
        assert cer is not None
        assert cer.id == test_cer.id
        assert cer.name == test_cer.name

    def test_get_cer_not_found(
        self,
        db_session: Session,
        test_tenant: Tenant
    ):
        """Test retrieving non-existent CER returns None"""
        # Act
        cer = CERService.get_cer(
            db_session,
            99999,
            test_tenant.id
        )

        # Assert
        assert cer is None

    def test_list_cers(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_cer: CER
    ):
        """Test listing CERs"""
        # Act
        cers = CERService.list_cers(
            db_session,
            test_tenant.id,
            skip=0,
            limit=10
        )

        # Assert
        assert len(cers) >= 1
        assert cers[0].tenant_id == test_tenant.id

    def test_list_cers_filter_by_status(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_cer: CER
    ):
        """Test filtering CERs by status"""
        # Act
        cers = CERService.list_cers(
            db_session,
            test_tenant.id,
            status=CERStatusEnum.ACTIVE.value
        )

        # Assert
        assert len(cers) >= 1
        assert all(c.status == CERStatusEnum.ACTIVE for c in cers)

    def test_update_cer_success(
        self,
        db_session: Session,
        test_cer: CER,
        test_user: User
    ):
        """Test successful CER update"""
        # Arrange
        update_data = CERUpdate(
            name="Updated CER Name",
            description="Updated description"
        )

        # Act
        updated_cer = CERService.update_cer(
            db_session,
            test_cer.id,
            update_data,
            test_cer.tenant_id,
            test_user.id
        )

        # Assert
        assert updated_cer is not None
        assert updated_cer.name == "Updated CER Name"
        assert updated_cer.description == "Updated description"
        assert updated_cer.code == test_cer.code  # Unchanged

    def test_delete_cer_success(
        self,
        db_session: Session,
        test_cer: CER,
        test_user: User
    ):
        """Test successful CER deletion (soft delete)"""
        # Act
        result = CERService.delete_cer(
            db_session,
            test_cer.id,
            test_cer.tenant_id,
            test_user.id
        )

        # Assert
        assert result is True

        # Verify soft delete
        deleted_cer = db_session.query(CER).filter(CER.id == test_cer.id).first()
        assert deleted_cer.deleted_at is not None

    def test_add_member_to_cer(
        self,
        db_session: Session,
        test_cer: CER,
        test_user: User
    ):
        """Test adding a member to CER"""
        # Arrange
        member_data = CERMemberCreate(
            member_type="consumer",
            pod_code="IT001E12345678",
            name="Test Consumer",
            fiscal_code="RSSMRA80A01H501U",
            address="Via Test 123",
            municipality="Rome"
        )

        # Act
        member = CERService.add_member(
            db_session,
            test_cer.id,
            member_data,
            test_cer.tenant_id,
            test_user.id
        )

        # Assert
        assert member is not None
        assert member.cer_id == test_cer.id
        assert member.pod_code == "IT001E12345678"
        assert member.member_type == "consumer"

    def test_list_cer_members(
        self,
        db_session: Session,
        test_cer: CER,
        test_user: User
    ):
        """Test listing CER members"""
        # Arrange - Add a member first
        member_data = CERMemberCreate(
            member_type="producer",
            pod_code="IT001E87654321",
            name="Test Producer",
            fiscal_code="RSSMRA80A01H501U"
        )
        CERService.add_member(
            db_session,
            test_cer.id,
            member_data,
            test_cer.tenant_id,
            test_user.id
        )

        # Act
        members = CERService.list_members(
            db_session,
            test_cer.id,
            test_cer.tenant_id
        )

        # Assert
        assert len(members) >= 1
        assert members[0].cer_id == test_cer.id

    def test_calculate_cer_capacity(
        self,
        db_session: Session,
        test_cer: CER,
        test_plant,
        test_user: User
    ):
        """Test calculating total CER capacity from linked plants"""
        # Arrange - Link plant to CER
        test_plant.cer_id = test_cer.id
        db_session.commit()

        # Act
        capacity = CERService._update_capacity(
            db_session,
            test_cer.id,
            test_cer.tenant_id
        )

        # Assert
        db_session.refresh(test_cer)
        assert test_cer.total_capacity_kw >= test_plant.power_kw

    def test_cer_tenant_isolation(
        self,
        db_session: Session,
        test_tenant: Tenant,
        test_user: User
    ):
        """Test that CERs are isolated by tenant"""
        # Arrange - Create CER for tenant 1
        cer1 = CERService.create_cer(
            db_session,
            CERCreate(
                name="Tenant 1 CER",
                code="T1-CER-001",
                status=CERStatusEnum.ACTIVE,
                legal_entity_type="Associazione"
            ),
            test_tenant.id,
            test_user.id
        )

        # Create second tenant
        tenant2 = Tenant(id="tenant-2", name="Tenant 2", is_active=True)
        db_session.add(tenant2)
        db_session.commit()

        # Act - Try to access tenant 1's CER with tenant 2's ID
        result = CERService.get_cer(db_session, cer1.id, tenant2.id)

        # Assert
        assert result is None

        # Verify tenant 2 can't see tenant 1's CERs in list
        tenant2_cers = CERService.list_cers(db_session, tenant2.id)
        assert len(tenant2_cers) == 0
