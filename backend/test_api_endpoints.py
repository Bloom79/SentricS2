#!/usr/bin/env python3
"""
Integration test script to verify API endpoints are working correctly
Tests CER, Billing, and Energy APIs
"""
import sys
import os
import requests
import json
from typing import Optional

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"

def test_endpoint(method: str, endpoint: str, expected_status: int = 200, 
                 data: Optional[dict] = None, headers: Optional[dict] = None) -> tuple[bool, dict]:
    """Test an API endpoint"""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=5)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            return False, {"error": f"Unsupported method: {method}"}
        
        success = response.status_code == expected_status
        result = {
            "status_code": response.status_code,
            "expected": expected_status,
            "success": success,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:200]
        }
        
        return success, result
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Connection refused - is the server running at {BASE_URL}?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout"}
    except Exception as e:
        return False, {"error": str(e)}


def test_cer_endpoints():
    """Test CER endpoints"""
    print("\n" + "=" * 60)
    print("Testing CER Endpoints")
    print("=" * 60)
    
    results = []
    
    # Test GET /cer/communities (should work even if empty)
    print("\n1. Testing GET /cer/communities")
    success, result = test_endpoint("GET", "/cer/communities", expected_status=200)
    results.append(("GET /cer/communities", success, result))
    if success:
        print(f"   ✓ Status: {result['status_code']}")
    else:
        print(f"   ✗ Failed: {result.get('error', result)}")
    
    # Test GET /cer/participation-requests
    print("\n2. Testing GET /cer/participation-requests")
    success, result = test_endpoint("GET", "/cer/participation-requests", expected_status=200)
    results.append(("GET /cer/participation-requests", success, result))
    if success:
        print(f"   ✓ Status: {result['status_code']}")
    else:
        print(f"   ✗ Failed: {result.get('error', result)}")
    
    return results


def test_billing_endpoints():
    """Test Billing endpoints"""
    print("\n" + "=" * 60)
    print("Testing Billing Endpoints")
    print("=" * 60)
    
    results = []
    
    # Test GET /billing/statements (should work even if empty)
    print("\n1. Testing GET /billing/statements")
    success, result = test_endpoint("GET", "/billing/statements", expected_status=200)
    results.append(("GET /billing/statements", success, result))
    if success:
        print(f"   ✓ Status: {result['status_code']}")
    else:
        print(f"   ✗ Failed: {result.get('error', result)}")
    
    # Test GET /billing/transactions
    print("\n2. Testing GET /billing/transactions")
    success, result = test_endpoint("GET", "/billing/transactions", expected_status=200)
    results.append(("GET /billing/transactions", success, result))
    if success:
        print(f"   ✓ Status: {result['status_code']}")
    else:
        print(f"   ✗ Failed: {result.get('error', result)}")
    
    # Test GET /billing/settlements
    print("\n3. Testing GET /billing/settlements")
    success, result = test_endpoint("GET", "/billing/settlements", expected_status=200)
    results.append(("GET /billing/settlements", success, result))
    if success:
        print(f"   ✓ Status: {result['status_code']}")
    else:
        print(f"   ✗ Failed: {result.get('error', result)}")
    
    return results


def test_energy_endpoints():
    """Test Energy endpoints"""
    print("\n" + "=" * 60)
    print("Testing Energy Endpoints")
    print("=" * 60)
    
    results = []
    
    # Test GET /energy/transactions (should work even if empty)
    print("\n1. Testing GET /energy/transactions")
    success, result = test_endpoint("GET", "/energy/transactions", expected_status=200)
    results.append(("GET /energy/transactions", success, result))
    if success:
        print(f"   ✓ Status: {result['status_code']}")
    else:
        print(f"   ✗ Failed: {result.get('error', result)}")
    
    return results


def test_api_health():
    """Test API health/root endpoint"""
    print("\n" + "=" * 60)
    print("Testing API Health")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✓ API docs accessible")
            return True
        else:
            print(f"✗ API docs returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {BASE_URL} - is the server running?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all API tests"""
    print("\n" + "=" * 60)
    print("API Endpoint Integration Test Suite")
    print("=" * 60)
    print(f"\nTesting against: {BASE_URL}")
    print(f"API Prefix: {API_PREFIX}")
    
    # Check if server is running
    if not test_api_health():
        print("\n⚠️  Server appears to be down. Starting tests anyway...")
        print("   (Some tests may fail due to connection errors)")
    
    all_results = []
    
    # Run endpoint tests
    all_results.extend(test_cer_endpoints())
    all_results.extend(test_billing_endpoints())
    all_results.extend(test_energy_endpoints())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in all_results if success)
    total = len(all_results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed < total:
        print("\nFailed tests:")
        for endpoint, success, result in all_results:
            if not success:
                print(f"  ✗ {endpoint}")
                if "error" in result:
                    print(f"    Error: {result['error']}")
                elif result.get("status_code"):
                    print(f"    Status: {result['status_code']} (expected {result.get('expected', 'N/A')})")
    
    if passed == total:
        print("\n✓ All API endpoints are accessible!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} endpoint(s) failed")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)

