#!/usr/bin/env python3
"""
Dump database schema (structure only) to SQL file
Creates a complete schema dump without data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_engine
from app.core.config import settings
from sqlalchemy import inspect, text
import subprocess
from datetime import datetime

def dump_schema_with_pg_dump():
    """Use pg_dump to dump schema only"""
    print("📦 Dumping database schema using pg_dump...")
    
    # Parse DATABASE_URL
    db_url = str(settings.DATABASE_URL)
    
    # Extract connection details
    if db_url.startswith('postgresql://'):
        # Format: postgresql://user:password@host:port/database
        parts = db_url.replace('postgresql://', '').split('@')
        if len(parts) == 2:
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')
            if len(host_db) == 2:
                host_port = host_db[0].split(':')
                host = host_port[0]
                port = host_port[1] if len(host_port) > 1 else '5432'
                database = host_db[1].split('?')[0]
                user = user_pass[0]
                password = ':'.join(user_pass[1:]) if len(user_pass) > 1 else ''
                
                # Use PGPASSWORD environment variable
                env = os.environ.copy()
                if password:
                    env['PGPASSWORD'] = password
                
                output_file = f"schema_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
                
                cmd = [
                    'pg_dump',
                    '-h', host,
                    '-p', port,
                    '-U', user,
                    '-d', database,
                    '--schema-only',  # Schema only, no data
                    '--no-owner',     # Don't include ownership commands
                    '--no-privileges', # Don't include privilege commands
                    '-f', output_file
                ]
                
                try:
                    subprocess.run(cmd, env=env, check=True)
                    print(f"✅ Schema dumped to: {output_file}")
                    return output_file
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error running pg_dump: {e}")
                    return None
                except FileNotFoundError:
                    print("❌ pg_dump not found. Trying SQLAlchemy method...")
                    return dump_schema_with_sqlalchemy()
    
    return dump_schema_with_sqlalchemy()

def dump_schema_with_sqlalchemy():
    """Dump schema using SQLAlchemy introspection"""
    print("📦 Dumping database schema using SQLAlchemy...")
    
    engine = get_engine()
    inspector = inspect(engine)
    
    output_file = f"schema_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    with open(output_file, 'w') as f:
        f.write("-- Kronos EAM Database Schema Dump\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write("-- This file contains only the database structure (no data)\n\n")
        
        # Enable PostGIS extension
        f.write("-- Enable PostGIS extension\n")
        f.write("CREATE EXTENSION IF NOT EXISTS postgis;\n")
        f.write("CREATE EXTENSION IF NOT EXISTS postgis_topology;\n\n")
        
        # Get all tables
        tables = inspector.get_table_names()
        
        for table_name in sorted(tables):
            # Skip Alembic version table structure (will be handled by migrations)
            if table_name == 'alembic_version':
                continue
                
            f.write(f"\n-- Table: {table_name}\n")
            
            # Get columns
            columns = inspector.get_columns(table_name)
            if columns:
                f.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                col_defs = []
                for col in columns:
                    col_def = f"    {col['name']} {col['type']}"
                    if not col.get('nullable', True):
                        col_def += " NOT NULL"
                    if col.get('default') is not None:
                        default = col['default']
                        if isinstance(default, str):
                            default = f"'{default}'"
                        col_def += f" DEFAULT {default}"
                    col_defs.append(col_def)
                f.write(",\n".join(col_defs))
                f.write("\n);\n")
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                for idx in indexes:
                    idx_name = idx['name']
                    idx_cols = ', '.join(idx['column_names'])
                    unique = 'UNIQUE ' if idx.get('unique', False) else ''
                    f.write(f"CREATE {unique}INDEX IF NOT EXISTS {idx_name} ON {table_name} ({idx_cols});\n")
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                for fk in foreign_keys:
                    fk_name = fk.get('name', f"{table_name}_{fk['constrained_columns'][0]}_fkey")
                    fk_cols = ', '.join(fk['constrained_columns'])
                    ref_table = fk['referred_table']
                    ref_cols = ', '.join(fk['referred_columns'])
                    f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT {fk_name} FOREIGN KEY ({fk_cols}) REFERENCES {ref_table}({ref_cols});\n")
    
    print(f"✅ Schema dumped to: {output_file}")
    return output_file

def main():
    """Main function"""
    print("=" * 60)
    print("Kronos EAM - Database Schema Dump")
    print("=" * 60)
    print()
    
    # Try pg_dump first (more complete), fallback to SQLAlchemy
    output_file = dump_schema_with_pg_dump()
    
    if output_file:
        print()
        print("=" * 60)
        print(f"✅ Schema dump complete: {output_file}")
        print("=" * 60)
        print()
        print("Note: This dump contains only structure, no data.")
        print("Use dump_seed_data.py to dump seed data separately.")
    else:
        print("❌ Failed to dump schema")
        sys.exit(1)

if __name__ == "__main__":
    main()

