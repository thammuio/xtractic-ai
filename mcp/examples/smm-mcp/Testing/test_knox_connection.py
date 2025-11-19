#!/usr/bin/env python3
"""
Test script to validate Knox gateway connections for SMM MCP Server
"""

import os
import sys
import requests
import json
from typing import Dict, Any, Optional

def test_knox_gateway_connectivity() -> bool:
    """Test basic connectivity to Knox gateway"""
    print("🧪 Testing Knox Gateway Connectivity")
    print("=" * 40)
    
    # Test different common Knox gateway URLs
    knox_urls = [
        "https://localhost:8444/gateway/smm",
        "https://localhost:8444/gateway/knoxsso",
        "https://localhost:8444/gateway",
        "https://localhost:8444",
        "http://localhost:8444/gateway/smm",
        "http://localhost:8444/gateway",
        "http://localhost:8444"
    ]
    
    working_knox_url = None
    
    for knox_url in knox_urls:
        print(f"   Trying Knox URL: {knox_url}")
        try:
            # Test basic connectivity (ignore SSL for testing)
            response = requests.get(knox_url, timeout=5, verify=False)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 401, 403, 404]:
                working_knox_url = knox_url
                print(f"   ✅ Knox gateway responding on {knox_url}")
                break
            elif response.status_code == 500:
                print(f"   ⚠️ Knox gateway error on {knox_url}")
            else:
                print(f"   ❌ Unexpected status {response.status_code}")
                
        except requests.exceptions.SSLError:
            print(f"   ⚠️ SSL error (expected for self-signed certs)")
            # Try HTTP version
            http_url = knox_url.replace('https://', 'http://')
            if http_url != knox_url:
                try:
                    response = requests.get(http_url, timeout=5)
                    if response.status_code in [200, 401, 403, 404]:
                        working_knox_url = http_url
                        print(f"   ✅ Knox gateway responding on {http_url}")
                        break
                except:
                    pass
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Cannot connect to {knox_url}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if not working_knox_url:
        print("   ❌ No working Knox gateway found")
        return False
    
    print(f"\n✅ Knox gateway found: {working_knox_url}")
    return True

def test_knox_authentication_methods() -> bool:
    """Test different Knox authentication methods"""
    print("\n🔐 Testing Knox Authentication Methods")
    print("=" * 45)
    
    # Get Knox URL from environment or use default
    knox_url = os.getenv('KNOX_GATEWAY_URL', 'https://localhost:8444/gateway/smm')
    print(f"   Using Knox URL: {knox_url}")
    
    # Test 1: JWT Token Authentication
    print("\n1. Testing JWT Token Authentication...")
    knox_token = os.getenv('KNOX_TOKEN')
    if knox_token:
        try:
            headers = {'Cookie': f'hadoop-jwt={knox_token}'}
            response = requests.get(f"{knox_url}/api/v2/admin/clusters", 
                                  headers=headers, timeout=10, verify=False)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ JWT token authentication successful")
                return True
            elif response.status_code in [401, 403]:
                print("   ⚠️ JWT token authentication failed (invalid token)")
            else:
                print(f"   ⚠️ JWT token returned status {response.status_code}")
        except Exception as e:
            print(f"   ❌ JWT token test failed: {e}")
    else:
        print("   ⚠️ KNOX_TOKEN not set, skipping JWT test")
    
    # Test 2: Username/Password Authentication
    print("\n2. Testing Username/Password Authentication...")
    knox_user = os.getenv('KNOX_USER')
    knox_password = os.getenv('KNOX_PASSWORD')
    knox_token_endpoint = os.getenv('KNOX_TOKEN_ENDPOINT')
    
    if knox_user and knox_password and knox_token_endpoint:
        try:
            # Try to get JWT token via token endpoint
            token_response = requests.post(
                knox_token_endpoint,
                data={'username': knox_user, 'password': knox_password},
                timeout=10,
                verify=False
            )
            print(f"   Token endpoint status: {token_response.status_code}")
            
            if token_response.status_code == 200:
                try:
                    token_data = token_response.json()
                    if 'access_token' in token_data:
                        jwt_token = token_data['access_token']
                        print("   ✅ JWT token obtained via username/password")
                        
                        # Test the token
                        headers = {'Authorization': f'Bearer {jwt_token}'}
                        response = requests.get(f"{knox_url}/api/v2/admin/clusters", 
                                              headers=headers, timeout=10, verify=False)
                        print(f"   API test status: {response.status_code}")
                        if response.status_code == 200:
                            print("   ✅ Username/password authentication successful")
                            return True
                except json.JSONDecodeError:
                    print("   ⚠️ Token response is not JSON")
            else:
                print(f"   ⚠️ Token endpoint returned {token_response.status_code}")
        except Exception as e:
            print(f"   ❌ Username/password test failed: {e}")
    else:
        print("   ⚠️ KNOX_USER, KNOX_PASSWORD, or KNOX_TOKEN_ENDPOINT not set")
    
    # Test 3: Cookie Authentication
    print("\n3. Testing Cookie Authentication...")
    knox_cookie = os.getenv('KNOX_COOKIE')
    if knox_cookie:
        try:
            headers = {'Cookie': knox_cookie}
            response = requests.get(f"{knox_url}/api/v2/admin/clusters", 
                                  headers=headers, timeout=10, verify=False)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Cookie authentication successful")
                return True
            elif response.status_code in [401, 403]:
                print("   ⚠️ Cookie authentication failed (invalid cookie)")
            else:
                print(f"   ⚠️ Cookie returned status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Cookie test failed: {e}")
    else:
        print("   ⚠️ KNOX_COOKIE not set, skipping cookie test")
    
    # Test 4: Passcode Token Authentication
    print("\n4. Testing Passcode Token Authentication...")
    knox_passcode = os.getenv('KNOX_PASSCODE_TOKEN')
    if knox_passcode:
        try:
            headers = {'X-Knox-Passcode': knox_passcode}
            response = requests.get(f"{knox_url}/api/v2/admin/clusters", 
                                  headers=headers, timeout=10, verify=False)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Passcode authentication successful")
                return True
            elif response.status_code in [401, 403]:
                print("   ⚠️ Passcode authentication failed (invalid passcode)")
            else:
                print(f"   ⚠️ Passcode returned status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Passcode test failed: {e}")
    else:
        print("   ⚠️ KNOX_PASSCODE_TOKEN not set, skipping passcode test")
    
    print("\n   ⚠️ No authentication method succeeded")
    return False

