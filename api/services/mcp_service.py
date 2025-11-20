"""
MCP (Model Context Protocol) Service
"""
import aiohttp
from typing import Dict, Any, Optional, List

from api.api.core.config import settings


class MCPService:
    """Service for interacting with MCP servers"""
    
    def __init__(self):
        self.mcp_url = settings.MCP_SERVER_URL
        self.api_key = settings.MCP_API_KEY
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to MCP server"""
        url = f"{self.mcp_url}{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=self.headers,
                json=data
            ) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"MCP server error: {error}")
                return await response.json()
    
    async def list_servers(self) -> List[Dict]:
        """List available MCP servers"""
        try:
            response = await self._make_request("GET", "/servers")
            return response.get("servers", [])
        except Exception as e:
            print(f"Error listing MCP servers: {e}")
            # Return default server configuration
            return [{
                "id": "default",
                "name": "Default MCP Server",
                "url": self.mcp_url,
                "status": "unknown"
            }]
    
    async def list_tools(self, server_id: str) -> List[Dict]:
        """List tools available on MCP server"""
        try:
            endpoint = f"/servers/{server_id}/tools"
            response = await self._make_request("GET", endpoint)
            return response.get("tools", [])
        except Exception as e:
            raise Exception(f"Error listing tools: {e}")
    
    async def invoke_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Invoke a tool on MCP server"""
        try:
            endpoint = f"/servers/{server_id}/tools/{tool_name}/invoke"
            data = {
                "arguments": arguments,
                "context": context or {}
            }
            response = await self._make_request("POST", endpoint, data)
            return response
        except Exception as e:
            raise Exception(f"Error invoking tool: {e}")
    
    async def list_prompts(self, server_id: str) -> List[Dict]:
        """List prompts available on MCP server"""
        try:
            endpoint = f"/servers/{server_id}/prompts"
            response = await self._make_request("GET", endpoint)
            return response.get("prompts", [])
        except Exception as e:
            raise Exception(f"Error listing prompts: {e}")
    
    async def get_prompt(
        self,
        server_id: str,
        prompt_name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Get and render a prompt from MCP server"""
        try:
            endpoint = f"/servers/{server_id}/prompts/{prompt_name}"
            data = {"variables": variables or {}}
            response = await self._make_request("POST", endpoint, data)
            return response
        except Exception as e:
            raise Exception(f"Error getting prompt: {e}")
    
    async def list_resources(self, server_id: str) -> List[Dict]:
        """List resources available on MCP server"""
        try:
            endpoint = f"/servers/{server_id}/resources"
            response = await self._make_request("GET", endpoint)
            return response.get("resources", [])
        except Exception as e:
            raise Exception(f"Error listing resources: {e}")
    
    async def read_resource(
        self,
        server_id: str,
        resource_uri: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Read a resource from MCP server"""
        try:
            endpoint = f"/servers/{server_id}/resources/read"
            data = {
                "uri": resource_uri,
                "parameters": parameters or {}
            }
            response = await self._make_request("POST", endpoint, data)
            return response
        except Exception as e:
            raise Exception(f"Error reading resource: {e}")
    
    async def get_server_status(self, server_id: str) -> Dict:
        """Get MCP server status"""
        try:
            endpoint = f"/servers/{server_id}/status"
            response = await self._make_request("GET", endpoint)
            return response
        except Exception as e:
            return {
                "server_id": server_id,
                "status": "error",
                "error": str(e)
            }
