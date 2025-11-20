"""
FastAPI main application for Xtractic AI
Integrates with Cloudera AI Agent Studio, MCP Servers, RAG, and Supabase
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uvicorn
import os

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

def create_app():
    """Create and configure the FastAPI application"""
    CDSW_DOMAIN = os.getenv('CDSW_DOMAIN')
    
    app = FastAPI(
        title="Xtractic AI API",
        description="API for interacting with Cloudera AI Agent Studio, MCP Servers, RAG, and Supabase",
        version="1.0.0",
        lifespan=lifespan
    )

    # CORS middleware with Cloudera domain support
    cors_origins = [
        "*",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://xtracticai-cloudera.vercel.app",
        "*.cloudera.site",
    ]
    
    # Add CDSW domain origins if available
    if CDSW_DOMAIN:
        cors_origins.extend([
            f"https://xtracticai-api.{CDSW_DOMAIN}",
            f"https://xtracticai-ui.{CDSW_DOMAIN}",
            f"https://{CDSW_DOMAIN}",
            f"https://*.{CDSW_DOMAIN}",
            f"*.{CDSW_DOMAIN}",
            "https://xtracticai-cloudera.vercel.app",
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8000",
        ])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
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
    
    return app

# Create the app instance at module level for Cloudera Workbench
app = create_app()

if __name__ == "__main__":
    # Get configuration from environment variables
    # CDSW_APP_PORT is automatically set by Cloudera Workbench
    host = os.getenv('CDSW_APP_HOST', '127.0.0.1')
    port = int(os.getenv('CDSW_APP_PORT', 9000))
    
    print(f"Starting Xtractic AI API on {host}:{port}")
    print(f"Swagger UI: http://{host}:{port}/docs")
    print(f"ReDoc: http://{host}:{port}/redoc")
    
    # Run uvicorn server
    # For Cloudera Workbench, this will keep the application running
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False
    )
