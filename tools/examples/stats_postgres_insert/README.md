# Stats PostgreSQL Insert Tool

A specialized agent tool for inserting statistics data into XtracticAI stats tables. This tool enables agents to dynamically track and record information about agents, MCP servers, file processing, and workflow executions with flexible column selection.

## Features

- ✅ **Dynamic Column Selection** - Agent decides which columns to insert based on collected information
- ✅ **Smart Updates** - Can update existing records instead of creating duplicates
- ✅ **Auto-generated Fields** - Automatically adds IDs and timestamps when needed
- ✅ **Multi-table Support** - Works with all stats tables in xtracticai schema
- ✅ **Type Safety** - Handles various data types including JSON, timestamps, and UUIDs
- ✅ **Network Resilience** - IPv4 fallback for connection issues

## Supported Stats Tables

### 1. `agent_stats`
Track agent deployments and executions.

**Key Columns:**
- `agent_name` (required) - Unique agent identifier
- `agent_type` - Type of agent (workflow, chatbot, etc.)
- `status` - Current status (deployed, stopped, running)
- `deployment_url` - URL where agent is deployed
- `total_executions` - Total number of executions
- `successful_executions` - Count of successful executions
- `failed_executions` - Count of failed executions
- `last_execution_at` - Timestamp of last execution

### 2. `mcp_server_stats`
Track MCP server calls and status.

**Key Columns:**
- `server_name` (required) - Unique server identifier
- `server_type` - Type of server (acled, fewsnet, nifi, etc.)
- `status` - Current status (active, inactive)
- `endpoint_url` - Server endpoint URL
- `total_calls` - Total number of calls
- `successful_calls` - Count of successful calls
- `failed_calls` - Count of failed calls
- `last_call_at` - Timestamp of last call

### 3. `file_processing_stats`
Track file uploads and processing.

**Key Columns:**
- `file_name` (required) - Name of the file
- `file_type` (required) - File type (pdf, csv, json, xml, etc.)
- `file_size_bytes` - Size in bytes
- `processing_status` - Status (processing, completed, failed)
- `records_extracted` - Number of records extracted
- `workflow_id` - Associated workflow ID
- `workflow_name` - Associated workflow name
- `error_message` - Error details if failed
- `processing_duration_ms` - Processing time in milliseconds

### 4. `workflow_execution_stats`
Track workflow executions and results.

**Key Columns:**
- `workflow_id` (required) - Workflow identifier
- `workflow_name` (required) - Workflow name
- `execution_type` - Type (manual, scheduled, triggered)
- `status` - Status (running, success, failed)
- `input_files_count` - Number of input files
- `output_records_count` - Number of output records
- `records_processed` - Records processed count
- `records_failed` - Failed records count
- `agents_used` - JSON array of agent names
- `tools_used` - JSON array of tool names
- `duration_ms` - Execution duration in milliseconds
- `error_message` - Error details if failed
- `metadata` - Additional metadata as JSON

## Configuration

### User Parameters (Set Once)

```json
{
  "connection_string": "postgresql://postgres:password@host:port/database",
  "force_ipv4": true,
  "connection_timeout": 30
}
```

## Usage Examples

### Example 1: Track Agent Deployment

```json
{
  "stats_table": "agent_stats",
  "data": {
    "agent_name": "pdf_extraction_agent",
    "agent_type": "workflow",
    "status": "deployed",
    "deployment_url": "https://cdsw.example.com/agent/pdf-extractor",
    "total_executions": 0,
    "successful_executions": 0,
    "failed_executions": 0
  },
  "update_if_exists": true
}
```

### Example 2: Update Agent Execution Stats

```json
{
  "stats_table": "agent_stats",
  "data": {
    "agent_name": "pdf_extraction_agent",
    "total_executions": 15,
    "successful_executions": 14,
    "failed_executions": 1,
    "last_execution_at": "2025-11-20T10:30:00"
  },
  "update_if_exists": true
}
```

### Example 3: Track MCP Server

```json
{
  "stats_table": "mcp_server_stats",
  "data": {
    "server_name": "acled_mcp_server",
    "server_type": "acled",
    "status": "active",
    "endpoint_url": "http://acled-server:8000",
    "total_calls": 0,
    "successful_calls": 0,
    "failed_calls": 0
  },
  "update_if_exists": true
}
```

### Example 4: Track File Processing

```json
{
  "stats_table": "file_processing_stats",
  "data": {
    "file_name": "humanitarian_report_2025.pdf",
    "file_type": "pdf",
    "file_size_bytes": 2458624,
    "processing_status": "completed",
    "records_extracted": 245,
    "workflow_id": "wf_12345",
    "workflow_name": "PDF to Relational",
    "processing_duration_ms": 3456.78
  },
  "update_if_exists": false
}
```

### Example 5: Track Workflow Execution