def test_knox_smm_endpoints() -> bool:
    """Test SMM-specific endpoints through Knox"""
    print("\n📊 Testing SMM Endpoints through Knox")
    print("=" * 40)
    
    knox_url = os.getenv('KNOX_GATEWAY_URL', 'https://localhost:8444/gateway/smm')
    print(f"   Using Knox URL: {knox_url}")
    
    # Test various SMM endpoints
    endpoints = [
        "/api/v2/admin/clusters",
        "/api/v2/admin/brokers", 
        "/api/v2/admin/topics",
        "/api/v2/admin/consumers",
        "/api/v2/admin/health",
        "/api/v2/clusters",
        "/api/v1/clusters",
        "/clusters"
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{knox_url}{endpoint}", 
                                  timeout=5, verify=False)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"   {status} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                working_endpoints.append(endpoint)
                # Try to parse as JSON
                try:
                    data = response.json()
                    print(f"      📊 JSON response with keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                except:
                    print(f"      📄 Non-JSON response (length: {len(response.text)})")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
    
    if working_endpoints:
        print(f"\n   ✅ Found {len(working_endpoints)} working endpoints")
        return True
    else:
        print(f"\n   ⚠️ No working SMM endpoints found")
        return False

def test_knox_environment_setup() -> bool:
    """Test Knox environment variable setup"""
    print("\n🔧 Testing Knox Environment Setup")
    print("=" * 35)
    
    env_vars = [
        'KNOX_GATEWAY_URL',
        'KNOX_TOKEN', 
        'KNOX_COOKIE',
        'KNOX_USER',
        'KNOX_PASSWORD',
        'KNOX_TOKEN_ENDPOINT',
        'KNOX_PASSCODE_TOKEN'
    ]
    
    configured_vars = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'TOKEN' in var or 'COOKIE' in var:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                masked_value = value
            print(f"   ✅ {var}: {masked_value}")
            configured_vars.append(var)
        else:
            print(f"   ⚠️ {var}: Not set")
    
    if configured_vars:
        print(f"\n   ✅ {len(configured_vars)} Knox environment variables configured")
        return True
    else:
        print(f"\n   ⚠️ No Knox environment variables configured")
        return False

if __name__ == "__main__":
    print("🚀 Starting Knox Connection Tests")
    print("Target: Knox Gateway for SMM")
    print()
    
    # Test environment setup first
    env_ok = test_knox_environment_setup()
    
    # Test basic connectivity
    connectivity_ok = test_knox_gateway_connectivity()
    
    # Test authentication methods
    auth_ok = test_knox_authentication_methods()
    
    # Test SMM endpoints
    endpoints_ok = test_knox_smm_endpoints()
    
    print("\n📊 Knox Test Summary:")
    print("=" * 25)
    print(f"   Environment Setup: {'✅' if env_ok else '⚠️'}")
    print(f"   Gateway Connectivity: {'✅' if connectivity_ok else '❌'}")
    print(f"   Authentication: {'✅' if auth_ok else '⚠️'}")
    print(f"   SMM Endpoints: {'✅' if endpoints_ok else '⚠️'}")
    
    if connectivity_ok:
        print("\n🎉 Knox connection tests completed!")
        print("✅ Knox gateway is accessible")
        if auth_ok or endpoints_ok:
            print("✅ Authentication and endpoints working")
        else:
            print("⚠️ Authentication not configured (expected for testing)")
        sys.exit(0)
    else:
        print("\n❌ Knox connection tests failed!")
        print("💡 Check Knox gateway configuration and authentication")
        sys.exit(1)
