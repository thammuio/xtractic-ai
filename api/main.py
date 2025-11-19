"""
FastAPI main application for Xtractic AI
Integrates with Cloudera AI Agent Studio, MCP Servers, RAG, and Supabase
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uvicorn

from routers import workflows, datasets, ai, etl, mcp, rag
from core.config import settings
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting Xtractic AI API...")
    await init_db()
    yield
    # Shutdown
    print("Shutting down Xtractic AI API...")

app = FastAPI(
    title="Xtractic AI API",
    description="API for interacting with Cloudera AI Agent Studio, MCP Servers, RAG, and Supabase",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://xtracticai-cloudera.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(etl.router, prefix="/api/etl", tags=["ETL"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["MCP"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Xtractic AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
