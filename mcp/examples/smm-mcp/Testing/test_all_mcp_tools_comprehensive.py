#!/usr/bin/env python3
"""
Comprehensive test of all MCP tools in the SMM MCP Server
"""

import os
import sys
import subprocess
from pathlib import Path

def test_all_mcp_tools_comprehensive():
    """Test all MCP tools comprehensively"""
    print("🧪 Comprehensive Testing of All MCP Tools")
    print("=" * 50)
    
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

print("🔧 Comprehensive MCP Tools Testing:")
print("=" * 40)

# Test results tracking
results = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": 0,
    "categories": {}
}

def test_method(category, method_name, args, description=""):
    """Test a single method and return results"""
    results["total_tests"] += 1
    if category not in results["categories"]:
        results["categories"][category] = {"total": 0, "passed": 0, "failed": 0, "errors": 0}
    
    results["categories"][category]["total"] += 1
    
    try:
        method = getattr(client, method_name)
        result = method(*args)
        
        # Check if result is valid
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
print("\\n1. Core Information:")
print("-" * 25)
success, message = test_method("Core Information", "get_smm_info", [], "SMM system information")
print(f"    {message}")
success, message = test_method("Core Information", "get_smm_version", [], "SMM version information")
print(f"    {message}")

# Test Cluster and Broker Management
print("\\n2. Cluster and Broker Management:")
print("-" * 40)
success, message = test_method("Cluster and Broker Management", "get_cluster_details", [], "Cluster details and information")
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_brokers", [], "All brokers in the cluster")
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_broker", [1001], "Specific broker details")
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_broker_metrics", [1001, "1h"], "Broker metrics")
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_all_broker_details", [], "All broker details")
print(f"    {message}")
success, message = test_method("Cluster and Broker Management", "get_broker_details", [1001], "Detailed broker information")
print(f"    {message}")

# Test Topic Management (Read)
print("\\n3. Topic Management (Read):")
print("-" * 35)
success, message = test_method("Topic Management (Read)", "get_all_topic_infos", [], "All topic information")
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_description", ["__smm_producer_metrics"], "Topic description")
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_info", ["__smm_producer_metrics"], "Basic topic information")
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_partitions", ["__smm_producer_metrics"], "Topic partition information")
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_partition_infos", ["__smm_producer_metrics"], "Detailed partition information")
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_topic_configs", ["__smm_producer_metrics"], "Topic configuration")
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_all_topic_configs", [], "All topic configurations")
print(f"    {message}")
success, message = test_method("Topic Management (Read)", "get_default_topic_configs", [], "Default topic configurations")
print(f"    {message}")

# Test Topic Management (Write) - These will likely fail due to SMM limitations
print("\\n4. Topic Management (Write):")
print("-" * 35)
success, message = test_method("Topic Management (Write)", "create_topics", [[{"name": "test-topic", "partitions": 1, "replicationFactor": 1}]], "Create new topics")
print(f"    {message}")
success, message = test_method("Topic Management (Write)", "create_partitions", ["test-topic", 2], "Create additional partitions")
print(f"    {message}")
success, message = test_method("Topic Management (Write)", "delete_topics", [["test-topic"]], "Delete specified topics")
print(f"    {message}")
success, message = test_method("Topic Management (Write)", "alter_topic_configs", ["test-topic", {"retention.ms": "604800000"}], "Alter topic configurations")
print(f"    {message}")

# Test Consumer Group Management
print("\\n5. Consumer Group Management:")
print("-" * 35)
success, message = test_method("Consumer Group Management", "get_consumer_groups", [], "All consumer groups")
print(f"    {message}")
success, message = test_method("Consumer Group Management", "get_consumer_group_names", [], "Consumer group names")
print(f"    {message}")
success, message = test_method("Consumer Group Management", "get_consumer_group_info", ["test-group"], "Consumer group information")
print(f"    {message}")
success, message = test_method("Consumer Group Management", "get_all_consumer_info", [], "All consumer information")
print(f"    {message}")
success, message = test_method("Consumer Group Management", "get_consumer_info", ["test-consumer"], "Specific consumer information")
print(f"    {message}")
success, message = test_method("Consumer Group Management", "reset_offset", ["test-group", "test-topic", 0, 0], "Reset consumer group offset")
print(f"    {message}")

# Test Metrics and Monitoring
print("\\n6. Metrics and Monitoring:")
print("-" * 35)
success, message = test_method("Metrics and Monitoring", "get_cluster_with_broker_metrics", ["1h"], "Cluster with broker metrics")
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_cluster_with_topic_metrics", ["1h"], "Cluster with topic metrics")
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_all_consumer_group_metrics", ["1h"], "All consumer group metrics")
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_consumer_group_metrics", ["test-group", "1h"], "Consumer group metrics")
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_all_producer_metrics", ["1h"], "All producer metrics")
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_producer_metrics", ["test-producer", "1h"], "Producer metrics")
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_topic_metrics", ["__smm_producer_metrics", "1h"], "Topic metrics")
print(f"    {message}")
success, message = test_method("Metrics and Monitoring", "get_topic_partition_metrics", ["__smm_producer_metrics", 0, "1h"], "Topic partition metrics")
print(f"    {message}")

