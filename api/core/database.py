"""
Database connection management for Supabase and PostgreSQL
"""
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from api.core.config import settings
import asyncpg

Base = declarative_base()

# Supabase client
supabase_client: Client = None

# PostgreSQL async engine for RAG database
rag_engine = None
AsyncSessionLocal = None


async def init_db():
    """Initialize database connections"""
    global supabase_client, rag_engine, AsyncSessionLocal
    
    # Initialize Supabase
    if settings.SUPABASE_URL and settings.SUPABASE_KEY and not settings.SUPABASE_URL.startswith("your_"):
        try:
            supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            print("✓ Supabase client initialized")
        except Exception as e:
            print(f"⚠ Supabase initialization skipped: {e}")
    else:
        print("⚠ Supabase credentials not configured - skipping initialization")
    
    # Initialize RAG database connection
    if settings.RAG_DB_HOST and settings.RAG_DB_HOST != "localhost":
        try:
            db_url = f"postgresql+asyncpg://{settings.RAG_DB_USER}:{settings.RAG_DB_PASSWORD}@{settings.RAG_DB_HOST}:{settings.RAG_DB_PORT}/{settings.RAG_DB_NAME}"
            rag_engine = create_async_engine(db_url, echo=settings.DEBUG)
            AsyncSessionLocal = sessionmaker(
                rag_engine, class_=AsyncSession, expire_on_commit=False
            )
            print("✓ RAG database connection initialized")
        except Exception as e:
            print(f"⚠ RAG database initialization skipped: {e}")
    else:
        print("⚠ RAG database not configured - skipping initialization")


def get_supabase() -> Client:
    """Get Supabase client instance"""
    if supabase_client is None:
        raise Exception("Supabase client not initialized")
    return supabase_client


async def get_rag_session() -> AsyncSession:
    """Get RAG database session"""
    if AsyncSessionLocal is None:
        raise Exception("RAG database not initialized")
    async with AsyncSessionLocal() as session:
        yield session
