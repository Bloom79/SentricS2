#!/usr/bin/env python3
"""
Comprehensive seed data script
Runs all seed scripts to populate the database with test data
All data is linked to the authenticated user (test@example.com)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
import subprocess
import argparse

def seed_all_data(tenant_id: str = "demo", user_email: str = "test@example.com"):
    """Run all seed scripts in order"""
    
    db: Session = next(get_db())
    
    try:
        # Verify user exists
        user = db.query(User).filter(
            User.email == user_email,
            User.tenant_id == tenant_id
        ).first()
        
        if not user:
            print(f"❌ User {user_email} not found in tenant {tenant_id}")
            print("   Please create the user first using create_test_user.py")
            sys.exit(1)
        
        print("=" * 60)
        print("Kronos EAM - Comprehensive Data Seeding")
        print("=" * 60)
        print(f"Tenant ID: {tenant_id}")
        print(f"User: {user.name} ({user.email})")
        print(f"User ID: {user.id}")
        print()
        
        # Scripts to run in order
        scripts = [
            {
                "name": "Seed Authenticated Data (Sites, Plants, Assets)",
                "script": "seed_authenticated_data.py",
                "args": [
                    "--tenant-id", tenant_id,
                    "--user-email", user_email,
                    "--user-name", user.name or "Test User",
                    "--user-role", "Admin"
                ]
            },
            {
                "name": "Seed CER Data (Communities, Members, Compliance)",
                "script": "seed_cer_data.py",
                "args": []
            },
            {
                "name": "Seed Workflows",
                "script": "seed_workflows.py",
                "args": []
            }
        ]
        
        # Run each script
        for script_info in scripts:
            print("-" * 60)
            print(f"Running: {script_info['name']}")
            print("-" * 60)
            
            script_path = os.path.join(os.path.dirname(__file__), script_info['script'])
            
            # Run script
            cmd = [sys.executable, script_path] + script_info['args']
            print(f"Command: {' '.join(cmd)}")
            print()
            
            result = subprocess.run(
                cmd,
                cwd=os.path.dirname(os.path.dirname(__file__)),
                capture_output=False,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Failed to run {script_info['script']}")
                db.rollback()
                sys.exit(1)
            
            print()
        
        print("=" * 60)
        print("✅ All seed data scripts completed successfully!")
        print("=" * 60)
        print()
        print("Data summary:")
        print("  - Sites and Plants")
        print("  - Assets and Components")
        print("  - CERs (Renewable Energy Communities)")
        print("  - CER Members and Assets")
        print("  - Compliance Requirements and Records")
        print("  - Documents")
        print("  - Workflows and Templates")
        print()
        print(f"All data is linked to user: {user_email}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Seed all data for authenticated user')
    parser.add_argument('--tenant-id', type=str, default='demo', help='Tenant ID')
    parser.add_argument('--user-email', type=str, default='test@example.com', help='User email')
    
    args = parser.parse_args()
    
    seed_all_data(
        tenant_id=args.tenant_id,
        user_email=args.user_email
    )

if __name__ == "__main__":
    main()

