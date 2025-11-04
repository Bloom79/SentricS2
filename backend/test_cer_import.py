#!/usr/bin/env python3
"""Test CER model import and basic query"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing CER model import...")
    from app.models.cer import CER
    print("✓ CER model imported successfully")
    
    print("Testing billing model import...")
    from app.models.billing import BillingStatement, Invoice, BillingTransaction, Settlement
    print("✓ Billing models imported successfully")
    
    print("Testing CER relationships...")
    cer_rels = [rel.key for rel in CER.__mapper__.relationships]
    print(f"✓ CER relationships: {cer_rels}")
    
    print("Testing BillingStatement relationships...")
    bs_rels = [rel.key for rel in BillingStatement.__mapper__.relationships]
    print(f"✓ BillingStatement relationships: {bs_rels}")
    
    print("\nAll imports and relationships configured successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

