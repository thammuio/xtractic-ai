import os
from typing import Optional
import asyncpg
from mcp.server.fastmcp import FastMCP
import json
import logging
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("xtractic-postgres")

# Get configuration from environment variables
def get_config():
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
        "database": os.environ.get("POSTGRES_DB", "postgres"),
        "user": os.environ.get("POSTGRES_USER", ""),
        "password": os.environ.get("POSTGRES_PASSWORD", "")
    }


async def get_db_connection():
    """Create and return a database connection"""
    config = get_config()
    try:
        conn = await asyncpg.connect(
            host=config["host"],
            port=int(config["port"]),
            database=config["database"],
            user=config["user"],
            password=config["password"]
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise


@mcp.tool(
    name="get_file_processing_stats",
    description="Get file processing statistics with optional filters for status, workflow_id, or date range"
)
async def get_file_processing_stats(
    status: Optional[str] = None,
    workflow_id: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Retrieve file processing statistics from the database
    
    :param status: Filter by processing status (e.g., 'completed', 'failed', 'processing')
    :param workflow_id: Filter by specific workflow ID
    :param limit: Maximum number of records to return (default: 10)
    :return: JSON string with file processing stats
    """
    try:
        conn = await get_db_connection()
        
        query = "SELECT * FROM xtracticai.file_processing_stats WHERE 1=1"
        params = []
        param_idx = 1
        
        if status:
            query += f" AND processing_status = ${param_idx}"
            params.append(status)
            param_idx += 1
            
        if workflow_id:
            query += f" AND workflow_id = ${param_idx}"
            params.append(workflow_id)
            param_idx += 1
        
        query += f" ORDER BY uploaded_at DESC LIMIT ${param_idx}"
        params.append(limit)
        
        rows = await conn.fetch(query, *params)
        await conn.close()
        
        results = [dict(row) for row in rows]
        
        # Convert datetime objects to ISO format strings
        for result in results:
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        logging.error(f"Error fetching file processing stats: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="get_workflow_submissions",
    description="Get workflow submission records with optional filters"
)
async def get_workflow_submissions(
    status: Optional[str] = None,
    workflow_name: Optional[str] = None,
    trace_id: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Retrieve workflow submission records
    
    :param status: Filter by submission status (e.g., 'submitted', 'completed', 'failed')
    :param workflow_name: Filter by workflow name
    :param trace_id: Get specific submission by trace_id
    :param limit: Maximum number of records to return (default: 10)
    :return: JSON string with workflow submissions
    """
    try:
        conn = await get_db_connection()
        
        query = "SELECT * FROM xtracticai.workflow_submissions WHERE 1=1"
        params = []
        param_idx = 1
        
        if trace_id:
            query += f" AND trace_id = ${param_idx}"
            params.append(trace_id)
            param_idx += 1
        elif status:
            query += f" AND status = ${param_idx}"
            params.append(status)
            param_idx += 1
            
        if workflow_name:
            query += f" AND workflow_name = ${param_idx}"
            params.append(workflow_name)
            param_idx += 1
        
        query += f" ORDER BY submitted_at DESC LIMIT ${param_idx}"
        params.append(limit)
        
        rows = await conn.fetch(query, *params)
        await conn.close()
        
        results = [dict(row) for row in rows]
        
        # Convert datetime objects to ISO format strings
        for result in results:
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        logging.error(f"Error fetching workflow submissions: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="get_processing_summary",
    description="Get a summary of file processing statistics including counts by status and workflow"
)
async def get_processing_summary() -> str:
    """
    Get aggregated statistics about file processing
    
    :return: JSON string with summary statistics
    """
    try:
        conn = await get_db_connection()
        
        # Get counts by status
        status_query = """
            SELECT processing_status, COUNT(*) as count, 
                   AVG(processing_duration_ms) as avg_duration,
                   SUM(records_extracted) as total_records
            FROM xtracticai.file_processing_stats
            GROUP BY processing_status
        """
        
        # Get counts by workflow
        workflow_query = """
            SELECT workflow_name, COUNT(*) as count,
                   AVG(processing_duration_ms) as avg_duration,
                   SUM(records_extracted) as total_records
            FROM xtracticai.file_processing_stats
            WHERE workflow_name IS NOT NULL
            GROUP BY workflow_name
        """
        
        # Get recent failures
        failures_query = """
            SELECT file_name, error_message, uploaded_at
            FROM xtracticai.file_processing_stats
            WHERE processing_status = 'failed'
            ORDER BY uploaded_at DESC
            LIMIT 5
        """
        
        status_rows = await conn.fetch(status_query)
        workflow_rows = await conn.fetch(workflow_query)
        failures_rows = await conn.fetch(failures_query)
        
        await conn.close()
        
        summary = {
            "by_status": [dict(row) for row in status_rows],
            "by_workflow": [dict(row) for row in workflow_rows],
            "recent_failures": [dict(row) for row in failures_rows]
        }
        
        # Convert datetime objects to ISO format strings
        for failure in summary["recent_failures"]:
            if failure.get("uploaded_at"):
                failure["uploaded_at"] = failure["uploaded_at"].isoformat()
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        logging.error(f"Error fetching processing summary: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="get_workflow_submission_summary",
    description="Get aggregated statistics about workflow submissions"
)
async def get_workflow_submission_summary() -> str:
    """
    Get summary statistics for workflow submissions
    
    :return: JSON string with workflow submission statistics
    """
    try:
        conn = await get_db_connection()
        
        # Get counts by status
        status_query = """
            SELECT status, COUNT(*) as count
            FROM xtracticai.workflow_submissions
            GROUP BY status
        """
        
        # Get counts by workflow
        workflow_query = """
            SELECT workflow_name, COUNT(*) as count,
                   SUM(CASE WHEN crew_kickoff_completed THEN 1 ELSE 0 END) as completed_kickoffs
            FROM xtracticai.workflow_submissions
            WHERE workflow_name IS NOT NULL
            GROUP BY workflow_name
        """
        
        # Get pending submissions
        pending_query = """
            SELECT trace_id, workflow_name, file_name, submitted_at
            FROM xtracticai.workflow_submissions
            WHERE status = 'submitted' AND completed_at IS NULL
            ORDER BY submitted_at DESC
            LIMIT 10
        """
        
        status_rows = await conn.fetch(status_query)
        workflow_rows = await conn.fetch(workflow_query)
        pending_rows = await conn.fetch(pending_query)
        
        await conn.close()
        
        summary = {
            "by_status": [dict(row) for row in status_rows],
            "by_workflow": [dict(row) for row in workflow_rows],
            "pending_submissions": [dict(row) for row in pending_rows]
        }
        
        # Convert datetime objects to ISO format strings
        for pending in summary["pending_submissions"]:
            if pending.get("submitted_at"):
                pending["submitted_at"] = pending["submitted_at"].isoformat()
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        logging.error(f"Error fetching workflow submission summary: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="search_files",
    description="Search for processed files by name pattern or file type"
)
async def search_files(
    file_name_pattern: Optional[str] = None,
    file_type: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Search for files in processing stats
    
    :param file_name_pattern: Search pattern for file name (supports SQL LIKE syntax with %)
    :param file_type: Filter by file type (e.g., 'pdf', 'csv', 'json')
    :param limit: Maximum number of records to return (default: 10)
    :return: JSON string with matching files
    """
    try:
        conn = await get_db_connection()
        
        query = "SELECT * FROM xtracticai.file_processing_stats WHERE 1=1"
        params = []
        param_idx = 1
        
        if file_name_pattern:
            query += f" AND file_name ILIKE ${param_idx}"
            params.append(f"%{file_name_pattern}%")
            param_idx += 1
            
        if file_type:
            query += f" AND file_type = ${param_idx}"
            params.append(file_type)
            param_idx += 1
        
        query += f" ORDER BY uploaded_at DESC LIMIT ${param_idx}"
        params.append(limit)
        
        rows = await conn.fetch(query, *params)
        await conn.close()
        
        results = [dict(row) for row in rows]
        
        # Convert datetime objects to ISO format strings
        for result in results:
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        logging.error(f"Error searching files: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="get_failed_submissions",
    description="Get all failed workflow submissions with error details"
)
async def get_failed_submissions(limit: int = 10) -> str:
    """
    Retrieve failed workflow submissions with error messages
    
    :param limit: Maximum number of records to return (default: 10)
    :return: JSON string with failed submissions
    """
    try:
        conn = await get_db_connection()
        
        query = """
            SELECT trace_id, workflow_name, file_name, status, 
                   error_message, submitted_at, completed_at
            FROM xtracticai.workflow_submissions
            WHERE error_message IS NOT NULL OR status = 'failed'
            ORDER BY submitted_at DESC
            LIMIT $1
        """
        
        rows = await conn.fetch(query, limit)
        await conn.close()
        
        results = [dict(row) for row in rows]
        
        # Convert datetime objects to ISO format strings
        for result in results:
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        logging.error(f"Error fetching failed submissions: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="get_workflow_performance",
    description="Get performance metrics for workflows including average processing time and success rate"
)
async def get_workflow_performance() -> str:
    """
    Get performance metrics for each workflow
    
    :return: JSON string with workflow performance data
    """
    try:
        conn = await get_db_connection()
        
        query = """
            SELECT 
                workflow_name,
                COUNT(*) as total_runs,
                COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as successful_runs,
                COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed_runs,
                AVG(processing_duration_ms) as avg_duration_ms,
                MIN(processing_duration_ms) as min_duration_ms,
                MAX(processing_duration_ms) as max_duration_ms,
                SUM(records_extracted) as total_records_extracted,
                AVG(records_extracted) as avg_records_per_run
            FROM xtracticai.file_processing_stats
            WHERE workflow_name IS NOT NULL
            GROUP BY workflow_name
            ORDER BY total_runs DESC
        """
        
        rows = await conn.fetch(query)
        await conn.close()
        
        results = [dict(row) for row in rows]
        
        # Calculate success rate
        for result in results:
            if result["total_runs"] > 0:
                result["success_rate"] = (result["successful_runs"] / result["total_runs"]) * 100
            else:
                result["success_rate"] = 0
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        logging.error(f"Error fetching workflow performance: {e}")
        return json.dumps({"error": str(e)})


def main():
    # Initialize and run the server
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
