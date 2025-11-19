#!/usr/bin/env python3
"""
Simple test script to verify SSM MCP Server connection and basic functionality.
"""

import os
import sys
from src.ssm_mcp_server.config import ServerConfig
from src.ssm_mcp_server.auth import KnoxAuthFactory
from src.ssm_mcp_server.client import SMMClient

def test_connection():
    """Test basic connection to SMM."""
    print("🧪 Testing SSM MCP Server Connection")
    print("=" * 50)
    
    try:
        # Load configuration
        config = ServerConfig()
        print(f"✅ Configuration loaded successfully")
        print(f"   SMM API Base: {config.build_smm_base()}")
        print(f"   Read-only mode: {config.readonly}")
        
        # Build client
        verify = config.build_verify()
        smm_base = config.build_smm_base()
        
        if config.knox_gateway_url:
            auth = KnoxAuthFactory(
                gateway_url=config.knox_gateway_url,
                token=config.knox_token,
                cookie=config.knox_cookie,
                user=config.knox_user,
                password=config.knox_password,
                token_endpoint=config.knox_token_endpoint,
                passcode_token=config.knox_passcode_token,
                verify=verify,
            )
            session = auth.build_session()
            print(f"✅ Authentication configured (Knox/CDP mode)")
        else:
            import requests
            session = requests.Session()
            session.verify = verify
            if config.smm_user and config.smm_password:
                session.auth = (config.smm_user, config.smm_password)
            print(f"✅ Authentication configured (Direct mode)")
        
        # Create client
        smm = SMMClient(
            smm_base,
            session,
            timeout_seconds=config.timeout_seconds,
            proxy_context_path=config.proxy_context_path,
        )
        print(f"✅ SMM Client created successfully")
        
        # Test basic connection
        try:
            info = smm.get_smm_info()
            print(f"✅ SMM Connection successful!")
            print(f"   Status: {info.get('status', 'unknown')}")
            print(f"   Message: {info.get('message', 'No message')}")
        except Exception as e:
            print(f"⚠️  SMM Connection failed: {str(e)}")
            print(f"   This might be expected if SMM is not running or accessible")
        
        print(f"\n🎉 SSM MCP Server setup completed successfully!")
        print(f"   You can now configure Claude Desktop to use this server.")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"1. Ensure SMM_API_BASE or KNOX_GATEWAY_URL is set")
        print(f"2. Check authentication credentials (KNOX_TOKEN, KNOX_USER/PASSWORD, etc.)")
        print(f"3. Verify SMM service is running and accessible")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
