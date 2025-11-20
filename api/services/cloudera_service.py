"""
Cloudera AI Agent Studio Service
Manages workflows and agent interactions with Cloudera platform
"""
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import time

from api.core.config import settings
from api.utils.cloudera_utils import (
    get_cloudera_credentials,
    get_workflow_endpoint,
    get_cloudera_headers,
    get_workflow_application_url,
    get_pdf_to_relational_workflow_url,
    get_env_var
)
from api.services.stats_service import StatsService


class ClouderaService:
    """Service for interacting with Cloudera AI Agent Studio"""
    
    def __init__(self):
        self.api_url = settings.CLOUDERA_API_URL
        self.api_key = settings.CLOUDERA_API_KEY
        self.workspace_id = settings.CLOUDERA_WORKSPACE_ID
        
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
        """Submit workflow to pdf-to-relational Agent Studio application"""
        stats_service = StatsService()
        start_time = time.time()
        execution_id = None
        file_id = None
        
        try:
            await stats_service.init_schema()
            
            # Track agent
            await stats_service.track_agent(
                agent_name="pdf-to-relational",
                agent_type="workflow",
                status="running"
            )
            
            # Track file upload
            file_name = uploaded_file_url.split('/')[-1] if '/' in uploaded_file_url else uploaded_file_url
            file_id = await stats_service.track_file_upload(
                file_name=file_name,
                file_type="pdf",
                file_size_bytes=0,
                workflow_id="pdf-to-relational",
                workflow_name="PDF to Relational"
            )
            
            # Track workflow execution
            execution_id = await stats_service.track_workflow_execution(
                workflow_id="pdf-to-relational",
                workflow_name="PDF to Relational",
                execution_type="manual",
                agents_used=["pdf-to-relational"],
                tools_used=["pdf_processor"]
            )
            
            # Get the pdf-to-relational workflow URL
            workflow_url = get_pdf_to_relational_workflow_url()
            if not workflow_url:
                raise Exception("pdf-to-relational workflow application not found in Agent Studio")
            
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        duration_ms = (time.time() - start_time) * 1000
                        
                        # Update stats for failure
                        await stats_service.update_agent_execution("pdf-to-relational", False)
                        if file_id:
                            await stats_service.update_file_processing(
                                file_id, "failed", error_message=error_text, duration_ms=duration_ms
                            )
                        if execution_id:
                            await stats_service.update_workflow_execution(
                                execution_id, "failed", error_message=error_text, duration_ms=duration_ms
                            )
                        
                        raise Exception(f"Workflow submission failed: {error_text}")
                    
                    result = await response.json()
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Update stats for success
                    await stats_service.update_agent_execution("pdf-to-relational", True)
                    if file_id:
                        await stats_service.update_file_processing(
                            file_id, "completed", duration_ms=duration_ms
                        )
                    if execution_id:
                        await stats_service.update_workflow_execution(
                            execution_id,
                            "success",
                            input_files_count=1,
                            duration_ms=duration_ms,
                            metadata={"workflow_url": workflow_url}
                        )
                    
                    return {
                        "success": True,
                        "data": result,
                        "workflow_url": workflow_url,
                        "execution_id": execution_id,
                        "file_id": file_id,
                        "message": "Workflow submitted successfully to pdf-to-relational"
                    }
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Update stats for error
            if execution_id:
                await stats_service.update_workflow_execution(
                    execution_id, "failed", error_message=str(e), duration_ms=duration_ms
                )
            
            raise Exception(f"Error submitting workflow: {str(e)}")
        finally:
            await stats_service.close()
