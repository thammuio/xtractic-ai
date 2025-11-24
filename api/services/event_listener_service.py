"""
Event Listener Service - Background polling for workflow events
Listens for trace_id events and captures crew_kickoff_completed state
"""
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from api.core.database import get_db_pool
from api.utils.cloudera_utils import get_env_var

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventListenerService:
    """Service for listening to workflow events in the background"""
    
    def __init__(self):
        self.active_listeners: Dict[str, asyncio.Task] = {}
        self.poll_interval = 1  # Poll every 1 second
        self.max_poll_duration = 600  # Maximum 10 minutes (600 seconds) of polling
    
    async def _get_pool(self):
        """Get shared connection pool"""
        return await get_db_pool()
    
    async def start_listening(self, trace_id: str, workflow_url: str) -> Dict[str, Any]:
        """Start background event listener for a trace_id
        
        Args:
            trace_id: The trace ID to listen for
            workflow_url: The workflow application URL
            
        Returns:
            Dictionary with listener status
        """
        # Check if already listening for this trace_id
        if trace_id in self.active_listeners:
            task = self.active_listeners[trace_id]
            if not task.done():
                return {
                    "success": True,
                    "message": f"Already listening for trace_id: {trace_id}",
                    "trace_id": trace_id
                }
        
        # Start new background task
        task = asyncio.create_task(self._poll_events(trace_id, workflow_url))
        self.active_listeners[trace_id] = task
        
        logger.info(f"Started event listener for trace_id: {trace_id}")
        
        return {
            "success": True,
            "message": f"Started listening for events on trace_id: {trace_id}",
            "trace_id": trace_id
        }
    
    async def _poll_events(self, trace_id: str, workflow_url: str):
        """Background polling loop for workflow events
        
        Continuously polls the events API until:
        - crew_kickoff_completed event is received
        - Maximum polling duration is reached
        - Error occurs that indicates completion
        
        Args:
            trace_id: The trace ID to poll
            workflow_url: The workflow application URL
        """
        pool = await self._get_pool()
        api_key = get_env_var("CDSW_APIV2_KEY")
        
        url = f"{workflow_url}/api/workflow/events"
        params = {"trace_id": trace_id}
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        start_time = asyncio.get_event_loop().time()
        poll_count = 0
        
        try:
            async with pool.acquire() as conn:
                while True:
                    poll_count += 1
                    elapsed_time = asyncio.get_event_loop().time() - start_time
                    
                    # Check if we've exceeded max polling duration
                    if elapsed_time > self.max_poll_duration:
                        logger.warning(f"Max polling duration reached for trace_id: {trace_id}")
                        await self._mark_workflow_timeout(conn, trace_id)
                        break
                    
                    try:
                        # Update last polled timestamp
                        await conn.execute("""
                            UPDATE xtracticai.workflow_submissions 
                            SET last_polled_at = $1
                            WHERE trace_id = $2
                        """, datetime.utcnow(), trace_id)
                        
                        # Poll the events API
                        async with aiohttp.ClientSession() as http_session:
                            async with http_session.get(url, headers=headers, params=params) as response:
                                if response.status >= 400:
                                    # Error response - workflow likely completed
                                    logger.info(f"Events API returned error {response.status} for trace_id: {trace_id} - marking as completed")
                                    await self._mark_workflow_completed(conn, trace_id, None)
                                    break
                                
                                events = await response.json()
                                
                                # Check if events is a list
                                if not isinstance(events, list):
                                    logger.warning(f"Unexpected events format for trace_id: {trace_id}")
                                    continue
                                
                                # Look for crew_kickoff_completed event
                                for event in events:
                                    if isinstance(event, dict) and event.get("type") == "crew_kickoff_completed":
                                        output = event.get("output", "")
                                        logger.info(f"Found crew_kickoff_completed event for trace_id: {trace_id}")
                                        
                                        # Update workflow with completion data
                                        await self._mark_workflow_completed(conn, trace_id, output)
                                        
                                        # Exit polling loop
                                        return
                                
                                # Update status to in-progress if still getting events
                                await conn.execute("""
                                    UPDATE xtracticai.workflow_submissions 
                                    SET status = $1
                                    WHERE trace_id = $2 AND status NOT IN ('completed', 'failed')
                                """, "in-progress", trace_id)
                                
                    except aiohttp.ClientError as e:
                        logger.error(f"HTTP error polling events for trace_id {trace_id}: {str(e)}")
                        # Don't break - continue polling
                    except Exception as e:
                        logger.error(f"Error polling events for trace_id {trace_id}: {str(e)}")
                        # Don't break - continue polling
                    
                    # Wait before next poll
                    await asyncio.sleep(self.poll_interval)
                    
        except Exception as e:
            logger.error(f"Fatal error in event listener for trace_id {trace_id}: {str(e)}")
            async with pool.acquire() as conn:
                await self._mark_workflow_failed(conn, trace_id, str(e))
        finally:
            # Clean up listener from active list
            if trace_id in self.active_listeners:
                del self.active_listeners[trace_id]
            logger.info(f"Stopped event listener for trace_id: {trace_id} after {poll_count} polls")
    
    async def _mark_workflow_completed(self, conn, trace_id: str, output: Optional[str]):
        """Mark workflow as completed with output
        
        Args:
            conn: Database connection
            trace_id: The trace ID
            output: The workflow output from crew_kickoff_completed event
        """
        try:
            await conn.execute("""
                UPDATE xtracticai.workflow_submissions 
                SET status = $1, 
                    completed_at = $2,
                    wf_output = $3,
                    crew_kickoff_completed = TRUE,
                    last_polled_at = $2
                WHERE trace_id = $4
            """, "completed", datetime.utcnow(), output, trace_id)
            
            logger.info(f"Marked workflow {trace_id} as completed")
        except Exception as e:
            logger.error(f"Error marking workflow as completed: {str(e)}")
    
    async def _mark_workflow_failed(self, conn, trace_id: str, error_message: str):
        """Mark workflow as failed
        
        Args:
            conn: Database connection
            trace_id: The trace ID
            error_message: Error description
        """
        try:
            await conn.execute("""
                UPDATE xtracticai.workflow_submissions 
                SET status = $1,
                    error_message = $2,
                    completed_at = $3,
                    last_polled_at = $3
                WHERE trace_id = $4
            """, "failed", error_message, datetime.utcnow(), trace_id)
            
            logger.info(f"Marked workflow {trace_id} as failed")
        except Exception as e:
            logger.error(f"Error marking workflow as failed: {str(e)}")
    
    async def _mark_workflow_timeout(self, conn, trace_id: str):
        """Mark workflow as timed out
        
        Args:
            conn: Database connection
            trace_id: The trace ID
        """
        try:
            await conn.execute("""
                UPDATE xtracticai.workflow_submissions 
                SET status = $1,
                    error_message = $2,
                    completed_at = $3,
                    last_polled_at = $3
                WHERE trace_id = $4 AND status NOT IN ('completed', 'failed')
            """, "failed", "Polling timeout exceeded", datetime.utcnow(), trace_id)
            
            logger.info(f"Marked workflow {trace_id} as timed out")
        except Exception as e:
            logger.error(f"Error marking workflow as timed out: {str(e)}")
    
    def get_listener_status(self, trace_id: str) -> Dict[str, Any]:
        """Get status of event listener for a trace_id
        
        Args:
            trace_id: The trace ID to check
            
        Returns:
            Dictionary with listener status
        """
        if trace_id not in self.active_listeners:
            return {
                "trace_id": trace_id,
                "listening": False,
                "message": "No active listener for this trace_id"
            }
        
        task = self.active_listeners[trace_id]
        return {
            "trace_id": trace_id,
            "listening": not task.done(),
            "message": "Listener is active" if not task.done() else "Listener completed"
        }
    
    def stop_listening(self, trace_id: str) -> Dict[str, Any]:
        """Stop listening for a specific trace_id
        
        Args:
            trace_id: The trace ID to stop listening for
            
        Returns:
            Dictionary with stop status
        """
        if trace_id not in self.active_listeners:
            return {
                "success": False,
                "message": f"No active listener found for trace_id: {trace_id}"
            }
        
        task = self.active_listeners[trace_id]
        if not task.done():
            task.cancel()
        
        del self.active_listeners[trace_id]
        logger.info(f"Stopped event listener for trace_id: {trace_id}")
        
        return {
            "success": True,
            "message": f"Stopped listening for trace_id: {trace_id}"
        }
    
    async def stop_all_listeners(self):
        """Stop all active listeners"""
        for trace_id, task in list(self.active_listeners.items()):
            if not task.done():
                task.cancel()
        
        self.active_listeners.clear()
        logger.info("Stopped all event listeners")


# Singleton instance
event_listener_service = EventListenerService()
