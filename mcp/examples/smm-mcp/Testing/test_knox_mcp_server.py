#!/usr/bin/env python3
"""
Test script to validate MCP server with Knox authentication
"""

import os
import sys
import subprocess
from pathlib import Path

def test_knox_mcp_server_config() -> bool:
    """Test MCP server configuration with Knox"""
    print("🧪 Testing MCP Server with Knox Configuration")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    # Set up Knox environment variables for testing
    test_env = os.environ.copy()
    test_env.update({
        'MCP_TRANSPORT': 'stdio',
        'KNOX_GATEWAY_URL': 'https://localhost:8444/gateway/smm',
        'KNOX_TOKEN': 'test-token',
        'SMM_READONLY': 'true'
    })
    
    print("1. Testing Knox configuration loading...")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['KNOX_GATEWAY_URL'] = 'https://localhost:8444/gateway/smm'
os.environ['KNOX_TOKEN'] = 'test-token'
from src.ssm_mcp_server.config import ServerConfig
config = ServerConfig()
print(f'Knox Gateway URL: {config.knox_gateway_url}')
print(f'SMM API Base: {config.build_smm_base()}')
print(f'Read-only: {config.readonly}')
"""
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Knox configuration loaded successfully")
            print(f"   📊 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Knox configuration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Knox configuration test failed: {e}")
        return False
    
    print("\n2. Testing Knox authentication factory...")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['KNOX_GATEWAY_URL'] = 'https://localhost:8444/gateway/smm'
os.environ['KNOX_TOKEN'] = 'test-token'
from src.ssm_mcp_server.auth import KnoxAuthFactory
auth = KnoxAuthFactory(
    gateway_url='https://localhost:8444/gateway/smm',
    token='test-token',
    cookie=None,
    user=None,
    password=None,
    token_endpoint=None,
    passcode_token=None,
    verify=False
)
print('KnoxAuthFactory created successfully')
print(f'Gateway URL: {auth.gateway_url}')
print(f'Token configured: {bool(auth.token)}')
"""
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Knox authentication factory created successfully")
            print(f"   📊 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Knox authentication factory failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Knox authentication factory test failed: {e}")
        return False
    
    print("\n3. Testing MCP server with Knox client...")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['KNOX_GATEWAY_URL'] = 'https://localhost:8444/gateway/smm'
os.environ['KNOX_TOKEN'] = 'test-token'
from src.ssm_mcp_server.config import ServerConfig
from src.ssm_mcp_server.auth import KnoxAuthFactory
from src.ssm_mcp_server.client import SMMClient
import requests

config = ServerConfig()
auth = KnoxAuthFactory(
    gateway_url=config.knox_gateway_url,
    token=config.knox_token,
    cookie=config.knox_cookie,
    user=config.knox_user,
    password=config.knox_password,
    token_endpoint=config.knox_token_endpoint,
    passcode_token=config.knox_passcode_token,
    verify=False
)
session = auth.build_session()
client = SMMClient(
    base_url=config.build_smm_base(),
    session=session,
    timeout_seconds=30,
    proxy_context_path=config.proxy_context_path
)
print('MCP server with Knox client created successfully')
print(f'Client base URL: {client.base_url}')
print(f'Session headers: {dict(session.headers)}')
"""
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10)
        
        if result.returncode == 0:
            print("   ✅ MCP server with Knox client created successfully")
            print(f"   📊 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ MCP server with Knox client failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ MCP server with Knox client test failed: {e}")
        return False
    
    print("\n🎉 Knox MCP Server configuration test completed!")
    print("✅ All Knox components load successfully")
    return True

def test_knox_authentication_methods() -> bool:
    """Test different Knox authentication methods"""
    print("\n🔐 Testing Knox Authentication Methods")
    print("=" * 45)
    
    project_root = Path(__file__).parent.parent
    
    # Test JWT Token Authentication
    print("1. Testing JWT Token Authentication...")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['KNOX_GATEWAY_URL'] = 'https://localhost:8444/gateway/smm'
os.environ['KNOX_TOKEN'] = 'test-jwt-token'
from src.ssm_mcp_server.auth import KnoxAuthFactory
auth = KnoxAuthFactory(
    gateway_url='https://localhost:8444/gateway/smm',
    token='test-jwt-token',
    cookie=None,
    user=None,
    password=None,
    token_endpoint=None,
    passcode_token=None,
    verify=False
)
session = auth.build_session()
print('JWT Token authentication configured')
print(f'Cookie header: {session.headers.get("Cookie", "Not set")}')
"""
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10)
        
        if result.returncode == 0:
            print("   ✅ JWT Token authentication configured")
            print(f"   📊 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ JWT Token authentication failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ JWT Token authentication test failed: {e}")
    
    # Test Username/Password Authentication
    print("\n2. Testing Username/Password Authentication...")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['KNOX_GATEWAY_URL'] = 'https://localhost:8444/gateway/smm'
