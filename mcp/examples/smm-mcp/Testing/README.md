# SMM MCP Server Testing

This directory contains tests to validate that the SMM MCP Server is working correctly.

## Prerequisites

- SMM should be running on `http://localhost:9991`
- Python 3.10+ installed
- `requests` library available

## Running Tests

### Option 1: Using uv (recommended)
```bash
# From the project root
cd Testing
uv run python test_smm_connection.py

# Or run all tests
uv run python run_tests.py
```

### Option 2: Using pip
```bash
# From the project root
cd Testing
python test_smm_connection.py

# Or run all tests
python run_tests.py
```

### Option 3: Using make
```bash
# From the project root
make test-smm
```

## Test Files

### Core Tests
- `test_smm_connection.py` - Tests basic SMM connectivity and endpoints
- `test_connection.py` - Direct SMM connection testing script
- `test_connection_uv.py` - UV-based connection testing script
- `test_mcp_server.py` - Tests MCP server components and structure
- `run_tests.py` - Test runner that executes all tests

### Comprehensive Testing
- `test_all_mcp_tools_comprehensive.py` - Tests all 86 MCP tools comprehensively
- `test_all_mcp_tools_fixed.py` - Tests MCP tools with fixed API endpoints
- `test_fixed_endpoints.py` - Tests specific API endpoint fixes

### Phase 1 Testing
- `test_phase1_methods.py` - Tests newly implemented Phase 1 methods

### Knox Integration Testing
- `test_knox_connection.py` - Tests Knox gateway connectivity and authentication
- `test_knox_mcp_server.py` - Tests MCP server with Knox configuration

## What the Tests Check

1. **Basic Connectivity** - Can connect to SMM on localhost:9991
2. **JSON Response** - SMM returns valid JSON responses
3. **Endpoint Availability** - Common SMM API endpoints are accessible
4. **Health Status** - SMM health endpoints (if available)
5. **MCP Server Components** - Server structure and module imports
6. **API Endpoint Fixes** - Validates corrected API endpoints
7. **Phase 1 Methods** - Tests newly implemented high-priority methods
8. **Knox Integration** - Knox gateway connectivity and authentication
9. **Comprehensive Testing** - All 86 MCP tools functionality

## Expected Output

```
🧪 Testing SMM Connection on localhost:9991
==================================================
1. Testing basic connectivity...
   Status Code: 200
   ✅ SMM is responding

2. Testing JSON response...
   ✅ Response is valid JSON
   📊 Response keys: ['clusters', 'total']

3. Testing other SMM endpoints...
   ✅ /api/v2/admin/clusters: 200
   ✅ /api/v2/admin/brokers: 200
   ✅ /api/v2/admin/topics: 200
   ✅ /api/v2/admin/consumers: 200

🎉 SMM connection test completed!
```

## Troubleshooting

If tests fail:

1. **Connection Error**: Make sure SMM is running on localhost:9991
2. **Timeout**: Check if SMM is responding slowly or overloaded
3. **JSON Error**: SMM might be returning HTML error pages instead of JSON
4. **Status 401/403**: SMM might require authentication

## Testing Examples

### Example 1: Basic SMM Connection Test
```bash
cd Testing
uv run python test_smm_connection.py
```

**Expected Output:**
```
🧪 Testing SMM Connection on localhost:9991
==================================================
1. Testing basic connectivity...
   Status Code: 200
   ✅ SMM is responding

2. Testing JSON response...
   ✅ Response is valid JSON
   📊 Response keys: ['clusters', 'total']

3. Testing other SMM endpoints...
   ✅ /api/v2/admin/clusters: 200
   ✅ /api/v2/admin/brokers: 200
   ✅ /api/v2/admin/topics: 200

🎉 SMM connection test completed!
```

### Example 2: MCP Server Component Test
```bash
cd Testing
uv run python test_mcp_server.py
```

**Expected Output:**
```
🧪 Testing MCP Server Components
================================
✅ Server module imports successfully
✅ SMMClient class available
✅ ServerConfig class available
✅ All required functions available
✅ MCP server structure is valid

🎉 MCP Server component test completed!
```

### Example 3: Comprehensive MCP Tools Test
```bash
cd Testing
uv run python test_all_mcp_tools_comprehensive.py
```

**Expected Output:**
```
🧪 Comprehensive Testing of All MCP Tools
==========================================
📊 Test Results Summary:
==============================
Total Tests: 86
Passed: 22
Failed: 4
Errors: 60
Success Rate: 25.6%

📋 Category Breakdown:
-------------------------
Core Information: 2/2 (100.0%)
Cluster and Broker Management: 6/6 (100.0%)
Topic Management (Read): 5/8 (62.5%)
...
```

