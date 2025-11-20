"""
Cloudera AI Agent Studio Service
Manages workflows and agent interactions with Cloudera platform
"""
import aiohttp
import asyncpg
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import time

from api.core.config import settings
from api.utils.cloudera_utils import (
    get_cloudera_credentials,
    get_workflow_endpoint,
    get_cloudera_headers,
    get_pdf_to_relational_workflow_url,
    get_env_var
)


class ClouderaService:
    """Service for interacting with Cloudera AI Agent Studio"""
    
    def __init__(self):
        self.api_url = settings.CLOUDERA_API_URL
        self.api_key = settings.CLOUDERA_API_KEY
        self.workspace_id = settings.CLOUDERA_WORKSPACE_ID
        self.db_url = settings.BACKEND_DATABASE_URL
        self._pool = None
        
        # Use utility functions for deployed workflow configuration
        try:
            self.deployed_workflow_url = get_workflow_endpoint()
            self.deployed_headers = get_cloudera_headers()
        except Exception:
            # Fallback to settings if utilities fail
            self.deployed_workflow_url = settings.DEPLOYED_WORKFLOW_URL
            self.cdsw_api_key = settings.CDSW_APIV2_KEY
            self.deployed_headers = {
                "Authorization": f"Bearer {self.cdsw_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _get_pool(self):
        """Get or create connection pool"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.db_url)
        return self._pool
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Cloudera API"""
        url = f"{self.api_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, json=data) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"Cloudera API error: {error}")
                return await response.json()
    
    async def list_workflows(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all workflows"""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        
        try:
            endpoint = f"/workspaces/{self.workspace_id}/workflows"
            response = await self._make_request("GET", endpoint)
            return response.get("workflows", [])
        except Exception as e:
            print(f"Error listing workflows: {e}")
            return []
    
    async def get_workflow_stats(self) -> Dict:
        """Get workflow statistics"""
        try:
            workflows = await self.list_workflows(limit=1000)
            stats = {
                "total": len(workflows),
                "running": len([w for w in workflows if w.get("status") == "running"]),
                "completed": len([w for w in workflows if w.get("status") == "completed"]),
                "failed": len([w for w in workflows if w.get("status") == "failed"]),
                "pending": len([w for w in workflows if w.get("status") == "pending"])
            }
            return stats
        except Exception as e:
            print(f"Error getting workflow stats: {e}")
            return {"total": 0, "running": 0, "completed": 0, "failed": 0, "pending": 0}
    
    async def get_recent_workflows(self, limit: int = 10) -> List[Dict]:
        """Get recently executed workflows"""
        try:
            workflows = await self.list_workflows(limit=limit)
            # Sort by start time
            workflows.sort(key=lambda x: x.get("start_time", ""), reverse=True)
            return workflows[:limit]
        except Exception as e:
            print(f"Error getting recent workflows: {e}")
            return []
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow by ID"""
        try:
            endpoint = f"/workspaces/{self.workspace_id}/workflows/{workflow_id}"
            return await self._make_request("GET", endpoint)
        except Exception as e:
            print(f"Error getting workflow: {e}")
            return None
    
    async def create_workflow(
        self,
        name: str,
        description: Optional[str],
        agent_config: Dict[str, Any],
        workflow_steps: List[Dict[str, Any]],
        schedule: Optional[str] = None
    ) -> Dict:
        """Create a new workflow"""
        data = {
            "name": name,
            "description": description,
            "agent_config": agent_config,
            "workflow_steps": workflow_steps,
            "schedule": schedule,
            "created_at": datetime.utcnow().isoformat()
        }
        
        endpoint = f"/workspaces/{self.workspace_id}/workflows"
        return await self._make_request("POST", endpoint, data)
    
    async def update_workflow(self, workflow_id: str, **kwargs) -> Dict:
        """Update workflow"""
        endpoint = f"/workspaces/{self.workspace_id}/workflows/{workflow_id}"
        return await self._make_request("PUT", endpoint, kwargs)
    
    async def delete_workflow(self, workflow_id: str) -> None:
        """Delete workflow"""
        endpoint = f"/workspaces/{self.workspace_id}/workflows/{workflow_id}"
        await self._make_request("DELETE", endpoint)
    
    async def start_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict] = None,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """Start workflow execution"""
        data = {
            "workflow_id": workflow_id,
            "input_data": input_data or {},
            "parameters": parameters or {},
            "execution_id": str(uuid.uuid4()),
            "started_at": datetime.utcnow().isoformat()
        }
        
        endpoint = f"/workspaces/{self.workspace_id}/workflows/{workflow_id}/executions"
        return await self._make_request("POST", endpoint, data)
    
    async def stop_workflow(self, workflow_id: str) -> Dict:
        """Stop workflow execution"""
        endpoint = f"/workspaces/{self.workspace_id}/workflows/{workflow_id}/stop"
        return await self._make_request("POST", endpoint)
    
    async def get_workflow_executions(
        self,
        workflow_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """Get workflow execution history"""
        endpoint = f"/workspaces/{self.workspace_id}/workflows/{workflow_id}/executions"
        response = await self._make_request("GET", endpoint)
        return response.get("executions", [])
    
    async def get_execution_details(self, workflow_id: str, execution_id: str) -> Dict:
        """Get detailed execution information"""
        endpoint = f"/workspaces/{self.workspace_id}/workflows/{workflow_id}/executions/{execution_id}"
        return await self._make_request("GET", endpoint)
    
    async def get_execution_logs(self, workflow_id: str, execution_id: str) -> List[Dict]:
        """Get execution logs"""
        endpoint = f"/workspaces/{self.workspace_id}/workflows/{workflow_id}/executions/{execution_id}/logs"
        response = await self._make_request("GET", endpoint)
        return response.get("logs", [])
    
    async def kickoff_deployed_workflow(self, uploaded_file_url: str) -> Dict:
        """Start deployed workflow with PDF URL"""
        url = f"{self.deployed_workflow_url}/api/workflow/kickoff"
        data = {
            "inputs": {
                "uploaded_file_url": uploaded_file_url
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.deployed_headers, json=data) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"Failed to start workflow: {error}")
                result = await response.json()
                return {
                    "success": True,
                    "trace_id": result.get("trace_id"),
                    "message": "Workflow started successfully"
                }
    
    async def get_deployed_workflow_events(self, trace_id: str) -> Dict:
        """Get events from deployed workflow"""
        url = f"{self.deployed_workflow_url}/api/workflow/events"
        params = {"trace_id": trace_id}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"Authorization": f"Bearer {self.cdsw_api_key}", "Accept": "application/json"}, params=params) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"Failed to get workflow events: {error}")
                events = await response.json()
                return {
                    "success": True,
                    "trace_id": trace_id,
                    "events": events
                }
    
    async def submit_workflow(self, uploaded_file_url: str, query: str) -> Dict:
        """Submit workflow to files-to-relational Agent Studio application"""
        start_time = time.time()
        trace_id = None
        workflow_url = None
        
        pool = await self._get_pool()
        
        async with pool.acquire() as conn:
            try:
                # Get the files-to-relational workflow URL
                workflow_url = get_pdf_to_relational_workflow_url()
                if not workflow_url:
                    raise Exception("files-to-relational workflow application not found in Agent Studio")
                
                api_key = get_env_var("CDSW_APIV2_KEY")
                
                url = f"{workflow_url}/api/workflow/kickoff"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data = {
                    "inputs": {
                        "uploaded_file_url": uploaded_file_url,
                        "query": query
                    }
                }
                
                async with aiohttp.ClientSession() as http_session:
                    async with http_session.post(url, headers=headers, json=data) as response:
                        if response.status >= 400:
                            error_text = await response.text()
                            
                            # Save failed submission to database
                            submission_id = await conn.fetchval("""
                                INSERT INTO xtracticai.workflow_submissions 
                                (trace_id, workflow_url, uploaded_file_url, query, status, 
                                 workflow_id, workflow_name, error_message, submitted_at)
                                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                                RETURNING id
                            """, str(uuid.uuid4()), workflow_url, uploaded_file_url, query, 
                                "failed", "files-to-relational", "PDF to Relational", 
                                error_text, datetime.utcnow())
                            
                            raise Exception(f"Workflow submission failed: {error_text}")
                        
                        result = await response.json()
                        trace_id = result.get("trace_id")
                        
                        if not trace_id:
                            raise Exception("No trace_id returned from workflow submission")
                        
                        # Save successful submission to database
                        import json
                        submission_id = await conn.fetchval("""
                            INSERT INTO xtracticai.workflow_submissions 
                            (trace_id, workflow_url, uploaded_file_url, query, status, 
                             workflow_id, workflow_name, metadata, submitted_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                            RETURNING id
                        """, trace_id, workflow_url, uploaded_file_url, query, 
                            "submitted", "files-to-relational", "PDF to Relational", 
                            json.dumps({"response": result}), datetime.utcnow())
                        
                        submission = await conn.fetchrow("""
                            SELECT * FROM xtracticai.workflow_submissions WHERE id = $1
                        """, submission_id)
                        
                        return {
                            "success": True,
                            "trace_id": trace_id,
                            "submission_id": str(submission['id']),
                            "workflow_url": workflow_url,
                            "status": "submitted",
                            "submitted_at": submission['submitted_at'].isoformat(),
                            "message": "Workflow submitted successfully to files-to-relational"
                        }
            except Exception as e:
                # Attempt to save error to database
                try:
                    if trace_id:
                        await conn.execute("""
                            INSERT INTO xtracticai.workflow_submissions 
                            (trace_id, workflow_url, uploaded_file_url, query, status, 
                             workflow_id, workflow_name, error_message, submitted_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        """, trace_id, workflow_url or "unknown", uploaded_file_url, query, 
                            "failed", "files-to-relational", "PDF to Relational", 
                            str(e), datetime.utcnow())
                except:
                    pass  # If database save fails, just raise the original error
                
                raise Exception(f"Error submitting workflow: {str(e)}")
    
    async def get_workflow_submission_status(self, trace_id: str) -> Dict:
        """Get status of a submitted workflow by polling the events API"""
        pool = await self._get_pool()
        
        async with pool.acquire() as conn:
            try:
                # Get submission record from database
                submission = await conn.fetchrow("""
                    SELECT * FROM xtracticai.workflow_submissions 
                    WHERE trace_id = $1
                """, trace_id)
                
                if not submission:
                    raise Exception(f"No submission found with trace_id: {trace_id}")
                
                # If already completed or failed, return cached status without polling
                if submission['status'] in ["completed", "failed"]:
                    return {
                        "success": True,
                        "trace_id": trace_id,
                        "status": submission['status'],
                        "submitted_at": submission['submitted_at'].isoformat(),
                        "completed_at": submission['completed_at'].isoformat() if submission['completed_at'] else None,
                        "error_message": submission['error_message'],
                        "message": f"Workflow is {submission['status']}"
                    }
                
                # Only poll if status is not final
                workflow_url = submission['workflow_url']
                api_key = get_env_var("CDSW_APIV2_KEY")
                
                url = f"{workflow_url}/api/workflow/events"
                params = {"trace_id": trace_id}
                headers = {
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                async with aiohttp.ClientSession() as http_session:
                    async with http_session.get(url, headers=headers, params=params) as response:
                        if response.status >= 400:
                            # No response or error means workflow is completed
                            # Only update DB if status changed
                            await conn.execute("""
                                UPDATE xtracticai.workflow_submissions 
                                SET status = $1, completed_at = $2, last_polled_at = $3
                                WHERE trace_id = $4 AND status != 'completed'
                            """, "completed", datetime.utcnow(), datetime.utcnow(), trace_id)
                            
                            return {
                                "success": True,
                                "trace_id": trace_id,
                                "status": "completed",
                                "submitted_at": submission['submitted_at'].isoformat(),
                                "completed_at": datetime.utcnow().isoformat(),
                                "message": "Workflow completed successfully"
                            }
                        
                        # If we get events, workflow is still in progress
                        events = await response.json()
                        
                        # Only update if status changed or first poll
                        if submission['status'] != 'in-progress':
                            await conn.execute("""
                                UPDATE xtracticai.workflow_submissions 
                                SET status = $1, last_polled_at = $2
                                WHERE trace_id = $3
                            """, "in-progress", datetime.utcnow(), trace_id)
                        else:
                            # Just update last_polled_at without changing status
                            await conn.execute("""
                                UPDATE xtracticai.workflow_submissions 
                                SET last_polled_at = $1
                                WHERE trace_id = $2
                            """, datetime.utcnow(), trace_id)
                        
                        return {
                            "success": True,
                            "trace_id": trace_id,
                            "status": "in-progress",
                            "submitted_at": submission['submitted_at'].isoformat(),
                            "last_polled_at": datetime.utcnow().isoformat(),
                            "events_count": len(events) if isinstance(events, list) else 0,
                            "message": "Workflow is still in progress"
                        }
            except Exception as e:
                raise Exception(f"Error checking workflow status: {str(e)}")
