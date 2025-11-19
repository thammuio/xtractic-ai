#!/bin/bash

# SSB MCP Server wrapper script
# This script ensures the proper environment is set up for the MCP server

# Set the working directory
cd /Users/ibrooks/Documents/GitHub/SSB-MCP-Server

# Set environment variables (use values from Claude Desktop config if available)
export SSB_API_BASE="${SSB_API_BASE:-http://localhost:18121}"
export SSB_USER="${SSB_USER:-admin}"
export SSB_PASSWORD="${SSB_PASSWORD:-admin}"
export SSB_READONLY="${SSB_READONLY:-false}"
export MCP_TRANSPORT="${MCP_TRANSPORT:-stdio}"
export MCP_HOST="${MCP_HOST:-127.0.0.1}"
export MCP_PORT="${MCP_PORT:-3030}"
export KNOX_VERIFY_SSL="${KNOX_VERIFY_SSL:-true}"
export HTTP_TIMEOUT_SECONDS="${HTTP_TIMEOUT_SECONDS:-30}"
export HTTP_MAX_RETRIES="${HTTP_MAX_RETRIES:-3}"
export HTTP_RATE_LIMIT_RPS="${HTTP_RATE_LIMIT_RPS:-5}"

# Legacy variables for backward compatibility
export READONLY="${SSB_READONLY}"
export TIMEOUT_SECONDS="${HTTP_TIMEOUT_SECONDS}"
export PROXY_CONTEXT_PATH=""

export PYTHONPATH="/Users/ibrooks/Documents/GitHub/SSB-MCP-Server/src"

# Debug: Print environment variables
echo "SSB_API_BASE: $SSB_API_BASE"
echo "SSB_USER: $SSB_USER"
echo "SSB_READONLY: $SSB_READONLY"

# Activate the virtual environment and run the MCP server
exec /Users/ibrooks/Documents/GitHub/SSB-MCP-Server/.venv/bin/python -m ssb_mcp_server.server
