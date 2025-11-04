#!/usr/bin/env python3
"""
Test script to verify all models and APIs can be imported correctly
This helps catch import errors, circular dependencies, and relationship issues
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all models can be imported"""
    print("=" * 60)
    print("Testing Model Imports")
    print("=" * 60)
    
    errors = []
    
    # Test base imports
    try:
        from app.models.base import BaseModel
        print("✓ BaseModel imported")
    except Exception as e:
        errors.append(f"BaseModel: {e}")
        print(f"✗ BaseModel failed: {e}")
    
    # Test CER models
    try:
        from app.models.cer import CER, CERMember, CERParticipationRequest
        print("✓ CER models imported")
    except Exception as e:
        errors.append(f"CER models: {e}")
        print(f"✗ CER models failed: {e}")
    
    # Test billing models
    try:
        from app.models.billing import (
            BillingStatement, Invoice, BillingTransaction, Settlement,
            BillingStatus, PaymentStatus, TransactionType, SettlementStatus
        )
        print("✓ Billing models imported")
    except Exception as e:
        errors.append(f"Billing models: {e}")
        print(f"✗ Billing models failed: {e}")
    
    # Test energy models
    try:
        from app.models.energy_transaction import EnergyTransaction, EnergySharingCalculation
        print("✓ Energy models imported")
    except Exception as e:
        errors.append(f"Energy models: {e}")
        print(f"✗ Energy models failed: {e}")
    
    # Test model __init__ imports
    try:
        from app.models import CER, BillingStatement, EnergyTransaction
        print("✓ Model __init__ imports work")
    except Exception as e:
        errors.append(f"Model __init__: {e}")
        print(f"✗ Model __init__ failed: {e}")
    
    return errors

def test_relationships():
    """Test that relationships are properly configured"""
    print("\n" + "=" * 60)
    print("Testing Model Relationships")
    print("=" * 60)
    
    errors = []
    
    try:
        from app.models.cer import CER
        from app.models.billing import BillingStatement
        
        # Check CER relationships
        cer_rels = [rel.key for rel in CER.__mapper__.relationships]
        print(f"✓ CER relationships: {', '.join(cer_rels)}")
        
        # Check BillingStatement relationships
        bs_rels = [rel.key for rel in BillingStatement.__mapper__.relationships]
        print(f"✓ BillingStatement relationships: {', '.join(bs_rels)}")
        
        # Verify back_populates are correct
        if 'billing_statements' in cer_rels:
            print("✓ CER.billing_statements relationship exists")
        else:
            errors.append("CER.billing_statements relationship missing")
            print("✗ CER.billing_statements relationship missing")
            
        if 'cer' in bs_rels:
            print("✓ BillingStatement.cer relationship exists")
        else:
            errors.append("BillingStatement.cer relationship missing")
            print("✗ BillingStatement.cer relationship missing")
            
    except Exception as e:
        errors.append(f"Relationship test: {e}")
        print(f"✗ Relationship test failed: {e}")
        import traceback
        traceback.print_exc()
    
    return errors

def test_api_endpoints():
    """Test that API endpoints can be imported"""
    print("\n" + "=" * 60)
    print("Testing API Endpoint Imports")
    print("=" * 60)
    
    errors = []
    
    try:
        from app.api.v1.endpoints.cer import router as cer_router
        print("✓ CER API router imported")
        print(f"  Routes: {len(cer_router.routes)} endpoints")
    except Exception as e:
        errors.append(f"CER API: {e}")
        print(f"✗ CER API failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from app.api.v1.endpoints.billing import router as billing_router
        print("✓ Billing API router imported")
        print(f"  Routes: {len(billing_router.routes)} endpoints")
    except Exception as e:
        errors.append(f"Billing API: {e}")
        print(f"✗ Billing API failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from app.api.v1.endpoints.energy import router as energy_router
        print("✓ Energy API router imported")
        print(f"  Routes: {len(energy_router.routes)} endpoints")
    except Exception as e:
        errors.append(f"Energy API: {e}")
        print(f"✗ Energy API failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from app.api.v1.api import api_router
        print("✓ Main API router imported")
        print(f"  Total routes: {len(api_router.routes)}")
    except Exception as e:
        errors.append(f"Main API router: {e}")
        print(f"✗ Main API router failed: {e}")
        import traceback
        traceback.print_exc()
    
    return errors

def test_services():
    """Test that services can be imported"""
    print("\n" + "=" * 60)
    print("Testing Service Imports")
    print("=" * 60)
    
    errors = []
    
    try:
        from app.services.cer_service import cer_service
        print("✓ CER service imported")
    except Exception as e:
        errors.append(f"CER service: {e}")
        print(f"✗ CER service failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from app.services.billing_service import billing_service
        print("✓ Billing service imported")
    except Exception as e:
        errors.append(f"Billing service: {e}")
        print(f"✗ Billing service failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from app.services.energy_service import energy_service
        print("✓ Energy service imported")
    except Exception as e:
        errors.append(f"Energy service: {e}")
        print(f"✗ Energy service failed: {e}")
        import traceback
        traceback.print_exc()
    
    return errors

def test_schemas():
    """Test that schemas can be imported"""
    print("\n" + "=" * 60)
    print("Testing Schema Imports")
    print("=" * 60)
    
    errors = []
    
    try:
        from app.schemas.cer import CERResponse, CERCreate, CERMemberResponse
        print("✓ CER schemas imported")
    except Exception as e:
        errors.append(f"CER schemas: {e}")
        print(f"✗ CER schemas failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from app.schemas.billing import (
            BillingStatementResponse, BillingTransactionResponse,
            SettlementResponse, BillingOverviewResponse
        )
        print("✓ Billing schemas imported")
    except Exception as e:
        errors.append(f"Billing schemas: {e}")
        print(f"✗ Billing schemas failed: {e}")
        import traceback
        traceback.print_exc()
    
    return errors

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("API and Model Import Test Suite")
    print("=" * 60 + "\n")
    
    all_errors = []
    
    # Run all tests
    all_errors.extend(test_imports())
    all_errors.extend(test_relationships())
    all_errors.extend(test_api_endpoints())
    all_errors.extend(test_services())
    all_errors.extend(test_schemas())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if all_errors:
        print(f"\n✗ Found {len(all_errors)} error(s):")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        return 1
    else:
        print("\n✓ All tests passed! APIs and models are ready to use.")
        return 0

if __name__ == "__main__":
    sys.exit(main())

