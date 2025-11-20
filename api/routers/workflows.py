"""
Workflow management endpoints for Cloudera AI Agent Studio
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from api.services.cloudera_service import ClouderaService
from api.services.stats_service import StatsService

router = APIRouter()


class WorkflowSubmitRequest(BaseModel):
    uploaded_file_url: str
    query: str


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

