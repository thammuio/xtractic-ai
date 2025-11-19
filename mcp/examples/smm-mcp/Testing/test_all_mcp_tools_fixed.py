#!/usr/bin/env python3
"""
Comprehensive test script for all MCP tools in the SMM MCP Server
"""

import os
import sys
import subprocess
from pathlib import Path

def test_all_mcp_tools():
    """Test all MCP tools comprehensively"""
    print("🧪 Testing All MCP Tools in SMM MCP Server")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    test_script = '''
import os
os.environ['SMM_API_BASE'] = 'http://localhost:9991/api/v1/admin'
os.environ['SMM_READONLY'] = 'false'

from src.ssm_mcp_server.config import ServerConfig
from src.ssm_mcp_server.client import SMMClient
import requests
import json

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

print("🔧 Testing All MCP Tools:")
print("=" * 30)

# Test results tracking
results = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": 0,
    "categories": {}
}

def test_method(category, method_name, args):
    """Test a single method and return results"""
    results["total_tests"] += 1
    if category not in results["categories"]:
        results["categories"][category] = {"total": 0, "passed": 0, "failed": 0, "errors": 0}
    
    results["categories"][category]["total"] += 1
    
    try:
        method = getattr(client, method_name)
        result = method(*args)
        
        # Check if result is valid (not None, not empty dict with error)
        if result is not None and not (isinstance(result, dict) and "error" in str(result).lower()):
            results["passed"] += 1
            results["categories"][category]["passed"] += 1
            return True, f"✅ {method_name}: Success - {type(result)}"
        else:
            results["failed"] += 1
            results["categories"][category]["failed"] += 1
            return False, f"⚠️ {method_name}: Invalid result - {result}"
            
    except Exception as e:
        results["errors"] += 1
        results["categories"][category]["errors"] += 1
        return False, f"❌ {method_name}: Error - {str(e)[:100]}..."

# Test Core Information
print("\\nCore Information:")
print("-" * 50)
success, message = test_method("Core Information", "get_smm_info", [])
print(f"    {message}")
success, message = test_method("Core Information", "get_smm_version", [])
print(f"    {message}")

# Test Cluster and Broker Management
print("\\nCluster and Broker Management:")
print("-" * 50)
success, message = test_method("Cluster and Broker Management", "get_cluster_details", [])
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_brokers", [])
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_broker", [1001])
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_broker_metrics", [1001, "1h"])
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_all_broker_details", [])
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_broker_details", [1001])
print(f"    {message}")

# Test Topic Management (Read)
print("\\nTopic Management (Read):")
print("-" * 50)
success, message = test_method("Topic Management (Read)", "get_all_topic_infos", [])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_description", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_info", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_partitions", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_partition_infos", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_configs", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_all_topic_configs", [])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_default_topic_configs", [])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_offsets", ["__smm_producer_metrics"])
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_content", ["__smm_producer_metrics", 0, 0, 10])
print(f"    {message}")

# Test Topic Management (Write) - These will likely fail due to SMM limitations
print("\\nTopic Management (Write):")
print("-" * 50)
success, message = test_method("Topic Management (Write)", "create_topics", [[{"name": "test-topic", "partitions": 1, "replicationFactor": 1}]])
print(f"    {message}")
success, message = test_method("Topic Management (Write)", "create_partitions", ["test-topic", 2])
print(f"    {message}")
success, message = test_method("Topic Management (Write)", "delete_topics", [["test-topic"]])
print(f"    {message}")
success, message = test_method("Topic Management (Write)", "alter_topic_configs", ["test-topic", {"retention.ms": "604800000"}])
print(f"    {message}")

# Test Consumer Group Management
print("\\nConsumer Group Management:")
print("-" * 50)
success, message = test_method("Consumer Group Management", "get_consumer_groups", [])
print(f"    {message}")
success, message = test_method("Consumer Group Management", "get_consumer_group_names", [])
print(f"    {message}")
success, message = test_method("Consumer Group Management", "get_consumer_group_info", ["test-group"])
print(f"    {message}")
success, message = test_method("Consumer Group Management", "get_all_consumer_info", [])
print(f"    {message}")
success, message = test_method("Consumer Group Management", "get_consumer_info", ["test-consumer"])
print(f"    {message}")
success, message = test_method("Consumer Group Management", "reset_offset", ["test-group", "test-topic", 0, 0])
print(f"    {message}")

# Test Metrics and Monitoring
print("\\nMetrics and Monitoring:")
print("-" * 50)
success, message = test_method("Metrics and Monitoring", "get_cluster_with_broker_metrics", ["1h"])
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_cluster_with_topic_metrics", ["1h"])
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_all_consumer_group_metrics", ["1h"])
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_consumer_group_metrics", ["test-group", "1h"])
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_all_producer_metrics", ["1h"])
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_producer_metrics", ["test-producer", "1h"])
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_topic_metrics", ["__smm_producer_metrics", "1h"])
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_topic_partition_metrics", ["__smm_producer_metrics", 0, "1h"])
print(f"    {message}")

# Test Alert Management
print("\\nAlert Management:")
print("-" * 50)
success, message = test_method("Alert Management", "get_all_alert_policies", [])
print(f"    {message}")
success, message = test_method("Alert Management", "get_alert_policy", ["test-policy"])
print(f"    {message}")
success, message = test_method("Alert Management", "add_alert_policy", [{"name": "test-policy", "description": "Test policy"}])
print(f"    {message}")
success, message = test_method("Alert Management", "update_alert_policy", ["test-policy", {"name": "test-policy-updated"}])
print(f"    {message}")
success, message = test_method("Alert Management", "delete_alert_policy", ["test-policy"])
print(f"    {message}")
success, message = test_method("Alert Management", "get_alert_notifications", [])
print(f"    {message}")
success, message = test_method("Alert Management", "get_alert_notifications_by_entity_type", ["topic"])
print(f"    {message}")
success, message = test_method("Alert Management", "get_alert_notifications_by_entity_type_and_name", ["topic", "test-topic"])
print(f"    {message}")
success, message = test_method("Alert Management", "mark_alert_notifications", [["test-notification"]])
print(f"    {message}")
success, message = test_method("Alert Management", "unmark_alert_notifications", [["test-notification"]])
print(f"    {message}")

# Test Alert Management (Enhanced) - Phase 1
print("\\nAlert Management (Enhanced):")
print("-" * 50)
success, message = test_method("Alert Management (Enhanced)", "disable_alert_policy", ["test-policy"])
print(f"    {message}")
success, message = test_method("Alert Management (Enhanced)", "enable_alert_policy", ["test-policy"])
print(f"    {message}")
success, message = test_method("Alert Management (Enhanced)", "get_alert_policy_automata", ["test-policy"])
print(f"    {message}")
success, message = test_method("Alert Management (Enhanced)", "get_alert_notifications_by_entity", ["topic", "test-topic"])
print(f"    {message}")
success, message = test_method("Alert Management (Enhanced)", "mark_alert_notifications_read", [["test-notification"]])
print(f"    {message}")

# Test Notifiers Management - Phase 1
print("\\nNotifiers Management:")
print("-" * 50)
success, message = test_method("Notifiers Management", "get_notifiers", [])
print(f"    {message}")
success, message = test_method("Notifiers Management", "get_notifier", ["test-notifier"])
print(f"    {message}")
success, message = test_method("Notifiers Management", "get_notifier_provider_configs", [])
print(f"    {message}")

# Test End-to-End Latency Monitoring - Phase 1
print("\\nEnd-to-End Latency Monitoring:")
print("-" * 50)
success, message = test_method("End-to-End Latency Monitoring", "get_topic_etelatency", ["__smm_producer_metrics", "1h"])
print(f"    {message}")
success, message = test_method("End-to-End Latency Monitoring", "get_topic_group_etelatency", ["__smm_producer_metrics", "test-group", "1h"])
print(f"    {message}")

# Test Replication Statistics - Phase 1
print("\\nReplication Statistics:")
print("-" * 50)
success, message = test_method("Replication Statistics", "get_replication_stats", [])
print(f"    {message}")
success, message = test_method("Replication Statistics", "is_replication_configured", [])
print(f"    {message}")
success, message = test_method("Replication Statistics", "get_replication_stats_by_cluster", ["source", "target"])
print(f"    {message}")
success, message = test_method("Replication Statistics", "get_topic_replication_stats", ["source", "target", "test-topic"])
print(f"    {message}")
success, message = test_method("Replication Statistics", "get_topic_replication_stats_simple", ["test-topic"])
print(f"    {message}")

# Test Schema Registry
print("\\nSchema Registry:")
print("-" * 50)
success, message = test_method("Schema Registry", "get_schema_registry_info", [])
print(f"    {message}")
success, message = test_method("Schema Registry", "get_schema_meta_for_topic", ["test-topic"])
print(f"    {message}")
success, message = test_method("Schema Registry", "get_key_schema_version_infos", ["test-topic"])
print(f"    {message}")
success, message = test_method("Schema Registry", "get_value_schema_version_infos", ["test-topic"])
print(f"    {message}")
success, message = test_method("Schema Registry", "register_topic_schema_meta", ["test-topic", {"keySchema": "string", "valueSchema": "string"}])
print(f"    {message}")

# Test Kafka Connect
print("\\nKafka Connect:")
print("-" * 50)
success, message = test_method("Kafka Connect", "get_connectors", [])
print(f"    {message}")
success, message = test_method("Kafka Connect", "get_connector", ["test-connector"])
print(f"    {message}")
success, message = test_method("Kafka Connect", "create_connector", [{"name": "test-connector", "config": {"topic": "test"}}])
print(f"    {message}")
success, message = test_method("Kafka Connect", "delete_connector", ["test-connector"])
print(f"    {message}")
success, message = test_method("Kafka Connect", "get_connector_config_def", ["test-connector"])
print(f"    {message}")
success, message = test_method("Kafka Connect", "get_connector_permissions", ["test-connector"])
print(f"    {message}")
success, message = test_method("Kafka Connect", "get_connect_worker_metrics", ["1h"])
print(f"    {message}")

# Test Kafka Connect (Enhanced) - Phase 1
print("\\nKafka Connect (Enhanced):")
print("-" * 50)
success, message = test_method("Kafka Connect (Enhanced)", "get_connector_templates", [])
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "get_connector_config_definitions", ["org.apache.kafka.connect.file.FileStreamSourceConnector"])
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "get_connector_config_sample", ["FileStreamSource", "org.apache.kafka.connect.file.FileStreamSourceConnector", "1.0"])
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "validate_connector_config", [{"name": "test-connector", "config": {"topic": "test"}}])
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "perform_connector_action", ["test-connector", "restart"])
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "is_connect_configured", [])
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "get_connector_sink_metrics", ["test-connector"])
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "get_connect_worker_metrics", ["1h"])
print(f"    {message}")

# Test Lineage Tracking
print("\\nLineage Tracking:")
print("-" * 50)
success, message = test_method("Lineage Tracking", "get_topic_lineage", ["test-topic"])
print(f"    {message}")
success, message = test_method("Lineage Tracking", "get_topic_partition_lineage", ["test-topic", 0])
print(f"    {message}")
success, message = test_method("Lineage Tracking", "get_consumer_group_lineage", ["test-group"])
print(f"    {message}")
success, message = test_method("Lineage Tracking", "get_producer_lineage", ["test-producer"])
print(f"    {message}")

# Test Authentication
print("\\nAuthentication:")
print("-" * 50)
success, message = test_method("Authentication", "get_access", [])
print(f"    {message}")
success, message = test_method("Authentication", "login", ["admin", "admin"])
print(f"    {message}")
success, message = test_method("Authentication", "logout", [])
print(f"    {message}")

# Print summary
print("\\n📊 Test Results Summary:")
print("=" * 30)
print(f"Total Tests: {results['total_tests']}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Errors: {results['errors']}")
print(f"Success Rate: {(results['passed'] / results['total_tests'] * 100):.1f}%")

print("\\n📋 Category Breakdown:")
print("-" * 25)
for category, stats in results["categories"].items():
    success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
    print(f"{category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")

print("\\n🎉 All MCP Tools Testing Complete!")
'''
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_script
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=300)  # 5 minute timeout for comprehensive testing
        
        print("MCP Tools Test Output:")
        print("-" * 25)
        print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print("-" * 10)
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error testing MCP tools: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing All MCP Tools in SMM MCP Server")
    print("Target: Comprehensive testing of all 90+ MCP tools")
    print()
    
    success = test_all_mcp_tools()
    
    if success:
        print("\n✅ All MCP tools testing completed!")
        print("💡 Check the results above for detailed status")
        sys.exit(0)
    else:
        print("\n❌ MCP tools testing failed")
        sys.exit(1)
