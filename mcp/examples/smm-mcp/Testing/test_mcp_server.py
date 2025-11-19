#!/usr/bin/env python3
"""
Test script to validate the MCP server can start up and load configuration
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_mcp_server_startup() -> bool:
    """Test that the MCP server can start up without errors"""
    print("🧪 Testing MCP Server Startup")
    print("=" * 40)
    
    # Set up environment for testing
    test_env = os.environ.copy()
    test_env.update({
        'MCP_TRANSPORT': 'stdio',
        'SMM_API_BASE': 'http://localhost:9991',
        'SMM_READONLY': 'true'
    })
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    server_script = project_root / "src" / "ssm_mcp_server" / "server.py"
    
    print(f"1. Testing server script exists...")
    if not server_script.exists():
        print(f"   ❌ Server script not found: {server_script}")
        return False
    print(f"   ✅ Server script found: {server_script}")
    
    print(f"\n2. Testing server imports...")
    try:
        # Change to project root and test imports
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        # Test imports by running a subprocess
        result = subprocess.run([
            sys.executable, "-c", 
            "from src.ssm_mcp_server.server import main; print('Import successful')"
        ], 
        capture_output=True, 
        text=True, 
        timeout=10)
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("   ✅ Server module imports successfully")
        else:
            print(f"   ❌ Server import failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Server import failed: {e}")
        return False
    
    print(f"\n3. Testing configuration loading...")
    try:
        # Change to project root for imports
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['SMM_API_BASE'] = 'http://localhost:9991'
from src.ssm_mcp_server.config import ServerConfig
config = ServerConfig()
print(f'Config loaded: {config.build_smm_base()}')
print(f'Read-only: {config.readonly}')
"""
        ], 
        capture_output=True, 
        text=True, 
        timeout=10)
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("   ✅ Configuration loaded")
            print(f"   📊 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Configuration loading failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Configuration loading failed: {e}")
        return False
    
    print(f"\n4. Testing client creation...")
    try:
        # Change to project root for imports
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['SMM_API_BASE'] = 'http://localhost:9991'
from src.ssm_mcp_server.config import ServerConfig
from src.ssm_mcp_server.client import SMMClient
import requests

config = ServerConfig()
session = requests.Session()
client = SMMClient(
    base_url=config.build_smm_base(),
    session=session,
    timeout_seconds=30,
    proxy_context_path=config.proxy_context_path
)
print(f'Client created: {client.base_url}')
"""
        ], 
        capture_output=True, 
        text=True, 
        timeout=10)
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("   ✅ Client created successfully")
            print(f"   📊 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Client creation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Client creation failed: {e}")
        return False
    
    print(f"\n🎉 MCP Server startup test completed!")
    print(f"✅ All components load successfully")
    return True

def test_mcp_server_help() -> bool:
    """Test that the MCP server can be imported and has expected structure"""
    print("\n🧪 Testing MCP Server Structure")
    print("=" * 35)
    
    project_root = Path(__file__).parent.parent
    
    try:
        # Test that the server module can be imported and has expected functions
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
os.environ['SMM_API_BASE'] = 'http://localhost:9991'
from src.ssm_mcp_server.server import main, build_client
print('Server functions available: main, build_client')
"""
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Server module structure is correct")
            print(f"   📄 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ⚠️ Server structure test returned {result.returncode}")
            print(f"   📄 Error: {result.stderr[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ Server structure test timed out")
        return False
    except Exception as e:
        print(f"   ❌ Server structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting MCP Server Tests")
    print("Target: SSM MCP Server Components")
    print()
    
    success1 = test_mcp_server_startup()
    success2 = test_mcp_server_help()
    
    if success1 and success2:
        print("\n✅ All MCP server tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some MCP server tests failed!")
        sys.exit(1)