# Test Alert Management
print("\\n7. Alert Management:")
print("-" * 25)
success, message = test_method("Alert Management", "get_all_alert_policies", [], "All alert policies")
print(f"    {message}")
success, message = test_method("Alert Management", "get_alert_policy", ["test-policy"], "Specific alert policy")
print(f"    {message}")
success, message = test_method("Alert Management", "add_alert_policy", [{"name": "test-policy", "description": "Test policy"}], "Add alert policy")
print(f"    {message}")
success, message = test_method("Alert Management", "update_alert_policy", ["test-policy", {"name": "test-policy-updated"}], "Update alert policy")
print(f"    {message}")
success, message = test_method("Alert Management", "delete_alert_policy", ["test-policy"], "Delete alert policy")
print(f"    {message}")
success, message = test_method("Alert Management", "get_alert_notifications", [], "Alert notifications")
print(f"    {message}")
success, message = test_method("Alert Management", "get_alert_notifications_by_entity_type", ["topic"], "Alert notifications by entity type")
print(f"    {message}")
success, message = test_method("Alert Management", "get_alert_notifications_by_entity_type_and_name", ["topic", "test-topic"], "Alert notifications by entity type and name")
print(f"    {message}")
success, message = test_method("Alert Management", "mark_alert_notifications", [["test-notification"]], "Mark alert notifications")
print(f"    {message}")
success, message = test_method("Alert Management", "unmark_alert_notifications", [["test-notification"]], "Unmark alert notifications")
print(f"    {message}")

# Test Alert Management (Enhanced) - Phase 1
print("\\n8. Alert Management (Enhanced):")
print("-" * 40)
success, message = test_method("Alert Management (Enhanced)", "disable_alert_policy", ["test-policy"], "Disable alert policy")
print(f"    {message}")
success, message = test_method("Alert Management (Enhanced)", "enable_alert_policy", ["test-policy"], "Enable alert policy")
print(f"    {message}")
success, message = test_method("Alert Management (Enhanced)", "get_alert_policy_automata", ["test-policy"], "Alert policy automata")
print(f"    {message}")
success, message = test_method("Alert Management (Enhanced)", "get_alert_notifications_by_entity", ["topic", "test-topic"], "Alert notifications by entity")
print(f"    {message}")
success, message = test_method("Alert Management (Enhanced)", "mark_alert_notifications_read", [["test-notification"]], "Mark alert notifications as read")
print(f"    {message}")

# Test Notifiers Management - Phase 1
print("\\n9. Notifiers Management:")
print("-" * 30)
success, message = test_method("Notifiers Management", "get_notifiers", [], "All notifiers")
print(f"    {message}")
success, message = test_method("Notifiers Management", "get_notifier", ["test-notifier"], "Specific notifier")
print(f"    {message}")
success, message = test_method("Notifiers Management", "get_notifier_provider_configs", [], "Notifier provider configurations")
print(f"    {message}")

# Test End-to-End Latency Monitoring - Phase 1
print("\\n10. End-to-End Latency Monitoring:")
print("-" * 45)
success, message = test_method("End-to-End Latency Monitoring", "get_topic_etelatency", ["__smm_producer_metrics", "1h"], "Topic end-to-end latency")
print(f"    {message}")
success, message = test_method("End-to-End Latency Monitoring", "get_topic_group_etelatency", ["__smm_producer_metrics", "test-group", "1h"], "Topic and group end-to-end latency")
print(f"    {message}")

# Test Replication Statistics - Phase 1
print("\\n11. Replication Statistics:")
print("-" * 35)
success, message = test_method("Replication Statistics", "get_replication_stats", [], "Replication statistics")
print(f"    {message}")
success, message = test_method("Replication Statistics", "is_replication_configured", [], "Replication configuration status")
print(f"    {message}")
success, message = test_method("Replication Statistics", "get_replication_stats_by_cluster", ["source", "target"], "Replication stats by cluster")
print(f"    {message}")
success, message = test_method("Replication Statistics", "get_topic_replication_stats", ["source", "target", "test-topic"], "Topic replication stats")
print(f"    {message}")
success, message = test_method("Replication Statistics", "get_topic_replication_stats_simple", ["test-topic"], "Simple topic replication stats")
print(f"    {message}")

