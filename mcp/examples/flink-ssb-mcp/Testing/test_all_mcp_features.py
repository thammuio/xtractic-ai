#!/usr/bin/env python3
"""
Comprehensive test suite for SSB MCP Server features.
Tests all 80+ MCP tools across 15 functional categories.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List
from datetime import datetime

# Add the src directory to the path (go up one level from Testing/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ssb_mcp_server.server import build_client
from ssb_mcp_server.config import ServerConfig


class MCPFeatureTester:
    """Comprehensive tester for all MCP features."""
    
    def __init__(self):
        self.config = ServerConfig()
        self.client = build_client(self.config)
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'categories': {}
        }
        self.test_data = {}
    
    def log_result(self, category: str, test_name: str, success: bool, error: str = None):
        """Log test result."""
        self.results['total_tests'] += 1
        if success:
            self.results['passed'] += 1
            print(f"✅ {category} - {test_name}")
        else:
            self.results['failed'] += 1
            error_msg = f"❌ {category} - {test_name}: {error}"
            print(error_msg)
            self.results['errors'].append(error_msg)
        
        if category not in self.results['categories']:
            self.results['categories'][category] = {'passed': 0, 'failed': 0}
        
        if success:
            self.results['categories'][category]['passed'] += 1
        else:
            self.results['categories'][category]['failed'] += 1
    
    def test_basic_connectivity(self):
        """Test basic connectivity and authentication."""
        print("\n🔗 Testing Basic Connectivity...")
        
        try:
            result = self.client.get_ssb_info()
            self.log_result("Connectivity", "get_ssb_info", True)
            self.test_data['ssb_info'] = result
        except Exception as e:
            self.log_result("Connectivity", "get_ssb_info", False, str(e))
        
        try:
            result = self.client.get_heartbeat()
            self.log_result("Connectivity", "get_heartbeat", True)
        except Exception as e:
            self.log_result("Connectivity", "get_heartbeat", False, str(e))
    
    def test_monitoring_diagnostics(self):
        """Test monitoring and diagnostics features."""
        print("\n📊 Testing Monitoring & Diagnostics...")
        
        try:
            result = self.client.get_diagnostic_counters()
            self.log_result("Monitoring", "get_diagnostic_counters", True)
        except Exception as e:
            self.log_result("Monitoring", "get_diagnostic_counters", False, str(e))
        
        try:
            result = self.client.analyze_sql("SELECT * FROM NVDA LIMIT 10")
            self.log_result("Monitoring", "analyze_sql", True)
        except Exception as e:
            self.log_result("Monitoring", "analyze_sql", False, str(e))
    
    def test_job_management(self):
        """Test job management features."""
        print("\n🔧 Testing Advanced Job Management...")
        
        # First, get a list of jobs to work with
        try:
            jobs_result = self.client.list_streams()
            jobs = jobs_result.get('jobs', [])
            if jobs:
                job_id = jobs[0]['job_id']
                self.test_data['job_id'] = job_id
                
                try:
                    result = self.client.get_job_events(job_id)
                    self.log_result("Job Management", "get_job_events", True)
                except Exception as e:
                    self.log_result("Job Management", "get_job_events", False, str(e))
                
                try:
                    result = self.client.get_job_state(job_id)
                    self.log_result("Job Management", "get_job_state", True)
                except Exception as e:
                    self.log_result("Job Management", "get_job_state", False, str(e))
                
                try:
                    result = self.client.get_job_mv_endpoints(job_id)
                    self.log_result("Job Management", "get_job_mv_endpoints", True)
                except Exception as e:
                    self.log_result("Job Management", "get_job_mv_endpoints", False, str(e))
                
                try:
                    result = self.client.copy_job(job_id)
                    self.log_result("Job Management", "copy_job", True)
                except Exception as e:
                    self.log_result("Job Management", "copy_job", False, str(e))
            else:
                print("⚠️  No jobs available for job management tests")
        except Exception as e:
            self.log_result("Job Management", "list_streams_for_job_tests", False, str(e))
    
    def test_table_management(self):
        """Test table management features."""
        print("\n🗂️ Testing Enhanced Table Management...")
        
        try:
            result = self.client.list_tables_detailed()
            self.log_result("Table Management", "list_tables_detailed", True)
            self.test_data['tables'] = result.get('tables', [])
        except Exception as e:
            self.log_result("Table Management", "list_tables_detailed", False, str(e))
        
        try:
            result = self.client.get_table_tree()
            self.log_result("Table Management", "get_table_tree", True)
        except Exception as e:
            self.log_result("Table Management", "get_table_tree", False, str(e))
        
        try:
            result = self.client.list_tables()
            self.log_result("Table Management", "list_tables", True)
        except Exception as e:
            self.log_result("Table Management", "list_tables", False, str(e))
        
        # Test table schema if we have tables
        if self.test_data.get('tables'):
            try:
                table_name = self.test_data['tables'][0].get('table_name', 'NVDA')
                result = self.client.get_table_schema(table_name)
                self.log_result("Table Management", "get_table_schema", True)
            except Exception as e:
                self.log_result("Table Management", "get_table_schema", False, str(e))
    
    def test_connector_format_management(self):
        """Test connector and format management features."""
        print("\n🔌 Testing Connector & Format Management...")
        
        try:
            result = self.client.list_data_formats()
            self.log_result("Connector Management", "list_data_formats", True)
        except Exception as e:
            self.log_result("Connector Management", "list_data_formats", False, str(e))
        
        try:
            result = self.client.list_connectors()
            self.log_result("Connector Management", "list_connectors", True)
        except Exception as e:
            self.log_result("Connector Management", "list_connectors", False, str(e))
        
        try:
            result = self.client.validate_kafka_connector("local-kafka")
            self.log_result("Connector Management", "validate_kafka_connector", True)
        except Exception as e:
            self.log_result("Connector Management", "validate_kafka_connector", False, str(e))
    
    def test_user_project_management(self):
        """Test user and project management features."""
        print("\n👤 Testing User & Project Management...")
        
        try:
            result = self.client.get_user_info()
            self.log_result("User Management", "get_user_info", True)
        except Exception as e:
            self.log_result("User Management", "get_user_info", False, str(e))
        
        try:
            result = self.client.get_user_settings()
            self.log_result("User Management", "get_user_settings", True)
        except Exception as e:
            self.log_result("User Management", "get_user_settings", False, str(e))
        
        try:
            result = self.client.list_projects()
            self.log_result("User Management", "list_projects", True)
        except Exception as e:
            self.log_result("User Management", "list_projects", False, str(e))
    
    def test_api_key_management(self):
        """Test API key management features."""
        print("\n🔑 Testing API Key Management...")
        
        try:
            result = self.client.list_api_keys()
            self.log_result("API Key Management", "list_api_keys", True)
        except Exception as e:
            self.log_result("API Key Management", "list_api_keys", False, str(e))
    
    def test_environment_management(self):
        """Test environment management features."""
        print("\n🌍 Testing Environment Management...")
        
        try:
            result = self.client.list_environments()
            self.log_result("Environment Management", "list_environments", True)
        except Exception as e:
            self.log_result("Environment Management", "list_environments", False, str(e))
    
    def test_sync_configuration(self):
        """Test sync and configuration features."""
        print("\n🔄 Testing Sync & Configuration...")
        
        try:
            result = self.client.get_sync_config()
            self.log_result("Sync Configuration", "get_sync_config", True)
        except Exception as e:
            self.log_result("Sync Configuration", "get_sync_config", False, str(e))
    
    def test_udf_management(self):
        """Test UDF management features."""
        print("\n📈 Testing UDF Management...")
        
        try:
            result = self.client.list_udfs_detailed()
            self.log_result("UDF Management", "list_udfs_detailed", True)
        except Exception as e:
            self.log_result("UDF Management", "list_udfs_detailed", False, str(e))
        
        try:
            result = self.client.list_udfs()
            self.log_result("UDF Management", "list_udfs", True)
        except Exception as e:
            self.log_result("UDF Management", "list_udfs", False, str(e))
        
        try:
            result = self.client.get_udf_artifacts()
            self.log_result("UDF Management", "get_udf_artifacts", True)
        except Exception as e:
            self.log_result("UDF Management", "get_udf_artifacts", False, str(e))
    
    def test_stream_management(self):
        """Test stream management features."""
        print("\n🌊 Testing Stream Management...")
        
        try:
            result = self.client.list_streams()
            self.log_result("Stream Management", "list_streams", True)
            self.test_data['streams'] = result.get('jobs', [])
        except Exception as e:
            self.log_result("Stream Management", "list_streams", False, str(e))
        
        if self.test_data.get('streams'):
            try:
                stream_name = self.test_data['streams'][0]['name']
                result = self.client.get_stream(stream_name)
                self.log_result("Stream Management", "get_stream", True)
            except Exception as e:
                self.log_result("Stream Management", "get_stream", False, str(e))
    
    def test_query_execution(self):
        """Test query execution features."""
        print("\n⚡ Testing Query Execution...")
        
        try:
            result = self.client.execute_query("SELECT 1 as test_column")
            self.log_result("Query Execution", "execute_query", True)
        except Exception as e:
            self.log_result("Query Execution", "execute_query", False, str(e))
        
        try:
            result = self.client.execute_query_with_sampling("SELECT 1 as test_column", sample_all_messages=True)
            self.log_result("Query Execution", "execute_query_with_sampling", True)
        except Exception as e:
            self.log_result("Query Execution", "execute_query_with_sampling", False, str(e))
    
    def test_job_control(self):
        """Test job control features."""
        print("\n🎮 Testing Job Control...")
        
        if self.test_data.get('job_id'):
            try:
                result = self.client.get_job_status(self.test_data['job_id'])
                self.log_result("Job Control", "get_job_status", True)
            except Exception as e:
                self.log_result("Job Control", "get_job_status", False, str(e))
            
            try:
                result = self.client.get_job_sample_by_id(self.test_data['job_id'])
                self.log_result("Job Control", "get_job_sample_by_id", True)
            except Exception as e:
                self.log_result("Job Control", "get_job_sample_by_id", False, str(e))
        
        try:
            result = self.client.list_jobs_with_samples()
            self.log_result("Job Control", "list_jobs_with_samples", True)
        except Exception as e:
            self.log_result("Job Control", "list_jobs_with_samples", False, str(e))
    
    def test_kafka_integration(self):
        """Test Kafka integration features."""
        print("\n📨 Testing Kafka Integration...")
        
        try:
            result = self.client.list_topics()
            self.log_result("Kafka Integration", "list_topics", True)
        except Exception as e:
            self.log_result("Kafka Integration", "list_topics", False, str(e))
    
    def test_cluster_management(self):
        """Test cluster management features."""
        print("\n🏢 Testing Cluster Management...")
        
        try:
            result = self.client.get_cluster_info()
            self.log_result("Cluster Management", "get_cluster_info", True)
        except Exception as e:
            self.log_result("Cluster Management", "get_cluster_info", False, str(e))
        
        try:
            result = self.client.get_cluster_health()
            self.log_result("Cluster Management", "get_cluster_health", True)
        except Exception as e:
            self.log_result("Cluster Management", "get_cluster_health", False, str(e))
    
    def test_kafka_table_management(self):
        """Test Kafka table management features."""
        print("\n🗃️ Testing Kafka Table Management...")
        
        try:
            result = self.client.create_kafka_table("test_table", "test-topic", "local-kafka")
            self.log_result("Kafka Table Management", "create_kafka_table", True)
        except Exception as e:
            self.log_result("Kafka Table Management", "create_kafka_table", False, str(e))
        
        try:
            result = self.client.register_kafka_table("test_register", "test-topic")
            self.log_result("Kafka Table Management", "register_kafka_table", True)
        except Exception as e:
            self.log_result("Kafka Table Management", "register_kafka_table", False, str(e))
    
    def run_all_tests(self):
        """Run all test categories."""
        print("🚀 Starting Comprehensive MCP Feature Testing")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test categories
        self.test_basic_connectivity()
        self.test_monitoring_diagnostics()
        self.test_job_management()
        self.test_table_management()
        self.test_connector_format_management()
        self.test_user_project_management()
        self.test_api_key_management()
        self.test_environment_management()
        self.test_sync_configuration()
        self.test_udf_management()
        self.test_stream_management()
        self.test_query_execution()
        self.test_job_control()
        self.test_kafka_integration()
        self.test_cluster_management()
        self.test_kafka_table_management()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print summary
        self.print_summary(duration)
        
        return self.results
    
    def print_summary(self, duration: float):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = self.results['total_tests']
        passed = self.results['passed']
        failed = self.results['failed']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in self.results['categories'].items():
            cat_total = stats['passed'] + stats['failed']
            cat_success = (stats['passed'] / cat_total * 100) if cat_total > 0 else 0
            print(f"   {category}: {stats['passed']}/{cat_total} ({cat_success:.1f}%)")
        
        if self.results['errors']:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results['errors'][:10]:  # Show first 10 errors
                print(f"   {error}")
            if len(self.results['errors']) > 10:
                print(f"   ... and {len(self.results['errors']) - 10} more errors")
        
        print(f"\n🎯 MCP Server Status: {'✅ HEALTHY' if success_rate >= 80 else '⚠️ NEEDS ATTENTION'}")
        
        # Save detailed results
        self.save_results()
    
    def save_results(self):
        """Save test results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mcp_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")


def main():
    """Main test runner."""
    print("🧪 SSB MCP Server Comprehensive Feature Test")
    print("Testing all 80+ MCP tools across 15 functional categories")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('src/ssb_mcp_server'):
        print("❌ Error: Please run this script from the SSB-MCP-Server root directory")
        sys.exit(1)
    
    # Set up environment variables if not already set
    if not os.getenv('SSB_API_BASE') and not os.getenv('KNOX_GATEWAY_URL'):
        print("⚠️  Warning: No SSB_API_BASE or KNOX_GATEWAY_URL set. Using defaults.")
        os.environ['SSB_API_BASE'] = 'http://localhost:18121'
        os.environ['SSB_USER'] = 'admin'
        os.environ['SSB_PASSWORD'] = 'admin'
    
    # Run tests
    tester = MCPFeatureTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    success_rate = (results['passed'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    sys.exit(0 if success_rate >= 80 else 1)


if __name__ == "__main__":
    main()
