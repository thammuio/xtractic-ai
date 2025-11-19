"""
Workflow management endpoints for Cloudera AI Agent Studio
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from services.cloudera_service import ClouderaService
from core.database import get_supabase

router = APIRouter()


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_config: Dict[str, Any]
    workflow_steps: List[Dict[str, Any]]
    schedule: Optional[str] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_config: Optional[Dict[str, Any]] = None
    workflow_steps: Optional[List[Dict[str, Any]]] = None
    schedule: Optional[str] = None
    status: Optional[str] = None


class WorkflowExecutionRequest(BaseModel):
    input_data: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


@router.get("/")
async def get_workflows(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get all workflows with optional filtering"""
    try:
        cloudera_service = ClouderaService()
        workflows = await cloudera_service.list_workflows(status=status, limit=limit, offset=offset)
        return {
            "success": True,
            "data": workflows,
            "count": len(workflows)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_workflow_stats():
    """Get workflow statistics"""
    try:
        cloudera_service = ClouderaService()
        stats = await cloudera_service.get_workflow_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_workflows(limit: int = 10):
    """Get recently executed workflows"""
    try:
        cloudera_service = ClouderaService()
        workflows = await cloudera_service.get_recent_workflows(limit=limit)
        return {
            "success": True,
            "data": workflows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow by ID"""
    try:
        cloudera_service = ClouderaService()
        workflow = await cloudera_service.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {
            "success": True,
            "data": workflow
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_workflow(workflow: WorkflowCreate):
    """Create a new workflow"""
    try:
        cloudera_service = ClouderaService()
        result = await cloudera_service.create_workflow(
            name=workflow.name,
            description=workflow.description,
            agent_config=workflow.agent_config,
            workflow_steps=workflow.workflow_steps,
            schedule=workflow.schedule
        )
        return {
            "success": True,
            "data": result,
            "message": "Workflow created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str, workflow: WorkflowUpdate):
    """Update workflow"""
    try:
        cloudera_service = ClouderaService()
        result = await cloudera_service.update_workflow(
            workflow_id=workflow_id,
            **workflow.model_dump(exclude_none=True)
        )
        return {
            "success": True,
            "data": result,
            "message": "Workflow updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete workflow"""
    try:
        cloudera_service = ClouderaService()
        await cloudera_service.delete_workflow(workflow_id)
        return {
            "success": True,
            "message": "Workflow deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks
):
    """Start workflow execution"""
    try:
        cloudera_service = ClouderaService()
        execution = await cloudera_service.start_workflow(
            workflow_id=workflow_id,
            input_data=request.input_data,
            parameters=request.parameters
        )
        return {
            "success": True,
            "data": execution,
            "message": "Workflow started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/stop")
async def stop_workflow(workflow_id: str):
    """Stop workflow execution"""
    try:
        cloudera_service = ClouderaService()
        result = await cloudera_service.stop_workflow(workflow_id)
        return {
            "success": True,
            "data": result,
            "message": "Workflow stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
    limit: int = 20,
    offset: int = 0
):
    """Get workflow execution history"""
    try:
        cloudera_service = ClouderaService()
        executions = await cloudera_service.get_workflow_executions(
            workflow_id=workflow_id,
            limit=limit,
            offset=offset
        )
        return {
            "success": True,
            "data": executions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions/{execution_id}")
async def get_execution_details(workflow_id: str, execution_id: str):
    """Get detailed execution information"""
    try:
        cloudera_service = ClouderaService()
        execution = await cloudera_service.get_execution_details(workflow_id, execution_id)
        return {
            "success": True,
            "data": execution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions/{execution_id}/logs")
async def get_execution_logs(workflow_id: str, execution_id: str):
    """Get execution logs"""
    try:
        cloudera_service = ClouderaService()
        logs = await cloudera_service.get_execution_logs(workflow_id, execution_id)
        return {
            "success": True,
            "data": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
