#!/bin/bash

# SSM MCP Server Runner Script
# This script runs the SSM MCP Server with proper environment setup using uv

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Set default environment variables if not set
export MCP_TRANSPORT=${MCP_TRANSPORT:-stdio}
export SMM_READONLY=${SMM_READONLY:-true}

# Run the MCP server using uv
echo "Starting SSM MCP Server with uv..."
uv run python -m ssm_mcp_server.server
