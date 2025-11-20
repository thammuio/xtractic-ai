"""
AI Service for chat and insights
"""
from typing import Dict, Any, Optional, List
import openai
from datetime import datetime
import uuid

from api.api.core.config import settings
from api.core.database import get_supabase


class AIService:
    """Service for AI-powered features"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        self.supabase = get_supabase()
    
    async def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
        stream: bool = False
    ) -> Dict:
        """Chat with AI assistant"""
        try:
            # Get or create conversation
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Get conversation history
            history = await self._get_conversation_history(conversation_id)
            
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant for Xtractic AI, helping users with data workflows, ETL processes, and data analysis."
                }
            ]
            
            # Add history
            messages.extend(history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Add context if provided
            if context:
                messages[-1]["content"] += f"\n\nContext: {context}"
            
            # Call OpenAI
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            assistant_message = response.choices[0].message.content
            
            # Store conversation
            await self._store_message(conversation_id, "user", message)
            await self._store_message(conversation_id, "assistant", assistant_message)
            
            return {
                "conversation_id": conversation_id,
                "message": assistant_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error in chat: {e}")
    
    async def generate_insights(
        self,
        dataset: str,
        columns: Optional[List[str]] = None,
        analysis_type: str = "comprehensive"
    ) -> Dict:
        """Generate insights from dataset"""
        try:
            # Fetch sample data from dataset
            from .dataset_service import DatasetService
            dataset_service = DatasetService()
            
            data = await dataset_service.get_dataset(dataset, limit=100)
            
            # Create prompt for insights
            prompt = f"""
            Analyze the following dataset and provide {analysis_type} insights:
            
            Dataset: {dataset}
            Sample data (first 10 rows): {data['data'][:10]}
            
            Please provide:
            1. Key patterns and trends
            2. Data quality observations
            3. Potential anomalies
            4. Recommendations for further analysis
            """
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analyst expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights = response.choices[0].message.content
            
            return {
                "dataset": dataset,
                "analysis_type": analysis_type,
                "insights": insights,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error generating insights: {e}")
    
    async def generate_query(
        self,
        natural_language: str,
        schema: Optional[Dict[str, Any]] = None,
        target_db: str = "postgresql"
    ) -> Dict:
        """Generate database query from natural language"""
        try:
            prompt = f"""
            Convert the following natural language query to a {target_db} SQL query:
            
            Query: {natural_language}
            
            {"Schema: " + str(schema) if schema else ""}
            
            Provide only the SQL query, no explanation.
            """
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert {target_db} SQL developer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            return {
                "natural_language": natural_language,
                "sql_query": sql_query,
                "target_database": target_db,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error generating query: {e}")
    
    async def _get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history from database"""
        try:
            response = self.supabase.table("conversations").select("*").eq(
                "conversation_id", conversation_id
            ).order("created_at").execute()
            
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in response.data
            ]
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    async def _store_message(self, conversation_id: str, role: str, content: str):
        """Store message in database"""
        try:
            self.supabase.table("conversations").insert({
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error storing message: {e}")
    
    async def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get full conversation"""
        try:
            response = self.supabase.table("conversations").select("*").eq(
                "conversation_id", conversation_id
            ).order("created_at").execute()
            
            return response.data
        except Exception as e:
            raise Exception(f"Error getting conversation: {e}")
    
    async def delete_conversation(self, conversation_id: str):
        """Delete conversation"""
        try:
            self.supabase.table("conversations").delete().eq(
                "conversation_id", conversation_id
            ).execute()
        except Exception as e:
            raise Exception(f"Error deleting conversation: {e}")
