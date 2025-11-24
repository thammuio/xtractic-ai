# Xtractic AI Postgres MCP Server

An MCP (Model Context Protocol) server for querying and analyzing Xtractic AI's PostgreSQL database containing file processing statistics and workflow submissions. Designed for deployment in Cloudera AI environments.

## Features

This MCP server provides 8 tools to interact with your Xtractic AI database:

### Available Tools

1. **get_file_processing_stats** - Query file processing records with filters
2. **get_workflow_submissions** - View workflow submissions by status, name, or trace_id
3. **get_processing_summary** - Get aggregated statistics and recent failures
4. **get_workflow_submission_summary** - Analyze workflow submission patterns
5. **search_files** - Search files by name pattern or file type
6. **get_failed_submissions** - Find failed submissions with error details
7. **get_workflow_performance** - View performance metrics and success rates

## Installation

Install dependencies using pip or uv:

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Configuration

### Environment Variables

Set these environment variables for database connection:

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=your_database_name
export POSTGRES_USER=your_username
export POSTGRES_PASSWORD=your_password
```

### Cloudera AI Deployment

To deploy in Cloudera AI:

1. Upload the `server.py` file to your Cloudera AI workspace
2. Set environment variables in your Cloudera AI session
3. Install dependencies:
   ```bash
   pip install asyncpg mcp
   ```
4. Run the server:
   ```bash
   python server.py
   ```

### Claude Desktop Configuration

Add to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "xtractic-postgres": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/xtractic-postgres-mcp",
        "run",
        "run-server"
      ],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "xtractic_db",
        "POSTGRES_USER": "your_user",
        "POSTGRES_PASSWORD": "your_password"
      }
    }
  }
}
```

## Usage Examples

### Natural Language Queries

- "Show me the last 10 file processing statistics"
- "What workflows have failed recently?"
- "Give me a summary of all processing activities"
- "How is the pdf-extraction workflow performing?"
- "Find all CSV files that were processed"
- "Show me pending workflow submissions"
- "What files failed to process today?"

## Database Schema

### file_processing_stats
Tracks file processing operations with metadata, status, duration, and error messages.

### workflow_submissions
Tracks workflow execution with trace IDs, status, metadata, and outputs.

## Use Cases

- **Monitoring** - Track failures and system health
- **Analytics** - Generate performance reports
- **Operations** - Find and retry failed submissions
- **Optimization** - Identify bottlenecks and improve performance

## Running the Server

```bash
# Direct execution
python server.py

# Or using the script entry point
uv run run-server
```
