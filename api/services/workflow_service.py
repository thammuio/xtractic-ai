"""
Workflow Service - Track and manage workflow submissions and processing
"""
import asyncpg
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from api.core.config import settings
from api.utils.cloudera_utils import (
    get_all_cloudera_env_vars,
    setup_applications,
    get_cloudera_credentials,
    get_agent_studio_applications,
    get_env_var
)

class WorkflowService:
    """Service for tracking workflow submissions and file processing statistics"""
    
    def __init__(self):
        self.db_url = settings.BACKEND_DATABASE_URL
        self._pool = None
    
    async def _get_pool(self):
        """Get or create connection pool"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.db_url)
        return self._pool
    
    async def get_workflow_submission_stats(
        self,
        limit: int = 50,
        status: str = None
    ) -> Dict[str, Any]:
        """Get workflow submission statistics with file processing stats using UNION
        
        Returns combined details from both workflow_submissions and file_processing_stats
        tables, matching on file_name. This ensures all files from both sources are included.
        
        Args:
            limit: Maximum number of records to return
            status: Optional status filter (submitted, in-progress, completed, failed)
            
        Returns:
            Dictionary containing combined data list, count, and summary statistics
        """
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Build query with UNION to get all unique files from both tables
            # Status filter only applies to workflow_submissions part
            status_filter = "AND ws.status = $2" if status else ""
            status_params = [limit, status] if status else [limit]
            
            # Query that UNIONs both tables based on file_name
            query = f"""
                WITH extracted_filenames AS (
                    SELECT 
                        ws.id as ws_id,
                        ws.trace_id,
                        ws.workflow_url,
                        ws.uploaded_file_url,
                        ws.file_name as ws_file_name,
                        ws.query,
                        ws.status,
                        ws.workflow_id as ws_workflow_id,
                        ws.workflow_name as ws_workflow_name,
                        ws.execution_id,
                        ws.file_id,
                        ws.error_message as ws_error_message,
                        ws.metadata,
                        ws.submitted_at,
                        ws.last_polled_at,
                        ws.completed_at as ws_completed_at,
                        -- Extract filename from URL (after last /) if file_name is null
                        COALESCE(ws.file_name, REGEXP_REPLACE(ws.uploaded_file_url, '.*/', '')) as extracted_filename
                    FROM xtracticai.workflow_submissions ws
                    WHERE 1=1 {status_filter}
                ),
                combined_data AS (
                    -- Get all workflow submissions with their file processing data
                    SELECT 
                        ef.extracted_filename as file_name,
                        ef.ws_id,
                        ef.trace_id,
                        ef.workflow_url,
                        ef.uploaded_file_url,
                        ef.query,
                        ef.status,
                        ef.ws_workflow_id,
                        ef.ws_workflow_name,
                        ef.execution_id,
                        ef.file_id,
                        ef.ws_error_message,
                        ef.metadata,
                        ef.submitted_at,
                        ef.last_polled_at,
                        ef.ws_completed_at,
                        fps.id as file_processing_id,
                        fps.file_type,
                        fps.file_size_bytes,
                        fps.processing_status,
                        fps.records_extracted,
                        fps.workflow_id as fps_workflow_id,
                        fps.workflow_name as fps_workflow_name,
                        fps.processing_duration_ms,
                        fps.uploaded_at as file_uploaded_at,
                        fps.completed_at as file_completed_at,
                        fps.error_message as file_error_message,
                        COALESCE(ef.submitted_at, fps.uploaded_at) as sort_date
                    FROM extracted_filenames ef
                    FULL OUTER JOIN xtracticai.file_processing_stats fps 
                        ON fps.file_name = ef.extracted_filename
                )
                SELECT * FROM combined_data
                ORDER BY sort_date DESC NULLS LAST
                LIMIT $1
            """
            
            rows = await conn.fetch(query, *status_params)
            
            # Convert to list of dicts with combined structure
            submissions = []
            for row in rows:
                submission = {
                    "file_name": row["file_name"],
                    "workflow_submission": None,
                    "file_processing": None
                }
                
                # Add workflow submission details if present
                if row["ws_id"]:
                    submission["workflow_submission"] = {
                        "id": str(row["ws_id"]),
                        "trace_id": row["trace_id"],
                        "workflow_url": row["workflow_url"],
                        "uploaded_file_url": row["uploaded_file_url"],
                        "query": row["query"],
                        "status": row["status"],
                        "workflow_id": row["ws_workflow_id"],
                        "workflow_name": row["ws_workflow_name"],
                        "execution_id": str(row["execution_id"]) if row["execution_id"] else None,
                        "file_id": str(row["file_id"]) if row["file_id"] else None,
                        "error_message": row["ws_error_message"],
                        "metadata": row["metadata"],
                        "submitted_at": row["submitted_at"].isoformat() if row["submitted_at"] else None,
                        "last_polled_at": row["last_polled_at"].isoformat() if row["last_polled_at"] else None,
                        "completed_at": row["ws_completed_at"].isoformat() if row["ws_completed_at"] else None,
                    }
                
                # Add file processing details if present
                if row["file_processing_id"]:
                    submission["file_processing"] = {
                        "id": str(row["file_processing_id"]),
                        "file_name": row["file_name"],
                        "file_type": row["file_type"],
                        "file_size_bytes": row["file_size_bytes"],
                        "processing_status": row["processing_status"],
                        "records_extracted": row["records_extracted"],
                        "workflow_id": row["fps_workflow_id"],
                        "workflow_name": row["fps_workflow_name"],
                        "processing_duration_ms": float(row["processing_duration_ms"]) if row["processing_duration_ms"] else None,
                        "uploaded_at": row["file_uploaded_at"].isoformat() if row["file_uploaded_at"] else None,
                        "completed_at": row["file_completed_at"].isoformat() if row["file_completed_at"] else None,
                        "error_message": row["file_error_message"]
                    }
                
                submissions.append(submission)
            
            # Get summary statistics from both tables
            summary_query = """
                WITH ws_stats AS (
                    SELECT 
                        COUNT(*) as total_submissions,
                        COUNT(*) FILTER (WHERE status = 'submitted') as submitted_count,
                        COUNT(*) FILTER (WHERE status = 'in-progress') as in_progress_count,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed_count,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed_count,
                        COUNT(DISTINCT workflow_id) as unique_workflows
                    FROM xtracticai.workflow_submissions
            """
            
            if status:
                summary_query += " WHERE status = $1"
            
            summary_query += """
                ),
                fps_stats AS (
                    SELECT 
                        COUNT(*) as total_files,
                        COUNT(*) FILTER (WHERE processing_status = 'completed') as completed_files,
                        COUNT(*) FILTER (WHERE processing_status = 'failed') as failed_files,
                        COUNT(*) FILTER (WHERE processing_status = 'processing') as processing_files,
                        COALESCE(SUM(records_extracted), 0) as total_records_extracted,
                        COALESCE(SUM(file_size_bytes), 0) as total_file_size_bytes
                    FROM xtracticai.file_processing_stats
                )
                SELECT * FROM ws_stats, fps_stats
            """
            
            if status:
                summary_row = await conn.fetchrow(summary_query, status)
            else:
                summary_row = await conn.fetchrow(summary_query)
            
            summary = {
                "workflow_submissions": {
                    "total": summary_row["total_submissions"],
                    "by_status": {
                        "submitted": summary_row["submitted_count"],
                        "in_progress": summary_row["in_progress_count"],
                        "completed": summary_row["completed_count"],
                        "failed": summary_row["failed_count"]
                    },
                    "unique_workflows": summary_row["unique_workflows"]
                },
                "file_processing": {
                    "total_files": summary_row["total_files"],
                    "completed": summary_row["completed_files"],
                    "failed": summary_row["failed_files"],
                    "processing": summary_row["processing_files"],
                    "total_records_extracted": summary_row["total_records_extracted"],
                    "total_size_bytes": summary_row["total_file_size_bytes"]
                }
            }
            
            return {
                "submissions": submissions,
                "count": len(submissions),
                "summary": summary
            }
    
    async def get_workflow_details_summary(self) -> Dict[str, Any]:
        """Get workflow summary for table display
        
        Returns aggregated data per workflow including:
        - Workflow ID and name
        - Type (derived from file types processed)
        - Status (active/paused based on recent activity)
        - File count
        - Success rate
        - Last run timestamp
        - Total records extracted
        
        Returns:
            Dictionary with list of workflow summaries and count
        """
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Query to aggregate workflow data from both tables
            query = """
                WITH workflow_files AS (
                    -- Get workflow info from workflow_submissions
                    SELECT 
                        COALESCE(ws.workflow_id, fps.workflow_id) as workflow_id,
                        COALESCE(ws.workflow_name, fps.workflow_name) as workflow_name,
                        fps.file_type,
                        fps.file_name,
                        fps.processing_status,
                        fps.records_extracted,
                        fps.completed_at,
                        ws.status as submission_status,
                        ws.submitted_at,
                        COALESCE(fps.completed_at, ws.completed_at, fps.uploaded_at) as last_activity
                    FROM xtracticai.workflow_submissions ws
                    FULL OUTER JOIN xtracticai.file_processing_stats fps 
                        ON fps.file_name = COALESCE(ws.file_name, REGEXP_REPLACE(ws.uploaded_file_url, '.*/', ''))
                    WHERE COALESCE(ws.workflow_id, fps.workflow_id) IS NOT NULL
                ),
                workflow_summary AS (
                    SELECT 
                        workflow_id,
                        workflow_name,
                        -- Determine primary file type (most common)
                        MODE() WITHIN GROUP (ORDER BY file_type) as primary_type,
                        -- Count unique files
                        COUNT(DISTINCT file_name) as file_count,
                        -- Calculate success rate
                        ROUND(
                            100.0 * COUNT(*) FILTER (WHERE processing_status = 'completed') / 
                            NULLIF(COUNT(*) FILTER (WHERE processing_status IS NOT NULL), 0),
                            1
                        ) as success_rate,
                        -- Last run time
                        MAX(last_activity) as last_run,
                        -- Status (active if run in last 7 days, otherwise paused)
                        CASE 
                            WHEN MAX(last_activity) > NOW() - INTERVAL '7 days' THEN 'ACTIVE'
                            ELSE 'PAUSED'
                        END as status,
                        -- Total records
                        COALESCE(SUM(records_extracted), 0) as total_records_extracted,
                        -- Failed count
                        COUNT(*) FILTER (WHERE processing_status = 'failed') as failed_count,
                        -- Completed count
                        COUNT(*) FILTER (WHERE processing_status = 'completed') as completed_count
                    FROM workflow_files
                    GROUP BY workflow_id, workflow_name
                )
                SELECT 
                    workflow_id,
                    workflow_name,
                    COALESCE(UPPER(primary_type), 'UNKNOWN') as type,
                    status,
                    last_run,
                    COALESCE(success_rate, 0) as success_rate,
                    file_count,
                    total_records_extracted,
                    completed_count,
                    failed_count
                FROM workflow_summary
                ORDER BY last_run DESC NULLS LAST
            """
            
            rows = await conn.fetch(query)
            
            workflows = []
            for row in rows:
                workflows.append({
                    "workflow_id": row["workflow_id"],
                    "workflow_name": row["workflow_name"] or "Unnamed Workflow",
                    "type": row["type"],
                    "status": row["status"],
                    "last_run": row["last_run"].isoformat() if row["last_run"] else None,
                    "next_run": None,  # Can be enhanced later with scheduling info
                    "success_rate": float(row["success_rate"]) if row["success_rate"] else 0.0,
                    "file_count": row["file_count"],
                    "total_records_extracted": row["total_records_extracted"],
                    "completed_count": row["completed_count"],
                    "failed_count": row["failed_count"]
                })
            
            return {
                "workflows": workflows,
                "count": len(workflows)
            }
    
    async def close(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
