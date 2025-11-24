"""
Stats Service - Track file processing and workflow executions
"""
import asyncpg
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json

from api.core.config import settings
from api.core.database import get_db_pool


class StatsService:
    """Service for tracking file processing and workflow execution statistics"""
    
    def __init__(self):
        pass
    
    async def _get_pool(self):
        """Get shared connection pool"""
        return await get_db_pool()
    
    async def track_file_upload(
        self,
        file_name: str,
        file_type: str,
        file_size_bytes: int,
        workflow_id: str = None,
        workflow_name: str = None
    ) -> str:
        """Track file upload"""
        pool = await self._get_pool()
        new_id = str(uuid.uuid4())
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO xtracticai.file_processing_stats
                (id, file_name, file_type, file_size_bytes, processing_status, workflow_id, workflow_name)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, uuid.UUID(new_id), file_name, file_type, file_size_bytes, "processing", workflow_id, workflow_name)
        return new_id
    
    async def update_file_processing(
        self,
        file_id: str,
        status: str,
        records_extracted: int = 0,
        duration_ms: float = None,
        error_message: str = None
    ):
        """Update file processing result"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE xtracticai.file_processing_stats
                SET processing_status = $1,
                    records_extracted = $2,
                    processing_duration_ms = $3,
                    error_message = $4,
                    completed_at = NOW()
                WHERE id = $5
            """, status, records_extracted, duration_ms, error_message, uuid.UUID(file_id))
    
    async def track_workflow_execution(
        self,
        workflow_id: str,
        workflow_name: str,
        execution_type: str = "manual",
        agents_used: List[str] = None,
        tools_used: List[str] = None
    ) -> str:
        """Start tracking workflow execution"""
        pool = await self._get_pool()
        new_id = str(uuid.uuid4())
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO xtracticai.workflow_execution_stats
                (id, workflow_id, workflow_name, execution_type, status, agents_used, tools_used)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, uuid.UUID(new_id), workflow_id, workflow_name, execution_type, "running",
                json.dumps(agents_used or []), json.dumps(tools_used or []))
        return new_id
    
    async def update_workflow_execution(
        self,
        execution_id: str,
        status: str,
        input_files_count: int = 0,
        output_records_count: int = 0,
        records_processed: int = 0,
        records_failed: int = 0,
        duration_ms: float = None,
        error_message: str = None,
        metadata: Dict = None
    ):
        """Update workflow execution result"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE xtracticai.workflow_execution_stats
                SET status = $1,
                    input_files_count = $2,
                    output_records_count = $3,
                    records_processed = $4,
                    records_failed = $5,
                    duration_ms = $6,
                    error_message = $7,
                    metadata = $8,
                    completed_at = NOW()
                WHERE id = $9
            """, status, input_files_count, output_records_count, records_processed, records_failed,
                duration_ms, error_message, json.dumps(metadata) if metadata else None,
                uuid.UUID(execution_id))
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # File processing stats
            file_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_files_processed,
                    COALESCE(SUM(file_size_bytes), 0) as total_file_size_bytes,
                    COALESCE(SUM(records_extracted), 0) as total_records_extracted,
                    COUNT(*) FILTER (WHERE processing_status = 'completed') as successful_files,
                    COUNT(*) FILTER (WHERE processing_status = 'failed') as failed_files
                FROM xtracticai.file_processing_stats
            """)
            
            # File type breakdown
            file_types = await conn.fetch("""
                SELECT 
                    file_type,
                    COUNT(*) as count,
                    COALESCE(SUM(file_size_bytes), 0) as total_size
                FROM xtracticai.file_processing_stats
                GROUP BY file_type
                ORDER BY count ASC
            """)
            
            # Workflow stats
            workflow_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_executions,
                    COUNT(*) FILTER (WHERE status = 'success') as successful_executions,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_executions,
                    COUNT(*) FILTER (WHERE status = 'running') as running_executions,
                    COALESCE(SUM(records_processed), 0) as total_records_processed,
                    COALESCE(AVG(duration_ms), 0) as avg_execution_duration_ms
                FROM xtracticai.workflow_execution_stats
            """)
            
            return {
                "files": {
                    "total_processed": file_stats['total_files_processed'],
                    "total_size_bytes": file_stats['total_file_size_bytes'],
                    "total_records_extracted": file_stats['total_records_extracted'],
                    "successful": file_stats['successful_files'],
                    "failed": file_stats['failed_files'],
                    "by_type": [dict(row) for row in file_types]
                },
                "workflows": {
                    "total_executions": workflow_stats['total_executions'],
                    "successful": workflow_stats['successful_executions'],
                    "failed": workflow_stats['failed_executions'],
                    "running": workflow_stats['running_executions'],
                    "total_records_processed": workflow_stats['total_records_processed'],
                    "avg_duration_ms": float(workflow_stats['avg_execution_duration_ms'])
                }
            }
    
    async def get_recent_file_uploads(self, limit: int = 50) -> List[Dict]:
        """Get recent file uploads"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM xtracticai.file_processing_stats
                ORDER BY uploaded_at ASC
                LIMIT $1
            """, limit)
            return [dict(row) for row in rows]
    
    async def get_recent_workflow_executions(self, limit: int = 50) -> List[Dict]:
        """Get recent workflow executions"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM xtracticai.workflow_execution_stats
                ORDER BY started_at ASC
                LIMIT $1
            """, limit)
            return [dict(row) for row in rows]
