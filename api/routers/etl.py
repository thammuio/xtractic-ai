"""
ETL job management endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from api.services.etl_service import ETLService

router = APIRouter()


class ETLJobConfig(BaseModel):
    job_name: str
    source_type: str  # pdf, csv, json, api, database
    source_config: Dict[str, Any]
    destination_type: str  # supabase, rag_db, s3
    destination_config: Dict[str, Any]
    transformations: Optional[List[Dict[str, Any]]] = None
    schedule: Optional[str] = None


@router.post("/run")
async def run_etl(config: ETLJobConfig, background_tasks: BackgroundTasks):
    """Run ETL job"""
    try:
        etl_service = ETLService()
        job_id = await etl_service.run_etl(
            job_name=config.job_name,
            source_type=config.source_type,
            source_config=config.source_config,
            destination_type=config.destination_type,
            destination_config=config.destination_config,
            transformations=config.transformations
        )
        return {
            "success": True,
            "data": {"job_id": job_id},
            "message": "ETL job started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def get_jobs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get all ETL jobs"""
    try:
        etl_service = ETLService()
        jobs = await etl_service.list_jobs(status=status, limit=limit, offset=offset)
        return {
            "success": True,
            "data": jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get ETL job status"""
    try:
        etl_service = ETLService()
        job = await etl_service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {
            "success": True,
            "data": job
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}/logs")
async def get_job_logs(job_id: str, limit: int = 100):
    """Get ETL job logs"""
    try:
        etl_service = ETLService()
        logs = await etl_service.get_job_logs(job_id, limit=limit)
        return {
            "success": True,
            "data": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel running ETL job"""
    try:
        etl_service = ETLService()
        result = await etl_service.cancel_job(job_id)
        return {
            "success": True,
            "message": "Job cancelled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), destination: str = "supabase"):
    """Upload file for processing"""
    try:
        etl_service = ETLService()
        result = await etl_service.process_upload(file, destination)
        return {
            "success": True,
            "data": result,
            "message": "File uploaded and processing started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete ETL job"""
    try:
        etl_service = ETLService()
        await etl_service.delete_job(job_id)
        return {
            "success": True,
            "message": "Job deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
