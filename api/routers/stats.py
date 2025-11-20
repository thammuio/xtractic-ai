"""
Activity Statistics endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from api.services.stats_service import StatsService

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics for agentic ETL workflows"""
    try:
        stats_service = StatsService()
        await stats_service.init_schema()
        
        dashboard = await stats_service.get_dashboard_stats()
        await stats_service.close()
        
        return {
            "success": True,
            "data": dashboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_agents():
    """Get all deployed agents"""
    try:
        stats_service = StatsService()
        await stats_service.init_schema()
        
        agents = await stats_service.get_agents()
        await stats_service.close()
        
        return {
            "success": True,
            "data": agents,
            "count": len(agents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp-servers")
async def get_mcp_servers():
    """Get all MCP servers"""
    try:
        stats_service = StatsService()
        await stats_service.init_schema()
        
        servers = await stats_service.get_mcp_servers()
        await stats_service.close()
        
        return {
            "success": True,
            "data": servers,
            "count": len(servers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def get_recent_files(limit: int = Query(50, ge=1, le=100)):
    """Get recent file uploads"""
    try:
        stats_service = StatsService()
        await stats_service.init_schema()
        
        files = await stats_service.get_recent_file_uploads(limit=limit)
        await stats_service.close()
        
        return {
            "success": True,
            "data": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows")
async def get_recent_workflows(limit: int = Query(50, ge=1, le=100)):
    """Get recent workflow executions"""
    try:
        stats_service = StatsService()
        await stats_service.init_schema()
        
        workflows = await stats_service.get_recent_workflow_executions(limit=limit)
        await stats_service.close()
        
        return {
            "success": True,
            "data": workflows,
            "count": len(workflows)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/init")
async def initialize_stats_schema():
    """Initialize stats schema and tables (admin endpoint)"""
    try:
        stats_service = StatsService()
        await stats_service.init_schema()
        await stats_service.close()
        
        return {
            "success": True,
            "message": "Stats schema and tables initialized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