### Example 4: Phase 1 Methods Test
```bash
cd Testing
uv run python test_phase1_methods.py
```

**Expected Output:**
```
🚀 Testing Phase 1 Methods Implementation
==========================================
🔧 Testing Phase 1 Methods:
==============================

1. Alert Management Completion:
-----------------------------------
   ✅ disable_alert_policy: Success - <class 'dict'>
   ✅ enable_alert_policy: Success - <class 'dict'>
   ✅ get_alert_policy_automata: Success - <class 'dict'>

2. Notifiers Management:
-------------------------
   ✅ get_notifiers: Success - <class 'list'>
   ✅ get_notifier_provider_configs: Success - <class 'dict'>

🎉 Phase 1 Methods Testing Complete!
```

### Example 5: Fixed Endpoints Test
```bash
cd Testing
uv run python test_fixed_endpoints.py
```

**Expected Output:**
```
🧪 Testing Fixed API Endpoints
===============================
🔧 Testing Fixed API Endpoints:
==================================================

1. Core Information:
--------------------
   ✅ get_smm_info: Success - <class 'dict'>
   ✅ get_smm_version: Success - <class 'dict'>

2. Cluster and Broker Management:
----------------------------------
   ✅ get_cluster_details: Success - <class 'dict'>
   ✅ get_brokers: Success - <class 'list'>
   ✅ get_broker: Success - <class 'dict'>

📊 Test Results Summary:
==============================
Total Tests: 24
Passed: 21
Failed: 3
Errors: 0
Success Rate: 87.5%
```

### Example 6: Knox Integration Test
```bash
cd Testing
uv run python test_knox_connection.py
```

**Expected Output:**
```
🧪 Testing Knox Gateway Connection
===================================
🔧 Testing Knox Integration:
==============================

1. Testing Knox Gateway Connectivity:
-------------------------------------
   ✅ Knox gateway is accessible
   ✅ Authentication methods available
   ✅ SMM endpoints accessible through Knox

2. Testing MCP Server with Knox:
---------------------------------
   ✅ MCP server starts with Knox configuration
   ✅ Authentication headers set correctly
   ✅ SMM client configured for Knox

🎉 Knox integration test completed!
```

### Example 7: Run All Tests
```bash
cd Testing
uv run python run_tests.py
```

**Expected Output:**
```
🚀 SMM MCP Server Test Suite
==================================================
🧪 Running test_smm_connection.py...
----------------------------------------
✅ SMM connection test completed!

🧪 Running test_mcp_server.py...
----------------------------------------
✅ MCP Server component test completed!

🧪 Running test_knox_connection.py...
----------------------------------------
✅ Knox integration test completed!

📊 Test Results:
   Passed: 6/6
   Failed: 0/6

🎉 All tests passed!
```

## Test Configuration

### Environment Variables
```bash
# For direct SMM connection
export SMM_API_BASE="http://localhost:9991/api/v1/admin"
export SMM_USER="admin"
export SMM_PASSWORD="admin"
export SMM_READONLY="false"

# For Knox/CDP connection
export KNOX_GATEWAY_URL="https://your-knox-gateway:8444/gateway/smm"
export KNOX_TOKEN="your-jwt-token"
export SMM_READONLY="true"
```

### Test Timeouts
- **Default Timeout**: 30 seconds per test
- **Comprehensive Test**: 5 minutes (300 seconds)
- **Individual Tests**: 30-60 seconds

## Debugging Tests

### Enable Verbose Output
```bash
# Run with verbose output
uv run python test_smm_connection.py --verbose

# Run with debug logging
DEBUG=1 uv run python test_mcp_server.py
```

### Test Specific Components
```bash
# Test only SMM connectivity
uv run python test_smm_connection.py

# Test only MCP server structure
uv run python test_mcp_server.py

# Test only Phase 1 methods
uv run python test_phase1_methods.py
```

## Adding New Tests

To add new tests:

1. Create a new Python file in this directory
2. Follow the pattern in `test_smm_connection.py`
3. Add the test file to the `tests` list in `run_tests.py`
4. Make sure the file is executable (`chmod +x filename.py`)

### Test Template
```python
#!/usr/bin/env python3
"""
Test description
"""

import os
import sys
import subprocess
from pathlib import Path

def test_functionality():
    """Test specific functionality"""
    print("🧪 Testing [Functionality Name]")
    print("=" * 40)
    
    # Your test logic here
    try:
        # Test implementation
        print("✅ Test passed!")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_functionality()
    sys.exit(0 if success else 1)
```
