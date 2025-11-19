"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_workflow():
    """Sample workflow data for testing"""
    return {
        "name": "Test Workflow",
        "description": "A test workflow",
        "agent_config": {
            "type": "etl",
            "settings": {}
        },
        "workflow_steps": [
            {"step": 1, "action": "extract", "source": "database"},
            {"step": 2, "action": "transform", "operation": "clean"},
            {"step": 3, "action": "load", "destination": "warehouse"}
        ]
    }


@pytest.fixture
def sample_etl_config():
    """Sample ETL configuration for testing"""
    return {
        "job_name": "Test ETL Job",
        "source_type": "csv",
        "source_config": {
            "file_path": "/tmp/test.csv"
        },
        "destination_type": "supabase",
        "destination_config": {
            "table": "test_table"
        }
    }
