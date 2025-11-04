#!/usr/bin/env python3
"""
Dump both schema and seed data
Combines dump_schema.py and dump_seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import dump functions
sys.path.insert(0, os.path.dirname(__file__))
from dump_schema import dump_schema_with_pg_dump, dump_schema_with_sqlalchemy
from dump_seed_data import dump_seed_data, create_safe_user_seed
from datetime import datetime

def main():
    """Main function"""
    print("=" * 60)
    print("Kronos EAM - Complete Database Dump")
    print("=" * 60)
    print()
    print("This will create:")
    print("  1. Schema dump (structure only)")
    print("  2. Seed data dump (data without sensitive auth info)")
    print("  3. Safe user seed (users with placeholder passwords)")
    print()
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    print()
    
    # Dump schema
    print("Step 1/3: Dumping schema...")
    schema_file = dump_schema_with_pg_dump()
    if not schema_file:
        schema_file = dump_schema_with_sqlalchemy()
    print()
    
    # Dump seed data
    print("Step 2/3: Dumping seed data...")
    seed_file = dump_seed_data()
    print()
    
    # Create safe user seed
    print("Step 3/3: Creating safe user seed...")
    user_file = create_safe_user_seed()
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Complete dump finished!")
    print("=" * 60)
    print()
    print("Files created:")
    if schema_file:
        print(f"  📄 {schema_file} - Database schema (structure)")
    if seed_file:
        print(f"  📄 {seed_file} - Seed data (all tables)")
    if user_file:
        print(f"  📄 {user_file} - Safe user seed (users with placeholder passwords)")
    print()
    print("Next steps:")
    print("  1. Review the generated SQL files")
    print("  2. Use import_dumps.py to import them into a new database")
    print("  3. Update user passwords after import")

if __name__ == "__main__":
    main()

