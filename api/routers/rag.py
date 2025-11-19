"""
RAG (Retrieval Augmented Generation) endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from services.rag_service import RAGService

router = APIRouter()


class DocumentIngest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    collection: str = "default"


class QueryRequest(BaseModel):
    query: str
    collection: Optional[str] = "default"
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = True


class ChatWithRAGRequest(BaseModel):
    question: str
    collection: Optional[str] = "default"
    context_size: int = 5
    conversation_id: Optional[str] = None


@router.post("/ingest")
async def ingest_document(document: DocumentIngest):
    """Ingest document into RAG database"""
    try:
        rag_service = RAGService()
        result = await rag_service.ingest_document(
            content=document.content,
            metadata=document.metadata,
            collection=document.collection
        )
        return {
            "success": True,
            "data": result,
            "message": "Document ingested successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    collection: str = "default",
    metadata: Optional[str] = None
):
    """Ingest file into RAG database"""
    try:
        rag_service = RAGService()
        result = await rag_service.ingest_file(
            file=file,
            collection=collection,
            metadata=metadata
        )
        return {
            "success": True,
            "data": result,
            "message": "File ingested successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/url")
async def ingest_url(url: str, collection: str = "default"):
    """Ingest content from URL into RAG database"""
    try:
        rag_service = RAGService()
        result = await rag_service.ingest_url(url=url, collection=collection)
        return {
            "success": True,
            "data": result,
            "message": "URL content ingested successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_rag(request: QueryRequest):
    """Query RAG database with semantic search"""
    try:
        rag_service = RAGService()
        results = await rag_service.query(
            query=request.query,
            collection=request.collection,
            top_k=request.top_k,
            filters=request.filters,
            include_metadata=request.include_metadata
        )
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_with_rag(request: ChatWithRAGRequest):
    """Chat with RAG-enhanced responses"""
    try:
        rag_service = RAGService()
        response = await rag_service.chat(
            question=request.question,
            collection=request.collection,
            context_size=request.context_size,
            conversation_id=request.conversation_id
        )
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections")
async def list_collections():
    """List all RAG collections"""
    try:
        rag_service = RAGService()
        collections = await rag_service.list_collections()
        return {
            "success": True,
            "data": collections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_name}/stats")
async def get_collection_stats(collection_name: str):
    """Get statistics for a collection"""
    try:
        rag_service = RAGService()
        stats = await rag_service.get_collection_stats(collection_name)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection"""
    try:
        rag_service = RAGService()
        await rag_service.delete_collection(collection_name)
        return {
            "success": True,
            "message": "Collection deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, collection: str = "default"):
    """Delete a document from collection"""
    try:
        rag_service = RAGService()
        await rag_service.delete_document(document_id, collection)
        return {
            "success": True,
            "message": "Document deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
