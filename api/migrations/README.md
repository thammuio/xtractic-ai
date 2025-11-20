# Database Migrations

This folder contains SQL migration scripts for creating and managing the Xtractic AI database schema.

## Initial Setup

Before starting the application, run the table creation script to set up the database schema:

### Using psql
```bash
psql -h <host> -U <username> -d <database> -f create_tables.sql
```

### Using PostgreSQL client
```sql
\i /path/to/create_tables.sql
```

### Using DBeaver or similar tools
1. Open the SQL script file `create_tables.sql`
2. Execute the entire script in your database

## Schema Overview

The script creates the following tables in the `xtracticai` schema:

### Tables Created

1. **agent_stats** - Tracks agent deployments and execution statistics
2. **mcp_server_stats** - Tracks MCP server statistics and call metrics
3. **file_processing_stats** - Tracks file uploads and processing statistics
4. **workflow_execution_stats** - Tracks workflow execution history and performance
5. **workflow_submissions** - Tracks workflow submissions with trace_id for status polling

## Application Behavior

The application **does not** create tables automatically. It only performs:
- **INSERT** operations (adding new records)
- **UPDATE** operations (modifying existing records)
- **DELETE** operations (removing records)

All CREATE TABLE statements must be run manually via this SQL script before starting the application.

## Migration Files

- `create_tables.sql` - Initial schema creation with all tables and indexes
- `add_workflow_submissions_table.sql` - Legacy migration (superseded by create_tables.sql)

## Notes

- All tables use UUID as primary keys with automatic generation
- Indexes are created for common query patterns (status, timestamps, names)
- JSONB fields are used for flexible metadata storage
- Timestamps are automatically managed with DEFAULT NOW()
