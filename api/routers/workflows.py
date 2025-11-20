"""
Workflow management endpoints for Cloudera AI Agent Studio
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from api.services.cloudera_service import ClouderaService
from api.services.stats_service import StatsService
from api.core.database import get_supabase
from api.utils.cloudera_utils import (
    get_all_cloudera_env_vars,
    setup_applications,
    get_cloudera_credentials,
    get_agent_studio_applications,
    get_env_var
)

router = APIRouter()


class WorkflowKickoffRequest(BaseModel):
    uploaded_file_url: str


class WorkflowSubmitRequest(BaseModel):
    uploaded_file_url: str
    query: str
    

class WorkflowEventsRequest(BaseModel):
    trace_id: str


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
async def get_workflow_stats(
    limit: int = 50,
    status: Optional[str] = None
):
    """Get unique workflow submissions with file processing details
    
    Returns unique rows based on filename extracted from uploaded_file_url.
    If multiple submissions exist for the same file, only the most recent one is returned.
    
    Correlates workflow_submissions with file_processing_stats by matching:
    - file_name from file_processing_stats
    - extracted filename from uploaded_file_url in workflow_submissions
    """
    try:
        stats_service = StatsService()
        await stats_service.init_schema()
        
        stats = await stats_service.get_workflow_submission_stats(
            limit=limit,
            status=status
        )
        
        await stats_service.close()
        
        return {
            "success": True,
            "data": stats["submissions"],
            "count": stats["count"],
            "summary": stats["summary"]
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


@router.get("/deployed")
async def get_deployed_workflows():
    """Get all deployed workflows/applications from Agent Studio project"""
    try:
        # Get applications with better error handling
        try:
            applications = get_agent_studio_applications()
        except Exception as app_error:
            # Return empty list with error details instead of failing
            return {
                "success": False,
                "data": [],
                "count": 0,
                "workflow_count": 0,
                "running_count": 0,
                "error": str(app_error),
                "message": f"Failed to fetch applications from Agent Studio: {str(app_error)}"
            }
        
        # Get CDSW_DOMAIN for URL construction
        try:
            cdsw_domain = get_env_var("CDSW_DOMAIN")
        except Exception:
            cdsw_domain = None
        
        # Filter and format workflow applications
        workflows = []
        for app in applications:
            # Check if it's a workflow application
            is_workflow = "Workflow:" in app.get("name", "")
            
            # Construct full URL: subdomain.CDSW_DOMAIN
            subdomain = app.get("subdomain")
            url = None
            if subdomain and cdsw_domain:
                url = f"https://{subdomain}.{cdsw_domain}"
            
            workflow_info = {
                "id": app.get("id"),
                "name": app.get("name"),
                "description": app.get("description"),
                "subdomain": subdomain,
                "status": app.get("status"),
                "url": url,
                "creator": app.get("creator", {}),
                "created_at": app.get("created_at"),
                "updated_at": app.get("updated_at"),
                "running_at": app.get("running_at"),
                "stopped_at": app.get("stopped_at"),
                "resources": {
                    "cpu": app.get("cpu"),
                    "memory": app.get("memory"),
                    "gpu": app.get("nvidia_gpu", 0)
                },
                "is_workflow": is_workflow,
                "project_id": app.get("project_id")
            }
            
            # Extract workflow ID from environment if available
            env_str = app.get("environment", "{}")
            try:
                import json
                env_dict = json.loads(env_str) if isinstance(env_str, str) else env_str
                workflow_info["workflow_id"] = env_dict.get("AGENT_STUDIO_DEPLOYED_WORKFLOW_ID")
                workflow_info["model_id"] = env_dict.get("AGENT_STUDIO_DEPLOYED_MODEL_ID")
                workflow_info["render_mode"] = env_dict.get("AGENT_STUDIO_RENDER_MODE")
            except:
                pass
            
            workflows.append(workflow_info)
        
        return {
            "success": True,
            "data": workflows,
            "count": len(workflows),
            "workflow_count": len([w for w in workflows if w.get("is_workflow")]),
            "running_count": len([w for w in workflows if "RUNNING" in w.get("status", "")]),
            "message": f"Found {len(workflows)} application(s) in Agent Studio"
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


@router.post("/submit")
async def submit_workflow(request: WorkflowSubmitRequest):
    """Submit workflow with PDF URL and query to Agent Studio"""
    try:
        cloudera_service = ClouderaService()
        result = await cloudera_service.submit_workflow(
            uploaded_file_url=request.uploaded_file_url,
            query=request.query
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}/status")
async def get_workflow_status(trace_id: str):
    """Get status of a submitted workflow by trace_id
    
    Polls the workflow events API every 5 seconds to check status:
    - If events are returned: workflow is in-progress
    - If no response/error: workflow is completed
    """
    try:
        cloudera_service = ClouderaService()
        status = await cloudera_service.get_workflow_submission_status(trace_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deployed/kickoff")
async def kickoff_deployed_workflow(request: WorkflowKickoffRequest):
    """Start a deployed workflow execution with PDF URL"""
    try:
        cloudera_service = ClouderaService()
        result = await cloudera_service.kickoff_deployed_workflow(
            uploaded_file_url=request.uploaded_file_url
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployed/events")
async def get_deployed_workflow_events(trace_id: str):
    """Get events for a deployed workflow execution"""
    try:
        cloudera_service = ClouderaService()
        events = await cloudera_service.get_deployed_workflow_events(trace_id)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cloudera/env")
async def get_cloudera_environment():
    """Get Cloudera environment variables (for debugging/admin)"""
    try:
        env_vars = get_all_cloudera_env_vars()
        # Mask sensitive data
        masked_vars = {}
        for key, value in env_vars.items():
            if value and ("KEY" in key or "SECRET" in key):
                masked_vars[key] = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                masked_vars[key] = value
        
        return {
            "success": True,
            "data": masked_vars
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cloudera/credentials")
async def get_cloudera_creds():
    """Get Cloudera credentials info (masked for security)"""
    try:
        creds = get_cloudera_credentials()
        return {
            "success": True,
            "data": {
                "domain": creds["domain"],
                "workspace_domain": creds["workspace_domain"],
                "has_api_key": bool(creds["api_key"]),
                "has_project_id": bool(creds["project_id"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AppSetupRequest(BaseModel):
    api_subdomain: str = "xtracticai-api"
    ui_subdomain: str = "xtracticai-ui"


@router.post("/cloudera/setup-apps")
async def setup_cloudera_applications(request: AppSetupRequest):
    """Setup and configure Cloudera applications"""
    try:
        result = setup_applications(
            api_subdomain=request.api_subdomain,
            ui_subdomain=request.ui_subdomain
        )
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
