#!/usr/bin/env python3
"""
Dump seed data from database to SQL INSERT statements
Excludes sensitive user authentication data (passwords, MFA secrets, etc.)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_db, get_engine
from sqlalchemy import inspect, text, MetaData, Table
from sqlalchemy.orm import Session
from datetime import datetime
import json

# Tables to exclude from seed data dump
EXCLUDED_TABLES = {
    'alembic_version',  # Migration tracking
}

# Tables with sensitive data - exclude specific columns
SENSITIVE_COLUMNS = {
    'users': {
        'password_hash',  # Never dump password hashes
        'mfa_secret',     # Never dump MFA secrets
        'failed_login_attempts',  # Security sensitive
        'locked_until',   # Security sensitive
    },
    'tenants': {
        # No sensitive columns, but we'll keep structure
    }
}

def serialize_value(value):
    """Serialize a value for SQL INSERT"""
    if value is None:
        return 'NULL'
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, dict) or isinstance(value, list):
        # JSON columns
        return f"'{json.dumps(value).replace(chr(39), chr(39)+chr(39))}'::jsonb"
    elif isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    else:
        # String - escape single quotes
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

def dump_table_data(db: Session, table_name: str, output_file):
    """Dump data from a single table"""
    inspector = inspect(get_engine())
    
    # Check if table exists
    if table_name not in inspector.get_table_names():
        return
    
    # Get columns
    columns = inspector.get_columns(table_name)
    if not columns:
        return
    
    # Filter out sensitive columns
    if table_name in SENSITIVE_COLUMNS:
        excluded_cols = SENSITIVE_COLUMNS[table_name]
        columns = [col for col in columns if col['name'] not in excluded_cols]
    
    col_names = [col['name'] for col in columns]
    
    # Query data
    query = f"SELECT {', '.join(col_names)} FROM {table_name} WHERE deleted_at IS NULL"
    result = db.execute(text(query))
    rows = result.fetchall()
    
    if not rows:
        return
    
    output_file.write(f"\n-- Table: {table_name}\n")
    output_file.write(f"-- {len(rows)} rows\n")
    
    # Generate INSERT statements
    for row in rows:
        values = []
        for i, col in enumerate(columns):
            value = row[i]
            values.append(serialize_value(value))
        
        col_list = ', '.join(col_names)
        val_list = ', '.join(values)
        output_file.write(f"INSERT INTO {table_name} ({col_list}) VALUES ({val_list}) ON CONFLICT DO NOTHING;\n")

def dump_seed_data():
    """Dump all seed data"""
    print("📦 Dumping seed data from database...")
    
    db: Session = next(get_db())
    inspector = inspect(get_engine())
    
    output_file_name = f"seed_data_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    with open(output_file_name, 'w') as f:
        f.write("-- Kronos EAM Seed Data Dump\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write("-- This file contains seed data for development/testing\n")
        f.write("-- Sensitive authentication data (passwords, MFA secrets) are excluded\n\n")
        
        f.write("-- Disable foreign key checks temporarily\n")
        f.write("SET session_replication_role = 'replica';\n\n")
        
        # Get all tables in dependency order
        tables = inspector.get_table_names()
        
        # Order tables by dependencies (tenants first, then users, then others)
        ordered_tables = []
        
        # 1. Tenants first (no dependencies)
        if 'tenants' in tables:
            ordered_tables.append('tenants')
        
        # 2. Users (depends on tenants)
        if 'users' in tables:
            ordered_tables.append('users')
        
        # 3. Sites (depends on tenants)
        if 'sites' in tables:
            ordered_tables.append('sites')
        
        # 4. Plants (depends on tenants, sites)
        if 'plants' in tables:
            ordered_tables.append('plants')
        
        # 5. CER (depends on tenants)
        if 'cer_configuration' in tables:
            ordered_tables.append('cer_configuration')
        
        # 6. Workflow templates (depends on tenants)
        if 'workflow_templates' in tables:
            ordered_tables.append('workflow_templates')
        
        # 7. Workflows (depends on tenants, plants, workflow_templates)
        if 'workflows' in tables:
            ordered_tables.append('workflows')
        
        # 8. Workflow phases (depends on workflows)
        if 'workflow_phases' in tables:
            ordered_tables.append('workflow_phases')
        
        # 9. Assets (depends on tenants, plants)
        if 'assets' in tables:
            ordered_tables.append('assets')
        
        # 10. Asset types (depends on tenants)
        if 'asset_types' in tables:
            ordered_tables.append('asset_types')
        
        # 11. Documents (depends on tenants, plants, cer)
        if 'documents' in tables:
            ordered_tables.append('documents')
        
        # 12. Compliance requirements (depends on tenants)
        if 'compliance_requirements' in tables:
            ordered_tables.append('compliance_requirements')
        
        # 13. Compliance records (depends on compliance_requirements, plants, cer)
        if 'compliance_records' in tables:
            ordered_tables.append('compliance_records')
        
        # 14. CER members (depends on cer, users)
        if 'cer_members' in tables:
            ordered_tables.append('cer_members')
        
        # 15. Add remaining tables
        for table in sorted(tables):
            if table not in ordered_tables and table not in EXCLUDED_TABLES:
                ordered_tables.append(table)
        
        # Dump each table
        total_rows = 0
        for table_name in ordered_tables:
            if table_name in EXCLUDED_TABLES:
                continue
            
            try:
                row_count_before = total_rows
                dump_table_data(db, table_name, f)
                
                # Count rows inserted
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE deleted_at IS NULL"))
                row_count = result.scalar()
                if row_count > 0:
                    total_rows += row_count
                    print(f"  ✅ {table_name}: {row_count} rows")
            except Exception as e:
                print(f"  ⚠️  {table_name}: Error - {e}")
                f.write(f"-- Error dumping {table_name}: {e}\n")
        
        f.write("\n-- Re-enable foreign key checks\n")
        f.write("SET session_replication_role = 'origin';\n\n")
        
        f.write(f"-- Total rows dumped: {total_rows}\n")
    
    db.close()
    print(f"\n✅ Seed data dumped to: {output_file_name}")
    print(f"   Total rows: {total_rows}")
    return output_file_name

def create_safe_user_seed():
    """Create a safe user seed script with placeholder passwords"""
    print("\n📝 Creating safe user seed script...")
    
    db: Session = next(get_db())
    
    output_file_name = f"safe_user_seed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    with open(output_file_name, 'w') as f:
        f.write("-- Safe User Seed Data\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write("-- This file creates users with placeholder passwords\n")
        f.write("-- IMPORTANT: Update passwords after import!\n\n")
        
        # Get users from database
        result = db.execute(text("""
            SELECT id, tenant_id, name, email, role, status, email_verified, 
                   phone, language, timezone, authorized_plants, preferences
            FROM users 
            WHERE deleted_at IS NULL
        """))
        
        users = result.fetchall()
        
        if users:
            f.write("-- Users (without passwords - update after import)\n")
            for user in users:
                user_id, tenant_id, name, email, role, status, email_verified, \
                phone, language, timezone, authorized_plants, preferences = user
                
                # Use placeholder password hash (bcrypt hash of "CHANGE_ME")
                # This is a known hash that users must change
                placeholder_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYxh1zLJdG2"
                
                authorized_plants_str = "NULL"
                if authorized_plants:
                    authorized_plants_str = f"'{json.dumps(authorized_plants)}'::jsonb"
                
                preferences_str = "NULL"
                if preferences:
                    preferences_str = f"'{json.dumps(preferences)}'::jsonb"
                
                phone_str = f"'{phone}'" if phone else "NULL"
                language_str = f"'{language}'" if language else "'en'"
                timezone_str = f"'{timezone}'" if timezone else "'Europe/Rome'"
                
                f.write(f"""
