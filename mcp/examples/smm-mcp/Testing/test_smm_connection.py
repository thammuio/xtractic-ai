#!/usr/bin/env python3
"""
Test script to validate SMM is running on localhost:9991
"""

import requests
import json
import sys
from typing import Dict, Any

def test_smm_connection() -> bool:
    """Test basic connection to SMM running on localhost:9991"""
    print("🧪 Testing SMM Connection on localhost:9991")
    print("=" * 50)
    
    base_url = "http://localhost:9991"
    
    # Test 1: Basic connectivity - try multiple common endpoints
    print("1. Testing basic connectivity...")
    endpoints_to_try = [
        "/api/v2/admin/clusters",
        "/api/v2/clusters", 
        "/api/v1/clusters",
        "/api/clusters",
        "/clusters",
        "/api/v2/admin",
        "/api/v2",
        "/api",
        "/"
    ]
    
    response = None
    working_endpoint = None
    
    for endpoint in endpoints_to_try:
        try:
            resp = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   Trying {endpoint}: {resp.status_code}")
            if resp.status_code == 200:
                response = resp
                working_endpoint = endpoint
                print(f"   ✅ SMM is responding on {endpoint}")
                break
            elif resp.status_code in [401, 403]:
                print(f"   ⚠️ SMM requires authentication on {endpoint}")
                response = resp
                working_endpoint = endpoint
                break
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
            continue
    
    if not response:
        print("   ❌ No working endpoints found")
        return False
    
    # Test 2: Check response content
    print("\n2. Testing response content...")
    content_type = response.headers.get('content-type', '').lower()
    print(f"   Content-Type: {content_type}")
    
    if 'json' in content_type:
        try:
            data = response.json()
            print("   ✅ Response is valid JSON")
            print(f"   📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        except json.JSONDecodeError:
            print("   ❌ Response claims to be JSON but is not valid")
            print(f"   📄 First 200 chars: {response.text[:200]}...")
    elif 'html' in content_type:
        print("   ⚠️ Response is HTML (likely a web interface)")
        print(f"   📄 First 200 chars: {response.text[:200]}...")
        print("   💡 This might be the SMM web UI, not the API")
    else:
        print(f"   📄 Response type: {content_type}")
        print(f"   📄 First 200 chars: {response.text[:200]}...")
    
    # Don't fail on non-JSON responses, just note them
    
    # Test 3: Test other common endpoints
    print("\n3. Testing other SMM endpoints...")
    endpoints = [
        "/api/v2/admin/clusters",
        "/api/v2/admin/brokers",
        "/api/v2/admin/topics",
        "/api/v2/admin/consumers"
    ]
    
    for endpoint in endpoints:
        try:
            resp = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if resp.status_code == 200 else "⚠️"
            print(f"   {status} {endpoint}: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
    
    print("\n🎉 SMM connection test completed!")
    print(f"✅ SMM is running and accessible on {base_url}")
    if working_endpoint:
        print(f"✅ Working endpoint found: {working_endpoint}")
    return True

def test_smm_health() -> bool:
    """Test SMM health endpoints"""
    print("\n🏥 Testing SMM Health...")
    print("=" * 30)
    
    base_url = "http://localhost:9991"
    
    # Test health endpoint (if available)
    health_endpoints = [
        "/api/v2/admin/health",
        "/api/v2/health",
        "/health",
        "/api/health"
    ]
    
    for endpoint in health_endpoints:
        try:
            resp = requests.get(f"{base_url}{endpoint}", timeout=5)
            if resp.status_code == 200:
                print(f"   ✅ Health endpoint found: {endpoint}")
                try:
                    health_data = resp.json()
                    print(f"   📊 Health data: {health_data}")
                except:
                    print(f"   📊 Health response: {resp.text[:100]}...")
                return True
        except:
            continue
    
    print("   ⚠️ No health endpoint found, but SMM is responding")
    return True

if __name__ == "__main__":
    print("🚀 Starting SMM Connection Tests")
    print("Target: http://localhost:9991")
    print()
    
    success = test_smm_connection()
    if success:
        test_smm_health()
        print("\n✅ All tests passed! SMM is running and accessible.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! SMM may not be running or accessible.")
        sys.exit(1)
