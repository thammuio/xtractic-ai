"""
AI and chat endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from api.services.ai_service import AIService

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None
    stream: bool = False


class InsightsRequest(BaseModel):
    dataset: str
    columns: Optional[List[str]] = None
    analysis_type: Optional[str] = "comprehensive"  # comprehensive, statistical, trends


class QueryGenerationRequest(BaseModel):
    query: str
    database_schema: Optional[Dict[str, Any]] = None
    target_database: str = "postgresql"  # postgresql, mysql, mongodb


@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat with AI assistant"""
    try:
        ai_service = AIService()
        response = await ai_service.chat(
            message=request.message,
            context=request.context,
            conversation_id=request.conversation_id,
            stream=request.stream
        )
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights")
async def get_insights(request: InsightsRequest):
    """Generate insights from dataset"""
    try:
        ai_service = AIService()
        insights = await ai_service.generate_insights(
            dataset=request.dataset,
            columns=request.columns,
            analysis_type=request.analysis_type
        )
        return {
            "success": True,
            "data": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-query")
async def generate_query(request: QueryGenerationRequest):
    """Generate database query from natural language"""
    try:
        ai_service = AIService()
        query = await ai_service.generate_query(
            natural_language=request.query,
            schema=request.database_schema,
            target_db=request.target_database
        )
        return {
            "success": True,
            "data": query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    try:
        ai_service = AIService()
        conversation = await ai_service.get_conversation(conversation_id)
        return {
            "success": True,
            "data": conversation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation history"""
    try:
        ai_service = AIService()
        await ai_service.delete_conversation(conversation_id)
        return {
            "success": True,
            "message": "Conversation deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