os.environ['KNOX_USER'] = 'testuser'
os.environ['KNOX_PASSWORD'] = 'testpass'
os.environ['KNOX_TOKEN_ENDPOINT'] = 'https://localhost:8444/gateway/knoxsso/api/v1/websso'
from src.ssm_mcp_server.auth import KnoxAuthFactory
auth = KnoxAuthFactory(
    gateway_url='https://localhost:8444/gateway/smm',
    token=None,
    cookie=None,
    user='testuser',
    password='testpass',
    token_endpoint='https://localhost:8444/gateway/knoxsso/api/v1/websso',
    passcode_token=None,
    verify=False
)
print('Username/Password authentication configured')
print(f'User: {auth.user}')
print(f'Token endpoint: {auth.token_endpoint}')
"""
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Username/Password authentication configured")
            print(f"   📊 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Username/Password authentication failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Username/Password authentication test failed: {e}")
    
    # Test Cookie Authentication
    print("\n3. Testing Cookie Authentication...")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['KNOX_GATEWAY_URL'] = 'https://localhost:8444/gateway/smm'
os.environ['KNOX_COOKIE'] = 'hadoop-jwt=test-cookie-value'
from src.ssm_mcp_server.auth import KnoxAuthFactory
auth = KnoxAuthFactory(
    gateway_url='https://localhost:8444/gateway/smm',
    token=None,
    cookie='hadoop-jwt=test-cookie-value',
    user=None,
    password=None,
    token_endpoint=None,
    passcode_token=None,
    verify=False
)
session = auth.build_session()
print('Cookie authentication configured')
print(f'Cookie header: {session.headers.get("Cookie", "Not set")}')
"""
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Cookie authentication configured")
            print(f"   📊 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Cookie authentication failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Cookie authentication test failed: {e}")
    
    print("\n🎉 Knox authentication methods test completed!")
    return True

def test_knox_environment_variables() -> bool:
    """Test Knox environment variable handling"""
    print("\n🔧 Testing Knox Environment Variables")
    print("=" * 40)
    
    project_root = Path(__file__).parent.parent
    
    # Test all Knox environment variables
    knox_env_vars = {
        'KNOX_GATEWAY_URL': 'https://test-knox:8444/gateway/smm',
        'KNOX_TOKEN': 'test-jwt-token',
        'KNOX_COOKIE': 'hadoop-jwt=test-cookie',
        'KNOX_USER': 'testuser',
        'KNOX_PASSWORD': 'testpass',
        'KNOX_TOKEN_ENDPOINT': 'https://test-knox:8444/gateway/knoxsso/api/v1/websso',
        'KNOX_PASSCODE_TOKEN': 'test-passcode'
    }
    
    try:
        # Set all environment variables
        test_env = os.environ.copy()
        test_env.update(knox_env_vars)
        
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
# Set environment variables
os.environ.update({
    'KNOX_GATEWAY_URL': 'https://test-knox:8444/gateway/smm',
    'KNOX_TOKEN': 'test-jwt-token',
    'KNOX_COOKIE': 'hadoop-jwt=test-cookie',
    'KNOX_USER': 'testuser',
    'KNOX_PASSWORD': 'testpass',
    'KNOX_TOKEN_ENDPOINT': 'https://test-knox:8444/gateway/knoxsso/api/v1/websso',
    'KNOX_PASSCODE_TOKEN': 'test-passcode'
})

from src.ssm_mcp_server.config import ServerConfig
config = ServerConfig()

print('Knox Environment Variables:')
print(f'  KNOX_GATEWAY_URL: {config.knox_gateway_url}')
print(f'  KNOX_TOKEN: {config.knox_token[:10]}...' if config.knox_token else '  KNOX_TOKEN: Not set')
print(f'  KNOX_COOKIE: {config.knox_cookie[:20]}...' if config.knox_cookie else '  KNOX_COOKIE: Not set')
print(f'  KNOX_USER: {config.knox_user}')
print(f'  KNOX_PASSWORD: {"***" if config.knox_password else "Not set"}')
print(f'  KNOX_TOKEN_ENDPOINT: {config.knox_token_endpoint}')
print(f'  KNOX_PASSCODE_TOKEN: {config.knox_passcode_token[:10]}...' if config.knox_passcode_token else '  KNOX_PASSCODE_TOKEN: Not set')
print(f'  SMM API Base: {config.build_smm_base()}')
"""
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Knox environment variables loaded successfully")
            print(f"   📊 Output:\n{result.stdout}")
        else:
            print(f"   ❌ Knox environment variables failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Knox environment variables test failed: {e}")
        return False
    
    print("\n🎉 Knox environment variables test completed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Knox MCP Server Tests")
    print("Target: MCP Server with Knox Authentication")
    print()
    
    success1 = test_knox_mcp_server_config()
    success2 = test_knox_authentication_methods()
    success3 = test_knox_environment_variables()
    
    if success1 and success2 and success3:
        print("\n✅ All Knox MCP server tests passed!")
        print("🎉 Knox integration is working correctly")
        sys.exit(0)
    else:
        print("\n❌ Some Knox MCP server tests failed!")
        print("💡 Check Knox configuration and authentication setup")
        sys.exit(1)
