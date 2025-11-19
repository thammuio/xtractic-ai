"""
Dataset Service for Supabase integration
"""
from typing import List, Dict, Any, Optional
import json

from core.database import get_supabase
from core.config import settings


class DatasetService:
    """Service for managing datasets in Supabase"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    async def list_datasets(self) -> List[Dict]:
        """List all available datasets (tables)"""
        try:
            # Query information schema to get all tables
            response = self.supabase.rpc(
                'get_tables_list',
                {}
            ).execute()
            
            # If the RPC doesn't exist, return a default list
            if not response.data:
                return [
                    {"name": "workflows", "row_count": 0, "size": "0 KB"},
                    {"name": "executions", "row_count": 0, "size": "0 KB"},
                    {"name": "documents", "row_count": 0, "size": "0 KB"}
                ]
            
            return response.data
        except Exception as e:
            print(f"Error listing datasets: {e}")
            # Return default tables
            return [
                {"name": "workflows", "description": "Workflow definitions"},
                {"name": "executions", "description": "Workflow execution history"},
                {"name": "documents", "description": "Ingested documents"}
            ]
    
    async def get_dataset(
        self,
        dataset_name: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[str] = None
    ) -> Dict:
        """Get dataset with pagination"""
        try:
            query = self.supabase.table(dataset_name).select("*")
            
            # Apply filters if provided
            if filters:
                filter_dict = json.loads(filters)
                for key, value in filter_dict.items():
                    query = query.eq(key, value)
            
            # Apply pagination
            query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            
            return {
                "data": response.data,
                "count": len(response.data),
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            raise Exception(f"Error fetching dataset: {e}")
    
    async def query_dataset(
        self,
        dataset_name: str,
        query: str,
        filters: Optional[Dict] = None
    ) -> Dict:
        """Query dataset with natural language (to be enhanced with AI)"""
        try:
            # For now, perform a basic text search
            # In production, this would use AI to interpret the query
            
            supabase_query = self.supabase.table(dataset_name).select("*")
            
            if filters:
                for key, value in filters.items():
                    supabase_query = supabase_query.eq(key, value)
            
            response = supabase_query.limit(100).execute()
            
            return {
                "query": query,
                "results": response.data,
                "count": len(response.data)
            }
        except Exception as e:
            raise Exception(f"Error querying dataset: {e}")
    
    async def get_dataset_stats(self, dataset_name: str) -> Dict:
        """Get dataset statistics"""
        try:
            # Get row count
            count_response = self.supabase.table(dataset_name).select("*", count="exact").execute()
            
            return {
                "table_name": dataset_name,
                "row_count": count_response.count if hasattr(count_response, 'count') else 0,
                "columns": []  # Would need schema introspection
            }
        except Exception as e:
            raise Exception(f"Error getting dataset stats: {e}")
    
    async def export_dataset(
        self,
        dataset_name: str,
        format: str = "csv",
        filters: Optional[str] = None
    ) -> List[Dict]:
        """Export dataset"""
        try:
            query = self.supabase.table(dataset_name).select("*")
            
            if filters:
                filter_dict = json.loads(filters)
                for key, value in filter_dict.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error exporting dataset: {e}")
    
    async def get_schema(self, dataset_name: str) -> Dict:
        """Get dataset schema"""
        try:
            # Query one row to get column names and types
            response = self.supabase.table(dataset_name).select("*").limit(1).execute()
            
            if response.data:
                sample = response.data[0]
                schema = {
                    "table_name": dataset_name,
                    "columns": [
                        {
                            "name": key,
                            "type": type(value).__name__
                        }
                        for key, value in sample.items()
                    ]
                }
                return schema
            
            return {"table_name": dataset_name, "columns": []}
        except Exception as e:
            raise Exception(f"Error getting schema: {e}")
