"""
Activity Statistics endpoints
"""
from fastapi import APIRouter, HTTPException

from api.services.stats_service import StatsService

router = APIRouter()


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

