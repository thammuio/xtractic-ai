"""
FastAPI main application for Xtractic AI
Integrates with Cloudera AI Agent Studio, MCP Servers, RAG, and Supabase
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import threading
import uvicorn
import os

from api.routers import workflows, datasets, ai, etl, mcp, rag
from api.core.config import settings


def create_app():
    """Create and configure the FastAPI application"""
    CDSW_DOMAIN = os.getenv('CDSW_DOMAIN')
    
    app = FastAPI()

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

def run_server(app, host="127.0.0.1", port=None, log_level="warning", reload=False):
    if port is None:
        port = int(os.getenv('CDSW_APP_PORT', 9000))  # Default to 8080 if API_PORT is not set
    uvicorn.run(app, host=host, port=port, log_level=log_level, reload=reload)

def main():
    app = create_app()
    server_thread = threading.Thread(target=run_server, args=(app,))
    server_thread.start()

if __name__ == "__main__":
    main()