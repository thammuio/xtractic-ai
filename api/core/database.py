"""
Database connection pool management
"""
import asyncpg
from typing import Optional
from api.core.config import settings


class DatabasePool:
    """Singleton database connection pool manager"""
    
    _instance: Optional['DatabasePool'] = None
    _pool: Optional[asyncpg.Pool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_pool(self) -> asyncpg.Pool:
        """Get or create the connection pool with size limits"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                settings.BACKEND_DATABASE_URL,
                min_size=2,  # Minimum connections to maintain
                max_size=10,  # Maximum connections allowed
                max_queries=50000,  # Recycle connection after this many queries
                max_inactive_connection_lifetime=300.0,  # Close idle connections after 5 minutes
                command_timeout=60.0  # Query timeout
            )
        return self._pool
    
    async def close(self):
        """Close the connection pool"""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None


# Global pool instance
db_pool = DatabasePool()


async def get_db_pool() -> asyncpg.Pool:
    """Dependency function to get database pool"""
    return await db_pool.get_pool()
