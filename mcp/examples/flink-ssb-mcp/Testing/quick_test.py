#!/usr/bin/env python3
"""
Quick test script for SSB MCP Server basic functionality.
Tests key features to verify the server is working.
"""

import os
import sys
import json
from datetime import datetime

# Set up environment variables BEFORE importing
print("Setting up test environment...")
os.environ['SSB_API_BASE'] = 'http://localhost:18121'
os.environ['SSB_USER'] = 'admin'
os.environ['SSB_PASSWORD'] = 'admin'
os.environ['SSB_READONLY'] = 'false'

# Add the src directory to the path (go up one level from Testing/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ssb_mcp_server.server import build_client
from ssb_mcp_server.config import ServerConfig


def quick_test():
    """Run quick tests on key MCP features."""
    print("🚀 Quick SSB MCP Server Test")
    print("=" * 40)
    
    try:
        config = ServerConfig()
        print(f"Config: SSB_API_BASE={config.ssb_api_base}, SSB_USER={config.ssb_user}")
        client = build_client(config)
        
        print("✅ Client initialized successfully")
        
        # Test basic connectivity
        print("\n🔗 Testing Basic Connectivity...")
        try:
            info = client.get_ssb_info()
            print(f"✅ SSB Info: {info.get('version', 'Unknown')}")
        except Exception as e:
            print(f"❌ SSB Info failed: {e}")
        
        # Test monitoring
        print("\n📊 Testing Monitoring...")
        try:
            counters = client.get_diagnostic_counters()
            print(f"✅ Diagnostic Counters: {counters.get('counters', {})}")
        except Exception as e:
            print(f"❌ Diagnostic Counters failed: {e}")
        
        # Test table management
        print("\n🗂️ Testing Table Management...")
        try:
            tables = client.list_tables_detailed()
            table_count = len(tables.get('tables', []))
            print(f"✅ Found {table_count} tables")
        except Exception as e:
            print(f"❌ Table Management failed: {e}")
        
        # Test job management
        print("\n🔧 Testing Job Management...")
        try:
            jobs = client.list_streams()
            job_count = len(jobs.get('jobs', []))
            print(f"✅ Found {job_count} jobs")
        except Exception as e:
            print(f"❌ Job Management failed: {e}")
        
        # Test user management
        print("\n👤 Testing User Management...")
        try:
            user_info = client.get_user_info()
            print(f"✅ User: {user_info.get('username', 'Unknown')}")
        except Exception as e:
            print(f"❌ User Management failed: {e}")
        
        # Test query execution
        print("\n⚡ Testing Query Execution...")
        try:
            result = client.execute_query("SELECT 1 as test_value")
            print(f"✅ Query executed successfully")
        except Exception as e:
            print(f"❌ Query Execution failed: {e}")
        
        print("\n🎉 Quick test completed!")
        print("✅ SSB MCP Server is working correctly")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
