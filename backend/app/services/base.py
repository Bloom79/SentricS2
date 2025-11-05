"""
Base Service Class
Provides common patterns and utilities for all service classes
"""

from typing import TypeVar, Type, Optional, List
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_

from app.models.base import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseService:
    """
    Base class for all service classes

    Provides common patterns:
    - Tenant isolation
    - Soft delete filtering
    - Standard CRUD operations
    - Pagination
    """

    @staticmethod
    def _apply_tenant_filter(
        query: Query,
        model: Type[T],
        tenant_id: str
    ) -> Query:
        """
        Apply tenant isolation filter to query

        Args:
            query: SQLAlchemy query
            model: Model class
            tenant_id: Tenant ID for filtering

        Returns:
            Query with tenant filter applied
        """
        return query.filter(model.tenant_id == tenant_id)

    @staticmethod
    def _apply_deleted_filter(
        query: Query,
        model: Type[T]
    ) -> Query:
        """
        Apply soft delete filter (exclude deleted records)

        Args:
            query: SQLAlchemy query
            model: Model class

        Returns:
            Query with deleted_at filter applied
        """
        return query.filter(model.deleted_at.is_(None))

    @staticmethod
    def _apply_tenant_and_deleted_filters(
        query: Query,
        model: Type[T],
        tenant_id: str
    ) -> Query:
        """
        Apply both tenant isolation and soft delete filters

        Args:
            query: SQLAlchemy query
            model: Model class
            tenant_id: Tenant ID for filtering

        Returns:
            Query with both filters applied
        """
        return query.filter(
            and_(
                model.tenant_id == tenant_id,
                model.deleted_at.is_(None)
            )
        )

    @staticmethod
    def _get_by_id(
        db: Session,
        model: Type[T],
        id: int,
        tenant_id: str
    ) -> Optional[T]:
        """
        Get single record by ID with tenant isolation

        Args:
            db: Database session
            model: Model class
            id: Record ID
            tenant_id: Tenant ID

        Returns:
            Model instance or None if not found
        """
        return (
            db.query(model)
            .filter(
                and_(
                    model.id == id,
                    model.tenant_id == tenant_id,
                    model.deleted_at.is_(None)
                )
            )
            .first()
        )

    @staticmethod
    def _get_all(
        db: Session,
        model: Type[T],
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        """
        Get all records with tenant isolation and pagination

        Args:
            db: Database session
            model: Model class
            tenant_id: Tenant ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return (
            db.query(model)
            .filter(
                and_(
                    model.tenant_id == tenant_id,
                    model.deleted_at.is_(None)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def _paginate(
        query: Query,
        skip: int = 0,
        limit: int = 100
    ) -> Query:
        """
        Apply pagination to query

        Args:
            query: SQLAlchemy query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Query with pagination applied
        """
        return query.offset(skip).limit(limit)

    @staticmethod
    def _soft_delete(
        db: Session,
        instance: T,
        user_id: int
    ) -> T:
        """
        Soft delete a record

        Args:
            db: Database session
            instance: Model instance to delete
            user_id: User performing the deletion

        Returns:
            Updated model instance
        """
        from datetime import datetime, timezone

        instance.deleted_at = datetime.now(timezone.utc)
        instance.updated_by = user_id
        db.commit()
        db.refresh(instance)
        return instance

    @staticmethod
    def _count(
        db: Session,
        model: Type[T],
        tenant_id: str
    ) -> int:
        """
        Count records with tenant isolation

        Args:
            db: Database session
            model: Model class
            tenant_id: Tenant ID

        Returns:
            Count of records
        """
        return (
            db.query(model)
            .filter(
                and_(
                    model.tenant_id == tenant_id,
                    model.deleted_at.is_(None)
                )
            )
            .count()
        )

    @staticmethod
    def _exists(
        db: Session,
        model: Type[T],
        id: int,
        tenant_id: str
    ) -> bool:
        """
        Check if record exists with tenant isolation

        Args:
            db: Database session
            model: Model class
            id: Record ID
            tenant_id: Tenant ID

        Returns:
            True if record exists, False otherwise
        """
        return (
            db.query(model)
            .filter(
                and_(
                    model.id == id,
                    model.tenant_id == tenant_id,
                    model.deleted_at.is_(None)
                )
            )
            .first()
        ) is not None
