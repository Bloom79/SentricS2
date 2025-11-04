#!/usr/bin/env python3
"""
Initialize GCP Cloud SQL database from dump files
Can be run locally (with Cloud SQL Proxy) or in Cloud Build
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_engine
from app.core.config import settings
from sqlalchemy import text
import argparse
from pathlib import Path
import subprocess

def check_cloud_sql_proxy():
    """Check if Cloud SQL Proxy is available"""
    try:
        result = subprocess.run(['cloud-sql-proxy', '--version'], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def import_from_gcs(gcs_path: str, instance_name: str, database_name: str):
    """Import SQL file from GCS to Cloud SQL"""
    print(f"📥 Importing from GCS: {gcs_path}")
    
    try:
        # Use gcloud sql import
        cmd = [
            'gcloud', 'sql', 'import', 'sql',
            instance_name,
            gcs_path,
            f'--database={database_name}',
            '--quiet'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Import successful")
            return True
        else:
            print(f"❌ Import failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def import_local_file(file_path: str, engine):
    """Import SQL file directly using SQLAlchemy"""
    print(f"📥 Importing local file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        sql_content = f.read()
    
    if not sql_content.strip():
        print("⚠️  File is empty, skipping...")
        return True
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                
                for i, statement in enumerate(statements, 1):
                    if statement.startswith('--'):
                        continue
                    
                    try:
                        conn.execute(text(statement))
                        if i % 100 == 0:
                            print(f"   ... executed {i}/{len(statements)} statements")
                    except Exception as e:
                        if 'already exists' not in str(e).lower() and 'duplicate' not in str(e).lower():
                            print(f"   ⚠️  Warning on statement {i}: {e}")
                
                trans.commit()
                print("✅ Import complete!")
                return True
            except Exception as e:
                trans.rollback()
                print(f"❌ Error: {e}")
                return False
    except Exception as e:
        print(f"❌ Failed to import: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Initialize GCP Cloud SQL database')
    parser.add_argument('--schema', type=str, help='Schema dump file (local or gs:// path)')
    parser.add_argument('--seed', type=str, help='Seed data dump file (local or gs:// path)')
    parser.add_argument('--users', type=str, help='User seed file (local or gs:// path)')
    parser.add_argument('--instance', type=str, help='Cloud SQL instance name')
    parser.add_argument('--database', type=str, default='kronos_eam', help='Database name')
    parser.add_argument('--enable-postgis', action='store_true', help='Enable PostGIS extension')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GCP Cloud SQL Database Initialization")
    print("=" * 60)
    print()
    
    # Determine if we're using GCS or local files
    use_gcs = False
    if args.schema and args.schema.startswith('gs://'):
        use_gcs = True
    elif args.seed and args.seed.startswith('gs://'):
        use_gcs = True
    elif args.users and args.users.startswith('gs://'):
        use_gcs = True
    
    if use_gcs and not args.instance:
        print("❌ Cloud SQL instance name required for GCS imports")
        sys.exit(1)
    
    # Enable PostGIS if requested
    if args.enable_postgis:
        print("📦 Enabling PostGIS extension...")
        if use_gcs:
            # Create temporary SQL file
            with open('/tmp/enable_postgis.sql', 'w') as f:
                f.write("CREATE EXTENSION IF NOT EXISTS postgis;\n")
                f.write("CREATE EXTENSION IF NOT EXISTS postgis_topology;\n")
            
            # Upload and import
            import subprocess
            subprocess.run(['gsutil', 'cp', '/tmp/enable_postgis.sql', 
                          args.schema.replace('schema.sql', 'enable_postgis.sql').replace('gs://', 'gs://')])
            import_from_gcs(args.schema.replace('schema.sql', 'enable_postgis.sql'), 
                          args.instance, args.database)
        else:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology;"))
                conn.commit()
            print("✅ PostGIS enabled")
    
    # Import schema
    if args.schema:
        if use_gcs:
            if not import_from_gcs(args.schema, args.instance, args.database):
                sys.exit(1)
        else:
            engine = get_engine()
            if not import_local_file(args.schema, engine):
                sys.exit(1)
    
    # Import seed data
    if args.seed:
        if use_gcs:
            if not import_from_gcs(args.seed, args.instance, args.database):
                print("⚠️  Seed data import had errors")
        else:
            engine = get_engine()
            if not import_local_file(args.seed, engine):
                print("⚠️  Seed data import had errors")
    
    # Import users
    if args.users:
        print("\n⚠️  IMPORTANT: Users will be imported with placeholder passwords!")
        response = input("Continue with user import? (yes/no): ")
        if response.lower() == 'yes':
            if use_gcs:
                if not import_from_gcs(args.users, args.instance, args.database):
                    print("⚠️  User import had errors")
            else:
                engine = get_engine()
                if not import_local_file(args.users, engine):
                    print("⚠️  User import had errors")
            print("\n⚠️  REMEMBER: Update all user passwords after import!")
        else:
            print("Skipping user import.")
    
    print()
    print("=" * 60)
    print("✅ Initialization complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

