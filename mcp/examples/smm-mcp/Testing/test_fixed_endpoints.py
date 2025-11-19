#!/usr/bin/env python3
"""
Test script for fixed API endpoints in SMM MCP Server
"""

import os
import sys
import subprocess
from pathlib import Path

def test_fixed_endpoints():
    """Test the fixed API endpoints"""
    print("🧪 Testing Fixed API Endpoints")
    print("=" * 40)
    
    project_root = Path(__file__).parent.parent
    
    test_script = '''
import os
os.environ['SMM_API_BASE'] = 'http://localhost:9991/api/v1/admin'
os.environ['SMM_READONLY'] = 'false'

from src.ssm_mcp_server.config import ServerConfig
from src.ssm_mcp_server.client import SMMClient
import requests

config = ServerConfig()
session = requests.Session()
if config.smm_user and config.smm_password:
    session.auth = (config.smm_user, config.smm_password)

client = SMMClient(
    base_url=config.build_smm_base(),
    session=session,
    timeout_seconds=30,
    proxy_context_path=config.proxy_context_path
)

print("🔧 Testing Fixed API Endpoints:")
print("=" * 40)

# Test results tracking
results = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": 0
}

def test_method(method_name, args):
    """Test a single method and return results"""
    results["total_tests"] += 1
    
    try:
        method = getattr(client, method_name)
        result = method(*args)
        
        # Check if result is valid
        if result is not None and not (isinstance(result, dict) and "error" in str(result).lower()):
            results["passed"] += 1
            return True, f"✅ {method_name}: Success - {type(result)}"
        else:
            results["failed"] += 1
            return False, f"⚠️ {method_name}: Invalid result - {result}"
            
    except Exception as e:
        results["errors"] += 1
        return False, f"❌ {method_name}: Error - {str(e)[:100]}..."

# Test Core Information
print("\\n1. Core Information:")
print("-" * 25)
success, message = test_method("get_smm_info", [])
print(f"    {message}")
success, message = test_method("get_smm_version", [])
print(f"    {message}")

# Test Cluster and Broker Management
print("\\n2. Cluster and Broker Management:")
print("-" * 40)
success, message = test_method("get_cluster_details", [])
print(f"    {message}")
success, message = test_method("get_brokers", [])
print(f"    {message}")
success, message = test_method("get_broker", [1001])
print(f"    {message}")
success, message = test_method("get_broker_metrics", [1001, "1h"])
print(f"    {message}")
success, message = test_method("get_all_broker_details", [])
print(f"    {message}")
success, message = test_method("get_broker_details", [1001])
print(f"    {message}")

# Test Topic Management (Read)
print("\\n3. Topic Management (Read):")
print("-" * 35)
success, message = test_method("get_all_topic_infos", [])
print(f"    {message}")
success, message = test_method("get_topic_description", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("get_topic_info", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("get_topic_partitions", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("get_topic_partition_infos", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("get_topic_configs", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("get_all_topic_configs", [])
print(f"    {message}")
success, message = test_method("get_default_topic_configs", [])
print(f"    {message}")

# Test Phase 1 Methods (should still work)
print("\\n4. Phase 1 Methods (Enhanced):")
print("-" * 40)
success, message = test_method("get_notifiers", [])
print(f"    {message}")
success, message = test_method("get_notifier_provider_configs", [])
print(f"    {message}")
success, message = test_method("is_replication_configured", [])
print(f"    {message}")
success, message = test_method("get_connector_templates", [])
print(f"    {message}")
success, message = test_method("get_connector_config_definitions", ["org.apache.kafka.connect.file.FileStreamSourceConnector"])
print(f"    {message}")
success, message = test_method("get_connector_config_sample", ["FileStreamSource", "org.apache.kafka.connect.file.FileStreamSourceConnector", "1.0"])
print(f"    {message}")
success, message = test_method("is_connect_configured", [])
print(f"    {message}")
success, message = test_method("get_connect_worker_metrics", ["1h"])
print(f"    {message}")

# Print summary
print("\\n📊 Test Results Summary:")
print("=" * 30)
print(f"Total Tests: {results['total_tests']}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Errors: {results['errors']}")
if results['total_tests'] > 0:
    success_rate = (results['passed'] / results['total_tests'] * 100)
    print(f"Success Rate: {success_rate:.1f}%")

print("\\n🎉 Fixed Endpoints Testing Complete!")
print("💡 Check the results above for improvement")
'''
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_script
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=120)
        
        print("Fixed Endpoints Test Output:")
        print("-" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print("-" * 10)
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error testing fixed endpoints: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Fixed API Endpoints")
    print("Target: Validate improvements after fixing 404 errors")
    print()
    
    success = test_fixed_endpoints()
    
    if success:
        print("\n✅ Fixed endpoints testing completed!")
        print("💡 Check the results above for improvement")
        sys.exit(0)
    else:
        print("\n❌ Fixed endpoints testing failed")
        sys.exit(1)
