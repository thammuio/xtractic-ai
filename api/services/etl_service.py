"""
ETL Service for data processing jobs
"""
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import asyncio

from core.database import get_supabase
from core.config import settings


class ETLService:
    """Service for ETL job management"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    async def run_etl(
        self,
        job_name: str,
        source_type: str,
        source_config: Dict[str, Any],
        destination_type: str,
        destination_config: Dict[str, Any],
        transformations: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Run ETL job"""
        try:
            job_id = str(uuid.uuid4())
            
            # Create job record
            job_data = {
                "job_id": job_id,
                "job_name": job_name,
                "source_type": source_type,
                "source_config": source_config,
                "destination_type": destination_type,
                "destination_config": destination_config,
                "transformations": transformations or [],
                "status": "running",
                "created_at": datetime.utcnow().isoformat(),
                "started_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("etl_jobs").insert(job_data).execute()
            
            # Start ETL process in background
            asyncio.create_task(self._execute_etl(job_id, job_data))
            
            return job_id
        except Exception as e:
            raise Exception(f"Error starting ETL job: {e}")
    
    async def _execute_etl(self, job_id: str, job_config: Dict):
        """Execute ETL job (background task)"""
        try:
            # Extract
            await self._log_job(job_id, "info", "Starting extraction...")
            extracted_data = await self._extract_data(
                job_config["source_type"],
                job_config["source_config"]
            )
            
            # Transform
            await self._log_job(job_id, "info", "Starting transformation...")
            transformed_data = await self._transform_data(
                extracted_data,
                job_config["transformations"]
            )
            
            # Load
            await self._log_job(job_id, "info", "Starting loading...")
            await self._load_data(
                transformed_data,
                job_config["destination_type"],
                job_config["destination_config"]
            )
            
            # Update job status
            self.supabase.table("etl_jobs").update({
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "records_processed": len(transformed_data)
            }).eq("job_id", job_id).execute()
            
            await self._log_job(job_id, "info", "ETL job completed successfully")
            
        except Exception as e:
            # Update job status to failed
            self.supabase.table("etl_jobs").update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            }).eq("job_id", job_id).execute()
            
            await self._log_job(job_id, "error", f"ETL job failed: {e}")
    
    async def _extract_data(self, source_type: str, config: Dict) -> List[Dict]:
        """Extract data from source"""
        if source_type == "supabase":
            response = self.supabase.table(config["table"]).select("*").execute()
            return response.data
        elif source_type == "csv":
            # Handle CSV extraction
            pass
        elif source_type == "api":
            # Handle API extraction
            pass
        
        return []
    
    async def _transform_data(self, data: List[Dict], transformations: List[Dict]) -> List[Dict]:
        """Apply transformations to data"""
        transformed = data
        
        for transform in transformations:
            transform_type = transform.get("type")
            
            if transform_type == "filter":
                # Apply filter
                field = transform["field"]
                value = transform["value"]
                transformed = [row for row in transformed if row.get(field) == value]
            
            elif transform_type == "map":
                # Apply mapping
                source_field = transform["source"]
                target_field = transform["target"]
                transformed = [
                    {**row, target_field: row.get(source_field)}
                    for row in transformed
                ]
        
        return transformed
    
    async def _load_data(self, data: List[Dict], destination_type: str, config: Dict):
        """Load data to destination"""
        if destination_type == "supabase":
            # Batch insert to Supabase
            table = config["table"]
            batch_size = 100
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                self.supabase.table(table).insert(batch).execute()
        
        elif destination_type == "rag_db":
            # Load to RAG database
            pass
    
    async def _log_job(self, job_id: str, level: str, message: str):
        """Log job message"""
        try:
            self.supabase.table("etl_job_logs").insert({
                "job_id": job_id,
                "level": level,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error logging job message: {e}")
    
    async def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """List ETL jobs"""
        try:
            query = self.supabase.table("etl_jobs").select("*")
            
            if status:
                query = query.eq("status", status)
            
            response = query.order("created_at", desc=True).range(
                offset, offset + limit - 1
            ).execute()
            
            return response.data
        except Exception as e:
            raise Exception(f"Error listing jobs: {e}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status"""
        try:
            response = self.supabase.table("etl_jobs").select("*").eq(
                "job_id", job_id
            ).execute()
            
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            raise Exception(f"Error getting job status: {e}")
    
    async def get_job_logs(self, job_id: str, limit: int = 100) -> List[Dict]:
        """Get job logs"""
        try:
            response = self.supabase.table("etl_job_logs").select("*").eq(
                "job_id", job_id
            ).order("timestamp").limit(limit).execute()
            
            return response.data
        except Exception as e:
            raise Exception(f"Error getting job logs: {e}")
    
    async def cancel_job(self, job_id: str) -> Dict:
        """Cancel running job"""
        try:
            self.supabase.table("etl_jobs").update({
                "status": "cancelled",
                "completed_at": datetime.utcnow().isoformat()
            }).eq("job_id", job_id).execute()
            
            await self._log_job(job_id, "info", "Job cancelled by user")
            
            return {"message": "Job cancelled successfully"}
        except Exception as e:
            raise Exception(f"Error cancelling job: {e}")
    
    async def process_upload(self, file, destination: str) -> Dict:
        """Process uploaded file"""
        try:
            # Generate job for file processing
            job_id = await self.run_etl(
                job_name=f"Upload: {file.filename}",
                source_type="upload",
                source_config={"filename": file.filename},
                destination_type=destination,
                destination_config={"table": "uploaded_files"}
            )
            
            return {
                "job_id": job_id,
                "filename": file.filename
            }
        except Exception as e:
            raise Exception(f"Error processing upload: {e}")
    
    async def delete_job(self, job_id: str):
        """Delete ETL job"""
        try:
            # Delete logs first
            self.supabase.table("etl_job_logs").delete().eq("job_id", job_id).execute()
            
            # Delete job
            self.supabase.table("etl_jobs").delete().eq("job_id", job_id).execute()
        except Exception as e:
            raise Exception(f"Error deleting job: {e}")
