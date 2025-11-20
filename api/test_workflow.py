"""
Test script for Cloudera workflow API
Run this to verify your workflow integration is working
"""
import requests
import time
import sys
from typing import Optional


class WorkflowTester:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health(self) -> bool:
        """Test if API is running"""
        print("1. Testing API health...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            print("   ✓ API is healthy")
            return True
        except Exception as e:
            print(f"   ✗ API health check failed: {e}")
            return False
    
    def test_cloudera_env(self) -> bool:
        """Test Cloudera environment configuration"""
        print("\n2. Testing Cloudera environment...")
        try:
            response = self.session.get(f"{self.base_url}/api/workflows/cloudera/env")
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                env_vars = data.get("data", {})
                print("   Environment variables:")
                for key, value in env_vars.items():
                    status = "✓" if value else "✗"
                    print(f"   {status} {key}: {value or 'Not set'}")
                return True
            return False
        except Exception as e:
            print(f"   ✗ Environment check failed: {e}")
            return False
    
    def test_cloudera_credentials(self) -> bool:
        """Test Cloudera credentials configuration"""
        print("\n3. Testing Cloudera credentials...")
        try:
            response = self.session.get(f"{self.base_url}/api/workflows/cloudera/credentials")
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                creds = data.get("data", {})
                print(f"   Domain: {creds.get('domain')}")
                print(f"   Workspace: {creds.get('workspace_domain')}")
                print(f"   Has API Key: {creds.get('has_api_key')}")
                print(f"   Has Project ID: {creds.get('has_project_id')}")
                
                if creds.get('has_api_key') and creds.get('has_project_id'):
                    print("   ✓ Credentials configured")
                    return True
                else:
                    print("   ✗ Incomplete credentials")
                    return False
            return False
        except Exception as e:
            print(f"   ✗ Credentials check failed: {e}")
            return False
    
    def test_workflow_kickoff(self, pdf_url: str) -> Optional[str]:
        """Test workflow kickoff"""
        print(f"\n4. Testing workflow kickoff with PDF: {pdf_url}")
        try:
            response = self.session.post(
                f"{self.base_url}/api/workflows/deployed/kickoff",
                json={"pdf_url": pdf_url}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                trace_id = data.get("trace_id")
                print(f"   ✓ Workflow started successfully")
                print(f"   Trace ID: {trace_id}")
                return trace_id
            else:
                print("   ✗ Workflow kickoff failed")
                return None
        except Exception as e:
            print(f"   ✗ Workflow kickoff error: {e}")
            return None
    
    def test_workflow_events(self, trace_id: str, max_wait: int = 60) -> bool:
        """Test workflow events and wait for completion"""
        print(f"\n5. Testing workflow events (trace_id: {trace_id})")
        print(f"   Polling for completion (max {max_wait}s)...")
        
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < max_wait:
            attempt += 1
            try:
                response = self.session.get(
                    f"{self.base_url}/api/workflows/deployed/events",
                    params={"trace_id": trace_id}
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("success"):
                    events = data.get("events", {})
                    
                    # Check if workflow completed
                    if events.get("success"):
                        elapsed = time.time() - start_time
                        print(f"   ✓ Workflow completed in {elapsed:.1f}s")
                        print(f"\n   Results:")
                        print(f"   - Table: {events.get('table_name')}")
                        print(f"   - Rows inserted: {events.get('rows_inserted')}")
                        print(f"   - Columns: {', '.join(events.get('columns', []))}")
                        print(f"   - Message: {events.get('message')}")
                        return True
                    else:
                        print(f"   Attempt {attempt}: Still processing...")
                        time.sleep(3)
                else:
                    print(f"   Attempt {attempt}: No events yet...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"   ✗ Error checking events: {e}")
                return False
        
        print(f"   ✗ Workflow did not complete within {max_wait}s")
        return False
    
    def run_all_tests(self, pdf_url: Optional[str] = None):
        """Run all tests"""
        print("=" * 60)
        print("Cloudera Workflow API Test Suite")
        print("=" * 60)
        
        results = []
        
        # Test 1: Health check
        results.append(("Health Check", self.test_health()))
        
        # Test 2: Environment
        results.append(("Environment Config", self.test_cloudera_env()))
        
        # Test 3: Credentials
        results.append(("Credentials Config", self.test_cloudera_credentials()))
        
        # Test 4 & 5: Workflow execution (optional)
        if pdf_url:
            trace_id = self.test_workflow_kickoff(pdf_url)
            if trace_id:
                results.append(("Workflow Kickoff", True))
                results.append(("Workflow Execution", self.test_workflow_events(trace_id)))
            else:
                results.append(("Workflow Kickoff", False))
                results.append(("Workflow Execution", False))
        else:
            print("\n4. Skipping workflow execution tests (no PDF URL provided)")
            print("   To test workflow execution, run:")
            print("   python test_workflow.py <pdf_url>")
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        print("=" * 60)
        
        return passed == total


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Cloudera workflow API")
    parser.add_argument(
        "--url",
        default="http://localhost:9000",
        help="Base URL of the API (default: http://localhost:9000)"
    )
    parser.add_argument(
        "--pdf-url",
        help="PDF URL to test workflow execution (optional)"
    )
    
    args = parser.parse_args()
    
    tester = WorkflowTester(base_url=args.url)
    success = tester.run_all_tests(pdf_url=args.pdf_url)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
