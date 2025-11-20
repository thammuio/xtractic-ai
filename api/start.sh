#!/bin/bash

# Quick start script for Xtractic AI API
# This script starts the API server with the deployed workflow integration

set -e

echo "🚀 Starting Xtractic AI API..."
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env and add your Cloudera credentials:"
    echo "   - CDSW_DOMAIN"
    echo "   - CDSW_APIV2_KEY"
    echo "   - CDSW_PROJECT_ID"
    echo "   - DEPLOYED_WORKFLOW_URL"
    echo ""
    read -p "Press Enter after you've configured .env to continue..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if cmlapi is installed
if ! python -c "import cmlapi" 2>/dev/null; then
    echo "⚠️  cmlapi not installed. Installing..."
    pip install cmlapi
fi

echo ""
echo "✅ Setup complete!"
echo ""

# Get port from environment or use default
PORT=${CDSW_APP_PORT:-9000}

echo "🌐 Starting API server on port $PORT..."
echo "📖 API Documentation will be available at:"
echo "   - Swagger UI: http://localhost:$PORT/docs"
echo "   - ReDoc: http://localhost:$PORT/redoc"
echo ""
echo "📡 Workflow endpoints:"
echo "   - POST /api/workflows/deployed/kickoff"
echo "   - GET  /api/workflows/deployed/events"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the API
python main.py
