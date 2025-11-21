#!/usr/bin/env python3
"""
Script to check and manage PostgreSQL database connections
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


async def check_db_connections():
    """Check current database connections and settings"""
    db_url = os.getenv("BACKEND_DATABASE_URL")
    
    if not db_url:
        print("❌ BACKEND_DATABASE_URL not set in environment")
        return
    
    try:
        # Create a single connection to check settings
        conn = await asyncpg.connect(db_url)
        
        # Check max_connections setting
        max_conn = await conn.fetchval("SHOW max_connections")
        print(f"✓ Database max_connections: {max_conn}")
        
        # Check current connections
        current_conns = await conn.fetch("""
            SELECT 
                datname,
                usename,
                application_name,
                state,
                COUNT(*) as connection_count
            FROM pg_stat_activity
            WHERE datname IS NOT NULL
            GROUP BY datname, usename, application_name, state
            ORDER BY connection_count DESC
        """)
        
        print(f"\n📊 Current connections by database/user/app:")
        total = 0
        for row in current_conns:
            count = row['connection_count']
            total += count
            print(f"  - {row['datname']}/{row['usename']}/{row['application_name'] or 'N/A'} ({row['state']}): {count}")
        
        print(f"\n📈 Total active connections: {total}/{max_conn}")
        
        # Check for idle connections
        idle_conns = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM pg_stat_activity 
            WHERE state = 'idle' 
            AND datname IS NOT NULL
        """)
        print(f"⏸  Idle connections: {idle_conns}")
        
        # Check for reserved superuser connections
        superuser_reserved = await conn.fetchval("SHOW superuser_reserved_connections")
        print(f"🔒 Superuser reserved connections: {superuser_reserved}")
        
        available = int(max_conn) - int(superuser_reserved) - total
        print(f"\n✅ Available connections: {available}")
        
        if available < 5:
            print(f"⚠️  WARNING: Only {available} connections available!")
            print("   Consider:")
            print("   1. Closing idle connections")
            print("   2. Reducing connection pool size")
            print("   3. Increasing max_connections in PostgreSQL")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")


async def kill_idle_connections():
    """Kill idle connections (use with caution!)"""
    db_url = os.getenv("BACKEND_DATABASE_URL")
    
    if not db_url:
        print("❌ BACKEND_DATABASE_URL not set")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        
        # Get idle connections
        idle_pids = await conn.fetch("""
            SELECT pid, usename, application_name, state_change
            FROM pg_stat_activity 
            WHERE state = 'idle' 
            AND datname IS NOT NULL
            AND pid != pg_backend_pid()
            AND state_change < NOW() - INTERVAL '5 minutes'
        """)
        
        if not idle_pids:
            print("✓ No idle connections to kill")
            await conn.close()
            return
        
        print(f"Found {len(idle_pids)} idle connections (>5 minutes):")
        for row in idle_pids:
            print(f"  - PID {row['pid']}: {row['usename']} ({row['application_name'] or 'N/A'}) - idle since {row['state_change']}")
        
        response = input("\nKill these connections? (yes/no): ")
        if response.lower() == 'yes':
            killed = 0
            for row in idle_pids:
                try:
                    await conn.execute(f"SELECT pg_terminate_backend({row['pid']})")
                    killed += 1
                    print(f"  ✓ Killed PID {row['pid']}")
                except Exception as e:
                    print(f"  ✗ Failed to kill PID {row['pid']}: {e}")
            
            print(f"\n✓ Killed {killed} connections")
        else:
            print("Cancelled")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "kill":
        print("🔪 Killing idle connections...\n")
        asyncio.run(kill_idle_connections())
    else:
        print("🔍 Checking database connections...\n")
        asyncio.run(check_db_connections())
        print("\nTip: Run 'python check_db_connections.py kill' to terminate idle connections")
