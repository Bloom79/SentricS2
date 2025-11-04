#!/usr/bin/env python3
"""
Import schema and seed data dumps into database
Handles dependencies and safe user import
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_engine
from app.core.config import settings
from sqlalchemy import text
import argparse
from pathlib import Path

def import_sql_file(engine, file_path: str, description: str):
    """Import a SQL file into the database"""
    print(f"\n📥 Importing {description}...")
    print(f"   File: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"   ❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        sql_content = f.read()
    
    if not sql_content.strip():
        print(f"   ⚠️  File is empty, skipping...")
        return True
    
    try:
        with engine.connect() as conn:
            # Execute in a transaction
            trans = conn.begin()
            try:
                # Split by semicolon and execute statements
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                
                for i, statement in enumerate(statements, 1):
                    # Skip comments
                    if statement.startswith('--'):
                        continue
                    
                    try:
                        conn.execute(text(statement))
                        if i % 100 == 0:
                            print(f"   ... executed {i}/{len(statements)} statements")
                    except Exception as e:
                        # Some errors are expected (e.g., IF NOT EXISTS conflicts)
                        if 'already exists' not in str(e).lower() and 'duplicate' not in str(e).lower():
                            print(f"   ⚠️  Warning on statement {i}: {e}")
                
                trans.commit()
                print(f"   ✅ Import complete!")
                return True
            except Exception as e:
                trans.rollback()
                print(f"   ❌ Error: {e}")
                return False
    except Exception as e:
        print(f"   ❌ Failed to import: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Import database dumps')
    parser.add_argument('--schema', type=str, help='Schema dump file path')
    parser.add_argument('--seed', type=str, help='Seed data dump file path')
    parser.add_argument('--users', type=str, help='Safe user seed file path')
    parser.add_argument('--all', type=str, help='Directory containing dump files (will auto-detect)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Kronos EAM - Database Import")
    print("=" * 60)
    print()
    
    engine = get_engine()
    
    # Auto-detect files if --all is provided
    if args.all:
        dump_dir = Path(args.all)
        if not dump_dir.exists():
            print(f"❌ Directory not found: {dump_dir}")
            sys.exit(1)
        
        # Find most recent files
        schema_files = list(dump_dir.glob('schema_dump_*.sql'))
        seed_files = list(dump_dir.glob('seed_data_dump_*.sql'))
        user_files = list(dump_dir.glob('safe_user_seed_*.sql'))
        
        if schema_files:
            args.schema = str(max(schema_files, key=lambda p: p.stat().st_mtime))
        if seed_files:
            args.seed = str(max(seed_files, key=lambda p: p.stat().st_mtime))
        if user_files:
            args.users = str(max(user_files, key=lambda p: p.stat().st_mtime))
    
    # Import schema first
    if args.schema:
        if not import_sql_file(engine, args.schema, "schema"):
            print("\n❌ Schema import failed. Aborting.")
            sys.exit(1)
    else:
        print("⚠️  No schema file specified. Skipping schema import.")
        print("   Make sure the database schema already exists.")
    
    # Import seed data
    if args.seed:
        if not import_sql_file(engine, args.seed, "seed data"):
            print("\n⚠️  Seed data import had errors. Continuing...")
    else:
        print("⚠️  No seed data file specified. Skipping seed data import.")
    
    # Import users last (safe)
    if args.users:
        print("\n⚠️  IMPORTANT: Users will be imported with placeholder passwords!")
        print("   After import, update passwords for all users.")
        response = input("   Continue with user import? (yes/no): ")
        if response.lower() == 'yes':
            if not import_sql_file(engine, args.users, "users"):
                print("\n⚠️  User import had errors. Check manually.")
        else:
            print("   Skipping user import.")
    else:
        print("⚠️  No user seed file specified. Skipping user import.")
    
    print()
    print("=" * 60)
    print("✅ Import complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Verify data was imported correctly")
    print("  2. Update user passwords (if users were imported)")
    print("  3. Run any pending migrations: alembic upgrade head")

if __name__ == "__main__":
    main()

