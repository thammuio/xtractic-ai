"""
Workflow management endpoints for Cloudera AI Agent Studio
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from api.services.cloudera_service import ClouderaService
from api.services.workflow_service import WorkflowService
from api.utils.cloudera_utils import (
    get_all_cloudera_env_vars,
    setup_applications,
    get_cloudera_credentials,
    get_agent_studio_applications,
    get_env_var
)
router = APIRouter()


class WorkflowSubmitRequest(BaseModel):
    uploaded_file_url: str
    query: str


@router.get("/stats")
async def get_workflows_stats(
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
        workflow_service = WorkflowService()
        
        stats = await workflow_service.get_workflow_submission_stats(
            limit=limit,
            status=status
        )
        
        await workflow_service.close()
        
        return {
            "success": True,
            "data": stats["submissions"],
            "count": stats["count"],
            "summary": stats["summary"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/details")
async def get_workflow_details():
    """Get workflow summary details for table display
    
    Returns aggregated workflow information including:
    - Workflow name and ID
    - File count processed
    - Success rate
    - Last run timestamp
    - Current status
    - Total records extracted
    """
    try:
        workflow_service = WorkflowService()
        
        details = await workflow_service.get_workflow_details_summary()
        
        await workflow_service.close()
        
        return {
            "success": True,
            "data": details["workflows"],
            "count": details["count"]
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

