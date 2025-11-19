# Xtractic AI - FastAPI Backend

A comprehensive FastAPI backend for interacting with Cloudera AI Agent Studio workflows, MCP Servers, RAG databases, and Supabase.

## Features

- 🔄 **Workflow Management** - Integrate with Cloudera AI Agent Studio for workflow orchestration
- 🤖 **AI Assistant** - Chat interface with RAG-enhanced responses
- 📊 **Dataset Management** - Query and manage datasets in Supabase
- 🔧 **ETL Jobs** - Run and monitor ETL data processing jobs
- 🌐 **MCP Integration** - Connect with Model Context Protocol servers
- 📚 **RAG System** - Retrieval Augmented Generation with vector search
- 🚀 **Async Operations** - High-performance async API endpoints

## Architecture

```
api/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py          # Configuration management
│   └── database.py        # Database connections (Supabase, PostgreSQL)
├── routers/
│   ├── workflows.py       # Workflow endpoints
│   ├── datasets.py        # Dataset endpoints
│   ├── ai.py             # AI chat endpoints
│   ├── etl.py            # ETL job endpoints
│   ├── mcp.py            # MCP server endpoints
│   └── rag.py            # RAG endpoints
└── services/
    ├── cloudera_service.py    # Cloudera API integration
    ├── dataset_service.py     # Supabase dataset operations
    ├── ai_service.py          # AI/LLM operations
    ├── etl_service.py         # ETL job management
    ├── mcp_service.py         # MCP server communication
    └── rag_service.py         # RAG operations
```

## Installation

1. **Install dependencies:**
```bash
cd api
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize database:**
```bash
# For Supabase, create the following tables:
# - workflows
# - executions
# - etl_jobs
# - etl_job_logs
# - conversations
# - documents

# For RAG database (PostgreSQL with pgvector):
# CREATE EXTENSION vector;
```

## Configuration

### Required Environment Variables

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anonymous key
- `CLOUDERA_API_URL` - Cloudera AI Agent Studio API URL
- `CLOUDERA_API_KEY` - Cloudera API authentication key
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `RAG_DB_*` - PostgreSQL database credentials for RAG

### Optional Configurations

- `MCP_SERVER_URL` - MCP server endpoint (default: http://localhost:3001)
- `VECTOR_DB_TYPE` - Vector database type (pgvector, pinecone, weaviate)
- `REDIS_URL` - Redis connection for caching

## Running the API

### Development Mode

```bash
cd api
python main.py
```

or

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Workflows
- `GET /api/workflows` - List all workflows
- `GET /api/workflows/{id}` - Get workflow details
- `POST /api/workflows` - Create new workflow
- `POST /api/workflows/{id}/start` - Start workflow execution
- `GET /api/workflows/stats` - Get workflow statistics

### Datasets
- `GET /api/datasets` - List all datasets
- `GET /api/datasets/{name}` - Get dataset data
- `POST /api/datasets/{name}/query` - Query dataset with NLP
- `GET /api/datasets/{name}/export` - Export dataset

### AI Assistant
- `POST /api/ai/chat` - Chat with AI assistant
- `POST /api/ai/insights` - Generate data insights
- `POST /api/ai/generate-query` - Generate SQL from natural language

### ETL Jobs
- `POST /api/etl/run` - Run ETL job
- `GET /api/etl/jobs` - List all jobs
- `GET /api/etl/jobs/{id}` - Get job status
- `POST /api/etl/jobs/{id}/cancel` - Cancel job

### MCP Servers
- `GET /api/mcp/servers` - List MCP servers
- `GET /api/mcp/servers/{id}/tools` - List available tools
- `POST /api/mcp/servers/{id}/tools/invoke` - Invoke tool
- `POST /api/mcp/servers/{id}/prompts/get` - Get prompt

### RAG
- `POST /api/rag/ingest` - Ingest document
- `POST /api/rag/query` - Semantic search
- `POST /api/rag/chat` - RAG-enhanced chat
- `GET /api/rag/collections` - List collections

## API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Integration with Frontend

The API is designed to work seamlessly with the frontend UI in `/ui`. Update the frontend's `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Database Schema

### Supabase Tables

**workflows**
```sql
CREATE TABLE workflows (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  agent_config JSONB,
  workflow_steps JSONB,
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**etl_jobs**
```sql
CREATE TABLE etl_jobs (
  job_id UUID PRIMARY KEY,
  job_name TEXT NOT NULL,
  source_type TEXT,
  source_config JSONB,
  destination_type TEXT,
  destination_config JSONB,
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**conversations**
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### RAG Database (PostgreSQL with pgvector)

```sql
CREATE EXTENSION vector;

CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB,
  collection TEXT DEFAULT 'default',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);
```

## Testing

```bash
pytest tests/
```

## Security

- API keys and secrets should be stored in environment variables
- Use HTTPS in production
- Implement rate limiting
- Add authentication middleware as needed

## Performance

- Uses async/await for non-blocking operations
- Connection pooling for databases
- Redis caching for frequently accessed data
- Background tasks for long-running operations

## Monitoring

- Health check endpoint: `GET /health`
- Prometheus metrics available (optional)

## Contributing

1. Follow FastAPI best practices
2. Add type hints to all functions
3. Document new endpoints
4. Write tests for new features

## License

See LICENSE file in the root directory.
