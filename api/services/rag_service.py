"""
RAG (Retrieval Augmented Generation) Service
"""
from typing import Dict, Any, Optional, List
import openai
from datetime import datetime
import uuid
import PyPDF2
import io

from api.api.core.config import settings
from api.core.database import get_rag_session


class RAGService:
    """Service for RAG operations"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.embedding_model = settings.EMBEDDING_MODEL
        self.llm_model = settings.LLM_MODEL
    
    async def ingest_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection: str = "default"
    ) -> Dict:
        """Ingest document into RAG database"""
        try:
            document_id = str(uuid.uuid4())
            
            # Generate embeddings
            embedding = await self._generate_embedding(content)
            
            # Store in vector database
            # This is a placeholder - actual implementation depends on vector DB
            await self._store_vector(
                document_id=document_id,
                content=content,
                embedding=embedding,
                metadata=metadata or {},
                collection=collection
            )
            
            return {
                "document_id": document_id,
                "collection": collection,
                "status": "ingested",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error ingesting document: {e}")
    
    async def ingest_file(
        self,
        file,
        collection: str = "default",
        metadata: Optional[str] = None
    ) -> Dict:
        """Ingest file into RAG database"""
        try:
            # Extract text based on file type
            content = ""
            
            if file.filename.endswith('.pdf'):
                content = await self._extract_pdf_text(file)
            elif file.filename.endswith('.txt'):
                content = (await file.read()).decode('utf-8')
            else:
                raise Exception("Unsupported file type")
            
            # Parse metadata if provided
            meta = {}
            if metadata:
                import json
                meta = json.loads(metadata)
            
            meta["filename"] = file.filename
            
            return await self.ingest_document(content, meta, collection)
        except Exception as e:
            raise Exception(f"Error ingesting file: {e}")
    
    async def ingest_url(self, url: str, collection: str = "default") -> Dict:
        """Ingest content from URL"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    content = await response.text()
            
            metadata = {"source": url, "type": "url"}
            
            return await self.ingest_document(content, metadata, collection)
        except Exception as e:
            raise Exception(f"Error ingesting URL: {e}")
    
    async def query(
        self,
        query: str,
        collection: Optional[str] = "default",
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """Query RAG database with semantic search"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search vector database
            results = await self._vector_search(
                query_embedding=query_embedding,
                collection=collection,
                top_k=top_k,
                filters=filters
            )
            
            # Format results
            formatted_results = []
            for result in results:
                item = {
                    "content": result["content"],
                    "score": result["score"]
                }
                if include_metadata:
                    item["metadata"] = result.get("metadata", {})
                
                formatted_results.append(item)
            
            return formatted_results
        except Exception as e:
            raise Exception(f"Error querying RAG: {e}")
    
    async def chat(
        self,
        question: str,
        collection: Optional[str] = "default",
        context_size: int = 5,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """Chat with RAG-enhanced responses"""
        try:
            # Get relevant context from RAG
            context_results = await self.query(
                query=question,
                collection=collection,
                top_k=context_size
            )
            
            # Build context string
            context = "\n\n".join([
                f"[Context {i+1}]\n{result['content']}"
                for i, result in enumerate(context_results)
            ])
            
            # Generate response with context
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use the provided context to answer questions accurately."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ]
            
            response = openai.chat.completions.create(
                model=self.llm_model,
                messages=messages
            )
            
            answer = response.choices[0].message.content
            
            return {
                "question": question,
                "answer": answer,
                "context": context_results,
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error in RAG chat: {e}")
    
    async def list_collections(self) -> List[Dict]:
        """List all RAG collections"""
        try:
            # This is a placeholder - actual implementation depends on vector DB
            return [
                {"name": "default", "document_count": 0},
                {"name": "technical_docs", "document_count": 0},
                {"name": "business_docs", "document_count": 0}
            ]
        except Exception as e:
            raise Exception(f"Error listing collections: {e}")
    
    async def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics for a collection"""
        try:
            return {
                "collection": collection_name,
                "document_count": 0,
                "total_size": "0 MB",
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error getting collection stats: {e}")
    
    async def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            # Placeholder for deletion logic
            pass
        except Exception as e:
            raise Exception(f"Error deleting collection: {e}")
    
    async def delete_document(self, document_id: str, collection: str = "default"):
        """Delete a document from collection"""
        try:
            # Placeholder for deletion logic
            pass
        except Exception as e:
            raise Exception(f"Error deleting document: {e}")
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {e}")
    
    async def _store_vector(
        self,
        document_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict,
        collection: str
    ):
        """Store vector in database"""
        # Placeholder - implement based on chosen vector DB
        # For pgvector, use PostgreSQL with vector extension
        # For Pinecone/Weaviate, use their respective APIs
        pass
    
    async def _vector_search(
        self,
        query_embedding: List[float],
        collection: str,
        top_k: int,
        filters: Optional[Dict]
    ) -> List[Dict]:
        """Search vector database"""
        # Placeholder - implement based on chosen vector DB
        return []
    
    async def _extract_pdf_text(self, file) -> str:
        """Extract text from PDF file"""
        try:
            content = await file.read()
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return text
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {e}")