# Test Schema Registry
print("\\n12. Schema Registry:")
print("-" * 25)
success, message = test_method("Schema Registry", "get_schema_registry_info", [], "Schema registry information")
print(f"    {message}")
success, message = test_method("Schema Registry", "get_schema_meta_for_topic", ["test-topic"], "Schema metadata for topic")
print(f"    {message}")
success, message = test_method("Schema Registry", "get_key_schema_version_infos", ["test-topic"], "Key schema version information")
print(f"    {message}")
success, message = test_method("Schema Registry", "get_value_schema_version_infos", ["test-topic"], "Value schema version information")
print(f"    {message}")
success, message = test_method("Schema Registry", "register_topic_schema_meta", ["test-topic", {"keySchema": "string", "valueSchema": "string"}], "Register topic schema metadata")
print(f"    {message}")

# Test Kafka Connect
print("\\n13. Kafka Connect:")
print("-" * 25)
success, message = test_method("Kafka Connect", "get_connectors", [], "All connectors")
print(f"    {message}")
success, message = test_method("Kafka Connect", "get_connector", ["test-connector"], "Specific connector")
print(f"    {message}")
success, message = test_method("Kafka Connect", "create_connector", [{"name": "test-connector", "config": {"topic": "test"}}], "Create connector")
print(f"    {message}")
success, message = test_method("Kafka Connect", "delete_connector", ["test-connector"], "Delete connector")
print(f"    {message}")
success, message = test_method("Kafka Connect", "get_connector_config_def", ["test-connector"], "Connector configuration definition")
print(f"    {message}")
success, message = test_method("Kafka Connect", "get_connector_permissions", ["test-connector"], "Connector permissions")
print(f"    {message}")
success, message = test_method("Kafka Connect", "get_connect_worker_metrics", ["1h"], "Connect worker metrics")
print(f"    {message}")

# Test Kafka Connect (Enhanced) - Phase 1
print("\\n14. Kafka Connect (Enhanced):")
print("-" * 40)
success, message = test_method("Kafka Connect (Enhanced)", "get_connector_templates", [], "Connector templates")
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "get_connector_config_definitions", ["org.apache.kafka.connect.file.FileStreamSourceConnector"], "Connector config definitions")
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "get_connector_config_sample", ["FileStreamSource", "org.apache.kafka.connect.file.FileStreamSourceConnector", "1.0"], "Connector config sample")
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "validate_connector_config", [{"name": "test-connector", "config": {"topic": "test"}}], "Validate connector config")
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "perform_connector_action", ["test-connector", "restart"], "Perform connector action")
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "is_connect_configured", [], "Connect configuration status")
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "get_connector_sink_metrics", ["test-connector"], "Connector sink metrics")
print(f"    {message}")
success, message = test_method("Kafka Connect (Enhanced)", "get_connect_worker_metrics", ["1h"], "Connect worker metrics")
print(f"    {message}")

# Test Lineage Tracking
print("\\n15. Lineage Tracking:")
print("-" * 25)
success, message = test_method("Lineage Tracking", "get_topic_lineage", ["test-topic"], "Topic lineage")
print(f"    {message}")
success, message = test_method("Lineage Tracking", "get_topic_partition_lineage", ["test-topic", 0], "Topic partition lineage")
print(f"    {message}")
success, message = test_method("Lineage Tracking", "get_consumer_group_lineage", ["test-group"], "Consumer group lineage")
print(f"    {message}")
success, message = test_method("Lineage Tracking", "get_producer_lineage", ["test-producer"], "Producer lineage")
print(f"    {message}")

# Test Authentication
print("\\n16. Authentication:")
print("-" * 25)
success, message = test_method("Authentication", "get_access", [], "Access information")
print(f"    {message}")
success, message = test_method("Authentication", "login", ["admin", "admin"], "Login to SMM")
print(f"    {message}")
success, message = test_method("Authentication", "logout", [], "Logout from SMM")
print(f"    {message}")

# Print comprehensive summary
print("\\n📊 Comprehensive Test Results Summary:")
print("=" * 45)
print(f"Total Tests: {results['total_tests']}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Errors: {results['errors']}")
if results['total_tests'] > 0:
    success_rate = (results['passed'] / results['total_tests'] * 100)
    print(f"Success Rate: {success_rate:.1f}%")

print("\\n📋 Category Breakdown:")
print("-" * 25)
for category, stats in results["categories"].items():
    if stats["total"] > 0:
        success_rate = (stats["passed"] / stats["total"] * 100)
        print(f"{category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")

print("\\n🎉 Comprehensive MCP Tools Testing Complete!")
print("💡 Check the results above for detailed status")
'''
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_script
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=300)  # 5 minute timeout for comprehensive testing
        
        print("Comprehensive MCP Tools Test Output:")
        print("-" * 40)
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
    print("🚀 Comprehensive Testing of All MCP Tools")
    print("Target: Validate all 90+ MCP tools after API endpoint fixes")
    print()
    
    success = test_all_mcp_tools_comprehensive()
    
    if success:
        print("\n✅ Comprehensive MCP tools testing completed!")
        print("💡 Check the results above for detailed status")
        sys.exit(0)
    else:
        print("\n❌ Comprehensive MCP tools testing failed")
        sys.exit(1)
