"""
Stats Service - Track agents, MCP servers, file processing, and workflow executions
"""
import asyncpg
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json

from api.core.config import settings


class StatsService:
    """Service for tracking ETL workflow statistics"""
    
    def __init__(self):
        self.db_url = settings.BACKEND_DATABASE_URL
        self._pool = None
    
    async def _get_pool(self):
        """Get or create connection pool"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.db_url)
        return self._pool
    
    async def init_schema(self):
        """Initialize schema and all stats tables"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Create schema
            await conn.execute("""
                CREATE SCHEMA IF NOT EXISTS xtracticai;
            """)
            
            # Agent stats table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS xtracticai.agent_stats (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    agent_name VARCHAR(255) NOT NULL,
                    agent_type VARCHAR(100),
                    status VARCHAR(50),
                    deployment_url TEXT,
                    total_executions INTEGER DEFAULT 0,
                    successful_executions INTEGER DEFAULT 0,
                    failed_executions INTEGER DEFAULT 0,
                    last_execution_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_agent_stats_name ON xtracticai.agent_stats(agent_name);
                CREATE INDEX IF NOT EXISTS idx_agent_stats_status ON xtracticai.agent_stats(status);
            """)
            
            # MCP server stats table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS xtracticai.mcp_server_stats (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    server_name VARCHAR(255) NOT NULL,
                    server_type VARCHAR(100),
                    status VARCHAR(50),
                    endpoint_url TEXT,
                    total_calls INTEGER DEFAULT 0,
                    successful_calls INTEGER DEFAULT 0,
                    failed_calls INTEGER DEFAULT 0,
                    last_call_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_mcp_stats_name ON xtracticai.mcp_server_stats(server_name);
                CREATE INDEX IF NOT EXISTS idx_mcp_stats_status ON xtracticai.mcp_server_stats(status);
            """)
            
            # File processing stats table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS xtracticai.file_processing_stats (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    file_name VARCHAR(500) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    file_size_bytes BIGINT,
                    processing_status VARCHAR(50),
                    records_extracted INTEGER DEFAULT 0,
                    workflow_id VARCHAR(255),
                    workflow_name VARCHAR(255),
                    error_message TEXT,
                    processing_duration_ms FLOAT,
                    uploaded_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_file_stats_type ON xtracticai.file_processing_stats(file_type);
                CREATE INDEX IF NOT EXISTS idx_file_stats_status ON xtracticai.file_processing_stats(processing_status);
                CREATE INDEX IF NOT EXISTS idx_file_stats_uploaded ON xtracticai.file_processing_stats(uploaded_at DESC);
            """)
            
            # Workflow execution stats table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS xtracticai.workflow_execution_stats (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    workflow_id VARCHAR(255) NOT NULL,
                    workflow_name VARCHAR(255) NOT NULL,
                    execution_type VARCHAR(50),
                    status VARCHAR(50),
                    input_files_count INTEGER DEFAULT 0,
                    output_records_count INTEGER DEFAULT 0,
                    records_processed INTEGER DEFAULT 0,
                    records_failed INTEGER DEFAULT 0,
                    agents_used JSONB,
                    tools_used JSONB,
                    duration_ms FLOAT,
                    error_message TEXT,
                    metadata JSONB,
                    started_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_workflow_stats_id ON xtracticai.workflow_execution_stats(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_workflow_stats_status ON xtracticai.workflow_execution_stats(status);
                CREATE INDEX IF NOT EXISTS idx_workflow_stats_started ON xtracticai.workflow_execution_stats(started_at DESC);
            """)
            
            # Workflow submissions table (for tracking trace_id based submissions)
            await conn.execute("""
                DROP TABLE IF EXISTS xtracticai.workflow_submissions;
                
                CREATE TABLE xtracticai.workflow_submissions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    trace_id VARCHAR NOT NULL UNIQUE,
                    workflow_url VARCHAR NOT NULL,
                    uploaded_file_url VARCHAR NOT NULL,
                    query TEXT,
                    status VARCHAR DEFAULT 'submitted',
                    workflow_id VARCHAR,
                    workflow_name VARCHAR,
                    execution_id UUID,
                    file_id UUID,
                    error_message TEXT,
                    metadata JSONB,
                    submitted_at TIMESTAMP DEFAULT NOW(),
                    last_polled_at TIMESTAMP,
                    completed_at TIMESTAMP
                );
                CREATE INDEX idx_workflow_submissions_trace_id ON xtracticai.workflow_submissions(trace_id);
                CREATE INDEX idx_workflow_submissions_status ON xtracticai.workflow_submissions(status);
                CREATE INDEX idx_workflow_submissions_submitted_at ON xtracticai.workflow_submissions(submitted_at DESC);
            """)
    
    async def track_agent(self, agent_name: str, agent_type: str, status: str, deployment_url: str = None) -> str:
        """Track or update agent deployment"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Check if agent exists
            row = await conn.fetchrow(
                "SELECT id FROM xtracticai.agent_stats WHERE agent_name = $1",
                agent_name
            )
            
            if row:
                await conn.execute("""
                    UPDATE xtracticai.agent_stats
                    SET status = $1, deployment_url = $2, updated_at = NOW()
                    WHERE agent_name = $3
                """, status, deployment_url, agent_name)
                return str(row['id'])
            else:
                new_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO xtracticai.agent_stats
                    (id, agent_name, agent_type, status, deployment_url)
                    VALUES ($1, $2, $3, $4, $5)
                """, uuid.UUID(new_id), agent_name, agent_type, status, deployment_url)
                return new_id
    
    async def update_agent_execution(self, agent_name: str, success: bool):
        """Update agent execution counts"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if success:
                await conn.execute("""
                    UPDATE xtracticai.agent_stats
                    SET total_executions = total_executions + 1,
                        successful_executions = successful_executions + 1,
                        last_execution_at = NOW(),
                        updated_at = NOW()
                    WHERE agent_name = $1
                """, agent_name)
            else:
                await conn.execute("""
                    UPDATE xtracticai.agent_stats
                    SET total_executions = total_executions + 1,
                        failed_executions = failed_executions + 1,
                        last_execution_at = NOW(),
                        updated_at = NOW()
                    WHERE agent_name = $1
                """, agent_name)
    
    async def track_mcp_server(self, server_name: str, server_type: str, status: str, endpoint_url: str = None) -> str:
        """Track or update MCP server"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id FROM xtracticai.mcp_server_stats WHERE server_name = $1",
                server_name
            )
            
            if row:
                await conn.execute("""
                    UPDATE xtracticai.mcp_server_stats
                    SET status = $1, endpoint_url = $2, updated_at = NOW()
                    WHERE server_name = $3
                """, status, endpoint_url, server_name)
                return str(row['id'])
            else:
                new_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO xtracticai.mcp_server_stats
                    (id, server_name, server_type, status, endpoint_url)
                    VALUES ($1, $2, $3, $4, $5)
                """, uuid.UUID(new_id), server_name, server_type, status, endpoint_url)
                return new_id
    
    async def update_mcp_call(self, server_name: str, success: bool):
        """Update MCP server call counts"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if success:
                await conn.execute("""
                    UPDATE xtracticai.mcp_server_stats
                    SET total_calls = total_calls + 1,
                        successful_calls = successful_calls + 1,
                        last_call_at = NOW(),
                        updated_at = NOW()
                    WHERE server_name = $1
                """, server_name)
            else:
                await conn.execute("""
                    UPDATE xtracticai.mcp_server_stats
                    SET total_calls = total_calls + 1,
                        failed_calls = failed_calls + 1,
                        last_call_at = NOW(),
                        updated_at = NOW()
                    WHERE server_name = $1
                """, server_name)
    
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
            # Agent stats
            agent_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_agents,
                    COUNT(*) FILTER (WHERE status = 'deployed') as deployed_agents,
                    COUNT(*) FILTER (WHERE status = 'running') as running_agents,
                    COALESCE(SUM(total_executions), 0) as total_agent_executions,
                    COALESCE(SUM(successful_executions), 0) as successful_agent_executions
                FROM xtracticai.agent_stats
            """)
            
            # MCP server stats
            mcp_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_servers,
                    COUNT(*) FILTER (WHERE status = 'active') as active_servers,
                    COALESCE(SUM(total_calls), 0) as total_mcp_calls,
                    COALESCE(SUM(successful_calls), 0) as successful_mcp_calls
                FROM xtracticai.mcp_server_stats
            """)
            
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
                ORDER BY count DESC
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
                "agents": {
                    "total": agent_stats['total_agents'],
                    "deployed": agent_stats['deployed_agents'],
                    "running": agent_stats['running_agents'],
                    "total_executions": agent_stats['total_agent_executions'],
                    "successful_executions": agent_stats['successful_agent_executions']
                },
                "mcp_servers": {
                    "total": mcp_stats['total_servers'],
                    "active": mcp_stats['active_servers'],
                    "total_calls": mcp_stats['total_mcp_calls'],
                    "successful_calls": mcp_stats['successful_mcp_calls']
                },
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
    
    async def get_agents(self) -> List[Dict]:
        """Get all agents"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM xtracticai.agent_stats ORDER BY created_at DESC")
            return [dict(row) for row in rows]
    
    async def get_mcp_servers(self) -> List[Dict]:
        """Get all MCP servers"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM xtracticai.mcp_server_stats ORDER BY created_at DESC")
            return [dict(row) for row in rows]
    
    async def get_recent_file_uploads(self, limit: int = 50) -> List[Dict]:
        """Get recent file uploads"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM xtracticai.file_processing_stats
                ORDER BY uploaded_at DESC
                LIMIT $1
            """, limit)
            return [dict(row) for row in rows]
    
    async def get_recent_workflow_executions(self, limit: int = 50) -> List[Dict]:
        """Get recent workflow executions"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM xtracticai.workflow_execution_stats
                ORDER BY started_at DESC
                LIMIT $1
            """, limit)
            return [dict(row) for row in rows]
    
    async def close(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
