#!/usr/bin/env python3
"""
Test runner for SSB MCP Server.
Provides options for quick testing or comprehensive testing.
"""

import os
import sys
import argparse
from datetime import datetime


def setup_environment():
    """Set up test environment variables."""
    print("🔧 Setting up test environment...")
    os.environ['SSB_API_BASE'] = 'http://localhost:18121'
    os.environ['SSB_USER'] = 'admin'
    os.environ['SSB_PASSWORD'] = 'admin'
    os.environ['SSB_READONLY'] = 'false'
    print("✅ Environment configured")


def run_quick_test():
    """Run quick functionality test."""
    print("\n🚀 Running Quick Test...")
    print("=" * 50)
    
    try:
        from . import quick_test
        success = quick_test.quick_test()
        return success
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False


def run_comprehensive_test():
    """Run comprehensive feature test."""
    print("\n🧪 Running Comprehensive Test...")
    print("=" * 50)
    
    try:
        from . import test_all_mcp_features
        tester = test_all_mcp_features.MCPFeatureTester()
        results = tester.run_all_tests()
        return results['passed'] / results['total_tests'] >= 0.8
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='SSB MCP Server Test Runner')
    parser.add_argument('--quick', action='store_true', help='Run quick test only')
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive test only')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    print("🧪 SSB MCP Server Test Runner")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set up environment
    setup_environment()
    
    # Determine which tests to run
    if args.quick:
        tests_to_run = ['quick']
    elif args.comprehensive:
        tests_to_run = ['comprehensive']
    else:
        tests_to_run = ['quick', 'comprehensive']
    
    # Run tests
    all_passed = True
    
    if 'quick' in tests_to_run:
        print("\n" + "="*60)
        print("🚀 QUICK TEST")
        print("="*60)
        if not run_quick_test():
            all_passed = False
    
    if 'comprehensive' in tests_to_run:
        print("\n" + "="*60)
        print("🧪 COMPREHENSIVE TEST")
        print("="*60)
        if not run_comprehensive_test():
            all_passed = False
    
    # Final summary
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    
    if all_passed:
        print("🎉 All tests passed! SSB MCP Server is working correctly.")
        print("✅ Status: HEALTHY")
        exit_code = 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("❌ Status: NEEDS ATTENTION")
        exit_code = 1
    
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
