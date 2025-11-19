"""
Dataset management endpoints using Supabase
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
import io
import csv

from services.dataset_service import DatasetService
from core.database import get_supabase

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    filters: Optional[dict] = None


@router.get("/")
async def get_datasets():
    """Get list of all available datasets"""
    try:
        dataset_service = DatasetService()
        datasets = await dataset_service.list_datasets()
        return {
            "success": True,
            "data": datasets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_name}")
async def get_dataset(
    dataset_name: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    filters: Optional[str] = None
):
    """Get dataset with pagination and filtering"""
    try:
        dataset_service = DatasetService()
        data = await dataset_service.get_dataset(
            dataset_name=dataset_name,
            limit=limit,
            offset=offset,
            filters=filters
        )
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{dataset_name}/query")
async def query_dataset(dataset_name: str, request: QueryRequest):
    """Query dataset with natural language"""
    try:
        dataset_service = DatasetService()
        results = await dataset_service.query_dataset(
            dataset_name=dataset_name,
            query=request.query,
            filters=request.filters
        )
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_name}/stats")
async def get_dataset_stats(dataset_name: str):
    """Get dataset statistics"""
    try:
        dataset_service = DatasetService()
        stats = await dataset_service.get_dataset_stats(dataset_name)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_name}/export")
async def export_dataset(
    dataset_name: str,
    format: str = Query("csv", regex="^(csv|json|parquet)$"),
    filters: Optional[str] = None
):
    """Export dataset in specified format"""
    try:
        dataset_service = DatasetService()
        data = await dataset_service.export_dataset(
            dataset_name=dataset_name,
            format=format,
            filters=filters
        )
        
        if format == "csv":
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={dataset_name}.csv"}
            )
        elif format == "json":
            return {
                "success": True,
                "data": data
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_name}/schema")
async def get_dataset_schema(dataset_name: str):
    """Get dataset schema information"""
    try:
        dataset_service = DatasetService()
        schema = await dataset_service.get_schema(dataset_name)
        return {
            "success": True,
            "data": schema
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
