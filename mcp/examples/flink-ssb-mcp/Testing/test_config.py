#!/usr/bin/env python3
"""
Test configuration for SSB MCP Server testing.
Sets up environment variables and provides test utilities.
"""

import os
import sys
from typing import Dict, Any


def setup_test_environment():
    """Set up test environment variables."""
    # Default configuration for testing
    test_config = {
        'SSB_API_BASE': 'http://localhost:18121',
        'SSB_USER': 'admin',
        'SSB_PASSWORD': 'admin',
        'SSB_READONLY': 'false',  # Allow write operations for testing
        'TIMEOUT_SECONDS': '30'
    }
    
    # Set environment variables if not already set
    for key, value in test_config.items():
        if not os.getenv(key):
            os.environ[key] = value
            print(f"Set {key}={value}")
    
    print("✅ Test environment configured")


def get_test_data() -> Dict[str, Any]:
    """Get test data for various test scenarios."""
    return {
        'test_table_name': 'test_mcp_table',
        'test_topic': 'test-topic',
        'test_sql': 'SELECT 1 as test_column',
        'test_project_name': 'test_project',
        'test_udf_name': 'test_udf',
        'test_environment_name': 'test_env'
    }


def print_test_header(test_name: str):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")


def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")


if __name__ == "__main__":
    setup_test_environment()
    print("Test configuration loaded successfully")