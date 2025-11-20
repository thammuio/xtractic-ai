"""
MCP (Model Context Protocol) Server endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from api.services.mcp_service import MCPService

router = APIRouter()


class MCPToolInvocation(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class MCPPromptRequest(BaseModel):
    prompt_name: str
    variables: Optional[Dict[str, Any]] = None


class MCPResourceRequest(BaseModel):
    resource_uri: str
    parameters: Optional[Dict[str, Any]] = None


@router.get("/servers")
async def list_servers():
    """List available MCP servers"""
    try:
        mcp_service = MCPService()
        servers = await mcp_service.list_servers()
        return {
            "success": True,
            "data": servers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}/tools")
async def list_tools(server_id: str):
    """List tools available on MCP server"""
    try:
        mcp_service = MCPService()
        tools = await mcp_service.list_tools(server_id)
        return {
            "success": True,
            "data": tools
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/tools/invoke")
async def invoke_tool(server_id: str, request: MCPToolInvocation):
    """Invoke a tool on MCP server"""
    try:
        mcp_service = MCPService()
        result = await mcp_service.invoke_tool(
            server_id=server_id,
            tool_name=request.tool_name,
            arguments=request.arguments,
            context=request.context
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}/prompts")
async def list_prompts(server_id: str):
    """List prompts available on MCP server"""
    try:
        mcp_service = MCPService()
        prompts = await mcp_service.list_prompts(server_id)
        return {
            "success": True,
            "data": prompts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/prompts/get")
async def get_prompt(server_id: str, request: MCPPromptRequest):
    """Get and render a prompt from MCP server"""
    try:
        mcp_service = MCPService()
        prompt = await mcp_service.get_prompt(
            server_id=server_id,
            prompt_name=request.prompt_name,
            variables=request.variables
        )
        return {
            "success": True,
            "data": prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}/resources")
async def list_resources(server_id: str):
    """List resources available on MCP server"""
    try:
        mcp_service = MCPService()
        resources = await mcp_service.list_resources(server_id)
        return {
            "success": True,
            "data": resources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/resources/read")
async def read_resource(server_id: str, request: MCPResourceRequest):
    """Read a resource from MCP server"""
    try:
        mcp_service = MCPService()
        resource = await mcp_service.read_resource(
            server_id=server_id,
            resource_uri=request.resource_uri,
            parameters=request.parameters
        )
        return {
            "success": True,
            "data": resource
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}/status")
async def get_server_status(server_id: str):
    """Get MCP server status"""
    try:
        mcp_service = MCPService()
        status = await mcp_service.get_server_status(server_id)
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
