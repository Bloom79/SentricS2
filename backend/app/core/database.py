"""
Database configuration with multi-tenant support and PostGIS
Consolidated from Kronos EAM with PostGIS support from Sentrics
"""

from typing import Generator, Optional, Dict, Any
from sqlalchemy import create_engine, event, Engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, Query
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import contextmanager
import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Global registry for tenant-specific engines
_tenant_engines: Dict[str, Engine] = {}
_tenant_sessions: Dict[str, sessionmaker] = {}


class TenantAwareQuery(Query):
    """Custom query class that automatically filters by tenant_id"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_id = None
    
    def set_tenant(self, tenant_id: str):
        """Set the tenant for this query"""
        self._tenant_id = tenant_id
        return self
    
    def filter_by_tenant(self):
        """Apply tenant filter if the model has tenant_id column"""
        if self._tenant_id and hasattr(self.column_descriptions[0]['type'], 'tenant_id'):
            return self.filter_by(tenant_id=self._tenant_id)
        return self


def get_engine(tenant_id: Optional[str] = None, **kwargs) -> Engine:
    """
    Get or create a database engine for a specific tenant
    Enhanced with PostGIS support
    """
    max_retries = 30
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            # Use tenant-specific engine if provided, otherwise use default
            if tenant_id and tenant_id in _tenant_engines:
                return _tenant_engines[tenant_id]
            
            # Default engine (shared for now, can be tenant-specific)
            if 'default' not in _tenant_engines:
                engine = create_engine(
                    str(settings.DATABASE_URL),
                    poolclass=QueuePool,
                    pool_size=settings.DB_POOL_SIZE,
                    max_overflow=settings.DB_MAX_OVERFLOW,
                    pool_pre_ping=settings.DB_POOL_PRE_PING,
                    echo=settings.DEBUG,
                    **kwargs
                )
                
                # Enable PostGIS extension on first connection
                @event.listens_for(engine, "connect")
                def enable_postgis(dbapi_conn, connection_record):
                    """Enable PostGIS extension on connection"""
                    try:
                        with dbapi_conn.cursor() as cursor:
                            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
                            dbapi_conn.commit()
                    except Exception as e:
                        logger.warning(f"Could not enable PostGIS: {e}")
                
                _tenant_engines['default'] = engine
            
            return _tenant_engines['default']
            
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise


def get_session(tenant_id: Optional[str] = None) -> Session:
    """Get database session with tenant context"""
    engine = get_engine(tenant_id)
    
    if tenant_id and tenant_id in _tenant_sessions:
        SessionLocal = _tenant_sessions[tenant_id]
    else:
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            query_cls=TenantAwareQuery
        )
        if tenant_id:
            _tenant_sessions[tenant_id] = SessionLocal
    
    session = SessionLocal()
    
    # Set tenant context
    if tenant_id:
        session.tenant_id = tenant_id
    
    return session


def get_db(tenant_id: Optional[str] = None) -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    """
    db = get_session(tenant_id)
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context(tenant_id: Optional[str] = None):
    """Context manager for database sessions"""
    db = get_session(tenant_id)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database - create tables and enable PostGIS"""
    engine = get_engine()
    
    # Enable PostGIS extensions
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology;"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized with PostGIS support")