INSERT INTO users (
    id, tenant_id, name, email, password_hash, role, status, 
    email_verified, phone, language, timezone, authorized_plants, preferences,
    created_at, updated_at
) VALUES (
    {user_id}, '{tenant_id}', '{name}', '{email}', '{placeholder_hash}',
    '{role}', '{status}', {email_verified}, {phone_str}, 
    {language_str}, {timezone_str}, {authorized_plants_str}, {preferences_str},
    NOW(), NOW()
) ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    role = EXCLUDED.role,
    status = EXCLUDED.status,
    email_verified = EXCLUDED.email_verified,
    phone = EXCLUDED.phone,
    language = EXCLUDED.language,
    timezone = EXCLUDED.timezone,
    authorized_plants = EXCLUDED.authorized_plants,
    preferences = EXCLUDED.preferences,
    updated_at = NOW();
""")
            
            f.write("\n-- IMPORTANT: After importing, reset passwords for all users!\n")
            f.write("-- Use: UPDATE users SET password_hash = '<new_hash>' WHERE email = '<email>';\n")
        
        print(f"✅ Safe user seed created: {output_file_name}")
    
    db.close()
    return output_file_name

def main():
    """Main function"""
    print("=" * 60)
    print("Kronos EAM - Seed Data Dump")
    print("=" * 60)
    print()
    print("⚠️  This will dump seed data excluding sensitive authentication data")
    print()
    
    # Dump seed data
    seed_file = dump_seed_data()
    
    # Create safe user seed
    user_file = create_safe_user_seed()
    
    print()
    print("=" * 60)
    print("✅ Seed data dump complete!")
    print("=" * 60)
    print()
    print(f"Files created:")
    print(f"  1. {seed_file} - Seed data (all tables)")
    print(f"  2. {user_file} - Safe user seed (with placeholder passwords)")
    print()
    print("⚠️  IMPORTANT:")
    print("  - User passwords are NOT included in the dump")
    print("  - Update passwords after importing the user seed")
    print("  - Review the data before importing to production")

if __name__ == "__main__":
    main()

