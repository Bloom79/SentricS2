#!/usr/bin/env python3
"""
Quick verification that the FastAPI app can be instantiated without errors
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Verify app can be imported and instantiated"""
    print("Verifying FastAPI app startup...")
    
    try:
        from app.main import app
        print("✓ App imported successfully")
        
        # Count routes
        routes = [r for r in app.routes if hasattr(r, 'path')]
        print(f"✓ Total routes registered: {len(routes)}")
        
        # Check for CER routes
        cer_routes = [r for r in routes if '/cer' in r.path]
        print(f"✓ CER routes: {len(cer_routes)}")
        
        # Check for billing routes
        billing_routes = [r for r in routes if '/billing' in r.path]
        print(f"✓ Billing routes: {len(billing_routes)}")
        
        # Check for energy routes
        energy_routes = [r for r in routes if '/energy' in r.path or '/cer/communities' in r.path]
        print(f"✓ Energy routes: {len(energy_routes)}")
        
        print("\n✅ Server can start successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

