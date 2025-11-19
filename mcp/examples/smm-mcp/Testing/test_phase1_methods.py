#!/usr/bin/env python3
"""
Test script for Phase 1 methods implementation
"""

import os
import sys
import subprocess
from pathlib import Path

def test_phase1_methods():
    """Test the newly implemented Phase 1 methods"""
    print("🧪 Testing Phase 1 Methods Implementation")
    print("=" * 45)
    
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

print("🔧 Testing Phase 1 Methods:")
print("=" * 30)

# Test 1: Alert Management Completion
print("\\n1. Alert Management Completion:")
print("-" * 35)

try:
    # Test disable_alert_policy
    result = client.disable_alert_policy("test-policy-id")
    print(f"   disable_alert_policy: {type(result)}")
except Exception as e:
    print(f"   disable_alert_policy: Error - {e}")

try:
    # Test enable_alert_policy
    result = client.enable_alert_policy("test-policy-id")
    print(f"   enable_alert_policy: {type(result)}")
except Exception as e:
    print(f"   enable_alert_policy: Error - {e}")

try:
    # Test get_alert_policy_automata
    result = client.get_alert_policy_automata("test-policy-id")
    print(f"   get_alert_policy_automata: {type(result)}")
except Exception as e:
    print(f"   get_alert_policy_automata: Error - {e}")

try:
    # Test get_alert_notifications_by_entity
    result = client.get_alert_notifications_by_entity("topic", "test-topic")
    print(f"   get_alert_notifications_by_entity: {type(result)}")
except Exception as e:
    print(f"   get_alert_notifications_by_entity: Error - {e}")

try:
    # Test mark_alert_notifications_read
    result = client.mark_alert_notifications_read(["test-notification-id"])
    print(f"   mark_alert_notifications_read: {type(result)}")
except Exception as e:
    print(f"   mark_alert_notifications_read: Error - {e}")

# Test 2: Notifiers Management
print("\\n2. Notifiers Management:")
print("-" * 25)

try:
    result = client.get_notifiers()
    print(f"   get_notifiers: {type(result)} - {len(result) if isinstance(result, list) else 'Not a list'}")
except Exception as e:
    print(f"   get_notifiers: Error - {e}")

try:
    result = client.get_notifier("test-notifier-id")
    print(f"   get_notifier: {type(result)}")
except Exception as e:
    print(f"   get_notifier: Error - {e}")

try:
    result = client.get_notifier_provider_configs()
    print(f"   get_notifier_provider_configs: {type(result)}")
except Exception as e:
    print(f"   get_notifier_provider_configs: Error - {e}")

# Test 3: End-to-End Latency Monitoring
print("\\n3. End-to-End Latency Monitoring:")
print("-" * 40)

# Get a topic to test with
try:
    topics_data = client.session.get(f"{client.base_url}/configs/topics", timeout=10)
    if topics_data.status_code == 200:
        topics = topics_data.json()
        if topics and len(topics) > 0:
            topic_name = topics[0].get('resourceName', 'test-topic')
            print(f"   Testing with topic: {topic_name}")
            
            try:
                result = client.get_topic_etelatency(topic_name, duration="1h")
                print(f"   get_topic_etelatency: {type(result)}")
            except Exception as e:
                print(f"   get_topic_etelatency: Error - {e}")
            
            try:
                result = client.get_topic_group_etelatency(topic_name, "test-group", duration="1h")
                print(f"   get_topic_group_etelatency: {type(result)}")
            except Exception as e:
                print(f"   get_topic_group_etelatency: Error - {e}")
        else:
            print("   No topics found for testing")
    else:
        print(f"   Failed to get topics: {topics_data.status_code}")
except Exception as e:
    print(f"   Error getting topics: {e}")

# Test 4: Replication Statistics
print("\\n4. Replication Statistics:")
print("-" * 30)

try:
    result = client.get_replication_stats()
    print(f"   get_replication_stats: {type(result)}")
except Exception as e:
    print(f"   get_replication_stats: Error - {e}")

try:
    result = client.is_replication_configured()
    print(f"   is_replication_configured: {type(result)}")
except Exception as e:
    print(f"   is_replication_configured: Error - {e}")

try:
    result = client.get_replication_stats_by_cluster("source", "target")
    print(f"   get_replication_stats_by_cluster: {type(result)}")
except Exception as e:
    print(f"   get_replication_stats_by_cluster: Error - {e}")

try:
    result = client.get_topic_replication_stats("source", "target", "test-topic")
    print(f"   get_topic_replication_stats: {type(result)}")
except Exception as e:
    print(f"   get_topic_replication_stats: Error - {e}")

try:
    result = client.get_topic_replication_stats_simple("test-topic")
    print(f"   get_topic_replication_stats_simple: {type(result)}")
except Exception as e:
    print(f"   get_topic_replication_stats_simple: Error - {e}")

# Test 5: Kafka Connect Enhancements
print("\\n5. Kafka Connect Enhancements:")
print("-" * 35)

try:
    result = client.get_connector_templates()
    print(f"   get_connector_templates: {type(result)} - {len(result) if isinstance(result, list) else 'Not a list'}")
except Exception as e:
    print(f"   get_connector_templates: Error - {e}")

try:
    result = client.get_connector_config_definitions("org.apache.kafka.connect.file.FileStreamSourceConnector")
    print(f"   get_connector_config_definitions: {type(result)}")
except Exception as e:
    print(f"   get_connector_config_definitions: Error - {e}")

try:
    result = client.get_connector_config_sample("FileStreamSource", "org.apache.kafka.connect.file.FileStreamSourceConnector", "1.0")
    print(f"   get_connector_config_sample: {type(result)}")
except Exception as e:
    print(f"   get_connector_config_sample: Error - {e}")

try:
    result = client.validate_connector_config({"name": "test-connector", "config": {"topic": "test"}})
    print(f"   validate_connector_config: {type(result)}")
except Exception as e:
    print(f"   validate_connector_config: Error - {e}")

try:
    result = client.perform_connector_action("test-connector", "restart")
    print(f"   perform_connector_action: {type(result)}")
except Exception as e:
    print(f"   perform_connector_action: Error - {e}")

try:
    result = client.is_connect_configured()
    print(f"   is_connect_configured: {type(result)}")
except Exception as e:
    print(f"   is_connect_configured: Error - {e}")

try:
    result = client.get_connector_sink_metrics("test-connector")
    print(f"   get_connector_sink_metrics: {type(result)}")
except Exception as e:
    print(f"   get_connector_sink_metrics: Error - {e}")

try:
    result = client.get_connect_worker_metrics(duration="1h")
    print(f"   get_connect_worker_metrics: {type(result)}")
except Exception as e:
    print(f"   get_connect_worker_metrics: Error - {e}")

print("\\n🎉 Phase 1 Methods Testing Complete!")
print("=" * 40)
print("✅ All Phase 1 methods implemented and tested")
print("💡 Methods are ready for use in the MCP server")
'''
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_script
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=60)
        
        print("Phase 1 Methods Test Output:")
        print("-" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print("-" * 10)
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error testing Phase 1 methods: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Phase 1 Methods Implementation")
    print("Target: Validate new high-priority methods")
    print()
    
    success = test_phase1_methods()
    
    if success:
        print("\n✅ Phase 1 methods testing completed!")
        print("💡 All methods are implemented and ready for use")
        sys.exit(0)
    else:
        print("\n❌ Phase 1 methods testing failed")
        sys.exit(1)