```json
{
  "stats_table": "workflow_execution_stats",
  "data": {
    "workflow_id": "wf_12345",
    "workflow_name": "PDF to Relational Extraction",
    "execution_type": "manual",
    "status": "success",
    "input_files_count": 3,
    "output_records_count": 689,
    "records_processed": 689,
    "records_failed": 0,
    "agents_used": ["pdf_extraction_agent", "data_validation_agent"],
    "tools_used": ["pdf_reader", "postgres_insert", "csv_writer"],
    "duration_ms": 12456.89,
    "metadata": {
      "user": "admin",
      "environment": "production"
    }
  },
  "update_if_exists": false
}
```

### Example 6: Minimal Insert (Agent Decides Columns)

The agent can include only the columns it has information about:

```json
{
  "stats_table": "agent_stats",
  "data": {
    "agent_name": "new_chatbot_agent",
    "agent_type": "chatbot",
    "status": "deployed"
  },
  "update_if_exists": false
}
```

### Example 7: Update MCP Server Call Stats

```json
{
  "stats_table": "mcp_server_stats",
  "data": {
    "server_name": "fewsnet_mcp",
    "total_calls": 50,
    "successful_calls": 48,
    "failed_calls": 2,
    "last_call_at": "2025-11-20T15:45:00",
    "status": "active"
  },
  "update_if_exists": true
}
```

## Tool Parameters Reference

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `stats_table` | string | Yes | - | Stats table to insert into |
| `data` | object | Yes | - | Dictionary with column-value pairs |
| `update_if_exists` | boolean | No | `false` | Update existing record if found |

## Auto-Generated Fields

The tool automatically adds these fields if not provided:

- **For all inserts**: `id` (UUID v4)
- **For agent_stats & mcp_server_stats**: `created_at`, `updated_at`
- **For file_processing_stats**: `uploaded_at`
- **For workflow_execution_stats**: `started_at`

## Response Format

### Success Response

```json
{
  "success": true,
  "operation": "inserted",
  "table": "xtracticai.agent_stats",
  "record_id": "550e8400-e29b-41d4-a716-446655440000",
  "columns_inserted": ["agent_name", "agent_type", "status", "deployment_url"],
  "message": "Successfully inserted record in xtracticai.agent_stats"
}
```

### Update Response

```json
{
  "success": true,
  "operation": "updated",
  "table": "xtracticai.agent_stats",
  "record_id": "550e8400-e29b-41d4-a716-446655440000",
  "columns_inserted": ["total_executions", "successful_executions", "last_execution_at"],
  "message": "Successfully updated record in xtracticai.agent_stats"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Stats table xtracticai.agent_stats does not exist. Please ensure the stats schema is initialized.",
  "error_type": "TableNotFoundError",
  "rows_inserted": 0
}
```

## Agent Usage Patterns

### Pattern 1: Track New Agent Deployment
1. Agent collects agent info (name, type, URL)
2. Agent calls tool with `update_if_exists: true`
3. Tool creates new record or updates existing one

### Pattern 2: Increment Execution Counts
1. Agent detects workflow execution
2. Agent retrieves current stats
3. Agent increments counters
4. Agent calls tool with `update_if_exists: true`

### Pattern 3: Log File Processing
1. Agent processes file
2. Agent collects metrics (size, duration, records)
3. Agent calls tool to log stats
4. Tool creates new processing record

### Pattern 4: Track Workflow Execution
1. Agent starts workflow
2. Agent collects execution info
3. Agent calls tool at workflow completion
4. Tool stores execution statistics

## Best Practices

1. **Use update_if_exists for counters**: When tracking stats like execution counts
2. **Include timestamps**: Provide timestamps when available for accurate tracking
3. **Minimal data is OK**: Agent can include only available columns
4. **Use JSON for arrays**: Store lists of agents/tools as JSON arrays
5. **Handle errors gracefully**: Check response.success before proceeding

## Error Handling

Common errors and solutions:

**Table doesn't exist:**
```json
{
  "error": "Stats table does not exist. Please ensure the stats schema is initialized."
}
```
Solution: Run stats schema initialization first.

**Invalid table name:**
```json
{
  "error": "Invalid stats_table. Must be one of: agent_stats, mcp_server_stats, file_processing_stats, workflow_execution_stats"
}
```
Solution: Use one of the valid table names.

**Network issues:**
```json
{
  "error": "Network is unreachable. Try setting force_ipv4=true in user parameters."
}
```
Solution: Enable IPv4 fallback in configuration.

## Installation

```bash
pip install -r requirements.txt
```

## Testing the Tool

```bash
python tool.py \
  --user-params '{"connection_string": "postgresql://postgres:password@host:5432/database", "force_ipv4": true}' \
  --tool-params '{"stats_table": "agent_stats", "data": {"agent_name": "test_agent", "agent_type": "workflow", "status": "deployed"}, "update_if_exists": true}'
```

## Integration with Stats Service

This tool complements the StatsService API endpoints and provides agents with direct database access for tracking statistics during workflow execution.
