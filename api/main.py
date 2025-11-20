"""
FastAPI main application for Xtractic AI
Integrates with Cloudera AI Agent Studio, MCP Servers, RAG, and Supabase
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import threading
import uvicorn
import os

from api.routers import workflows, datasets, ai, etl, mcp, rag, stats
from api.core.config import settings


def create_app():
    CDSW_DOMAIN = os.getenv('CDSW_DOMAIN')
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*",
            f"https://xtracticai-api.{CDSW_DOMAIN}",
            f"https://xtracticai-ui.{CDSW_DOMAIN}",
            f"https://{CDSW_DOMAIN}",
            f"https://*.{CDSW_DOMAIN}",
            f"*.{CDSW_DOMAIN}",
            "*.cloudera.site",
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Include routers
    app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
    app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])

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