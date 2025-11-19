#!/usr/bin/env python3
"""
Test script to verify MCP server can start and discover tools.
"""

import os
import sys
import json
import subprocess
import time

def test_mcp_server():
    """Test if MCP server can start and respond to tool discovery."""
    
    # Set up environment
    env = os.environ.copy()
    env.update({
        'SSB_API_BASE': 'http://localhost:18121',
        'SSB_USER': 'admin',
        'SSB_PASSWORD': 'admin',
        'SSB_READONLY': 'false',
        'MCP_TRANSPORT': 'stdio',
        'PYTHONPATH': '/Users/ibrooks/Documents/GitHub/SSB-MCP-Server/src'
    })
    
    print("🧪 Testing MCP Server...")
    print(f"SSB_API_BASE: {env['SSB_API_BASE']}")
    print(f"SSB_USER: {env['SSB_USER']}")
    print(f"PYTHONPATH: {env['PYTHONPATH']}")
    
    try:
        # Start the MCP server
        process = subprocess.Popen(
            [sys.executable, '-m', 'ssb_mcp_server.server'],
            cwd='/Users/ibrooks/Documents/GitHub/SSB-MCP-Server',
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send MCP initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("\n📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Wait for response
        time.sleep(2)
        
        # Send tools list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("📤 Sending tools/list request...")
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        # Wait for response
        time.sleep(3)
        
        # Read responses
        stdout, stderr = process.communicate(timeout=5)
        
        print("\n📥 Server Output:")
        print(stdout)
        
        if stderr:
            print("\n❌ Server Errors:")
            print(stderr)
        
        # Check if we got tool information
        if "tools" in stdout.lower() or "get_ssb_info" in stdout:
            print("\n✅ MCP Server is working! Tools discovered.")
            return True
        else:
            print("\n❌ MCP Server failed to respond with tools.")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⏰ MCP Server timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"\n❌ Error testing MCP server: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
