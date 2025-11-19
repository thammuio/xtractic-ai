#!/usr/bin/env python3
"""
Test runner for SMM MCP Server tests
"""

import subprocess
import sys
import os

def run_test(test_file: str) -> bool:
    """Run a single test file"""
    print(f"🧪 Running {test_file}...")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SMM MCP Server Test Suite")
    print("=" * 50)
    
    tests = [
        "test_smm_connection.py",
        "test_mcp_server.py",
        "test_knox_connection.py",
        "test_knox_mcp_server.py",
        "test_phase1_methods.py",
        "test_fixed_endpoints.py"
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if run_test(test):
            passed += 1
        print()
    
    print("📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
