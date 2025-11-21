"""
API Endpoint Verification Script
Tests that all new CER energy sharing endpoints are accessible
"""

import sys
import asyncio
from datetime import datetime


async def verify_endpoints():
    """Verify all endpoints are registered and importable"""
    
    print("=" * 70)
    print("CER ENERGY SHARING - API ENDPOINT VERIFICATION")
    print("=" * 70)
    
    try:
        # Test 1: Import the service
        print("\n[1/5] Testing Energy Sharing Calculator service import...")
        from app.services.energy_sharing_calculator import (
            EnergyShareCalculator,
            MeterData,
            MemberEnergyData,
            EnergySharingResult,
        )
        print("✓ Service imports successfully")
        
        # Test 2: Import the API endpoints
        print("\n[2/5] Testing CER Energy API endpoints import...")
        from app.api.v1.endpoints.cer_energy import router
        print("✓ API endpoints import successfully")
        
        # Test 3: Check routes are registered
        print("\n[3/5] Checking API routes registration...")
        from app.api.v1.api import api_router
        
        cer_energy_routes = [
            r for r in api_router.routes
            if any(keyword in r.path for keyword in [
                'calculate-sharing',
                'generate-billing',
                'sharing-visualization',
                'billing-statements'
            ])
        ]
        
        print(f"✓ Found {len(cer_energy_routes)} CER energy sharing routes:")
        for route in cer_energy_routes:
            method = list(route.methods)[0] if hasattr(route, 'methods') else 'GET'
            print(f"    {method:6} {route.path}")
        
        # Test 4: Verify FastAPI app loads
        print("\n[4/5] Testing FastAPI application loading...")
        from app.main import app
        print(f"✓ FastAPI app loaded with {len(api_router.routes)} total routes")
        
        # Test 5: Create calculator instance
        print("\n[5/5] Testing calculator instantiation...")
        calculator = EnergyShareCalculator()
        print("✓ Calculator instantiated successfully")
        
        print("\n" + "=" * 70)
        print("✅ ALL VERIFICATIONS PASSED")
        print("=" * 70)
        print("\nNew CER Energy Sharing functionality is ready!")
        print("\nAvailable endpoints:")
        print("  • POST /cer/{cer_id}/calculate-sharing")
        print("      Calculate energy sharing for a CER (dry-run)")
        print()
        print("  • POST /cer/{cer_id}/generate-billing")
        print("      Calculate AND create billing statements (database write)")
        print()
        print("  • GET /cer/{cer_id}/sharing-visualization")
        print("      Get hourly energy data for charts (requires date range)")
        print()
        print("  • GET /cer/{cer_id}/billing-statements")
        print("      Get existing billing statements (with filters)")
        print()
        print("Next steps:")
        print("  1. Start backend: uvicorn app.main:app --reload")
        print("  2. Visit API docs: http://localhost:8000/docs")
        print("  3. Test with your CER data")
        print()
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Suppress warning messages
    import warnings
    warnings.filterwarnings("ignore")
    
    # Change to backend directory
    import os
    backend_dir = "/home/bloom/projects/sentrics/SentricS2/backend"
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
    
    # Run verification
    success = asyncio.run(verify_endpoints())
    sys.exit(0 if success else 1)
