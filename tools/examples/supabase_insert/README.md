# Supabase Insert Tool

A tool for inserting extracted data from agents into Supabase tables.

## Features

- **Auto-Create Tables**: Automatically creates tables on the fly based on data structure
- **Intelligent Type Inference**: Infers PostgreSQL data types from Python values
- **Single or Bulk Insert**: Insert one record or multiple records at once
- **Upsert Support**: Insert or update on conflict with configurable conflict columns
- **Auto Timestamps**: Automatically add `created_at` timestamps to records
- **Flexible Configuration**: Set default table or specify per-call
- **Error Handling**: Comprehensive error messages for troubleshooting

## User Configuration

Configure once per tool instance:

```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_key": "your-anon-or-service-role-key",
  "default_table": "extracted_data",
  "auto_create_table": true
}
```

### Parameters:
- `supabase_url` (required): Your Supabase project URL
- `supabase_key` (required): Supabase API key (anon or service role)
- `default_table` (optional): Default table name if not specified in tool calls
- `auto_create_table` (optional, default=true): Auto-create tables if they don't exist

## Tool Parameters

Parameters for each tool call:

```json
{
  "table_name": "my_table",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
  },
  "upsert": false,
  "on_conflict": null,
  "return_records": true,
  "add_timestamp": true,
  "primary_key": "id"
}
```

### Parameters:
- `table_name` (optional): Table to insert into. Uses `default_table` if not specified
- `data` (required): Single record (dict) or multiple records (list of dicts)
- `upsert` (optional, default=false): Perform upsert instead of insert
- `on_conflict` (optional): Column(s) for conflict resolution (e.g., "id" or "email,user_id")
- `return_records` (optional, default=true): Return inserted records or just count
- `add_timestamp` (optional, default=true): Auto-add `created_at` timestamp
- `primary_key` (optional, default="id"): Primary key column for auto-created tables

## Usage Examples

### Example 1: Simple Single Record Insert

```python
# Tool Parameters
{
  "table_name": "customers",
  "data": {
    "name": "Alice Smith",
    "email": "alice@example.com",
    "company": "Acme Corp"
  }
}
```

### Example 2: Bulk Insert Multiple Records

```python
# Tool Parameters
{
  "table_name": "products",
  "data": [
    {"name": "Product A", "price": 29.99, "category": "Electronics"},
    {"name": "Product B", "price": 49.99, "category": "Electronics"},
    {"name": "Product C", "price": 19.99, "category": "Books"}
  ],
  "add_timestamp": true
}
```

### Example 3: Upsert with Conflict Resolution

```python
# Tool Parameters
{
  "table_name": "users",
  "data": {
    "email": "john@example.com",
    "name": "John Doe Updated",
    "status": "active"
  },
  "upsert": true,
  "on_conflict": "email"
}
```

### Example 4: Using Default Table

```python
# User Config (set once)
{
  "supabase_url": "https://xxx.supabase.co",
  "supabase_key": "xxx",
  "default_table": "extracted_data"
}

# Tool Parameters (table_name omitted)
{
  "data": {
    "source": "pdf_document",
    "content": "Extracted text here...",
    "confidence": 0.95
  }
}
```

### Example 5: Auto-Create Table from Extracted Data

```python
# Tool Parameters - table will be created automatically if it doesn't exist
{
  "table_name": "scraped_articles",
  "data": {
    "title": "AI Trends in 2025",
    "url": "https://example.com/article",
    "author": "John Smith",
    "published_date": "2025-11-19",
    "word_count": 1500,
    "is_premium": false,
    "tags": ["AI", "Technology", "Machine Learning"],
    "summary": "A comprehensive look at AI trends..."
  }
}

# Response will include table creation info:
{
  "success": true,
  "table": "scraped_articles",
  "operation": "insert",
  "count": 1,
  "table_created": true,
  "inferred_schema": {
    "created": true,
    "table": "scraped_articles",
    "columns": ["title", "url", "author", "published_date", "word_count", "is_premium", "tags", "summary", "created_at"]
  },
  "records": [...]
}
```

## Return Format

### Success Response:
```json
{
  "success": true,
  "table": "customers",
  "operation": "insert",
  "count": 1,
  "records": [
    {
      "id": 123,
      "name": "Alice Smith",
      "email": "alice@example.com",
      "company": "Acme Corp",
      "created_at": "2025-11-19T10:30:00"
    }
  ]
}
```

### Error Response:
```json
{
  "success": false,
  "error": "Table 'invalid_table' does not exist",
  "error_type": "PostgrestAPIError"
}
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get your Supabase credentials:
   - Go to your Supabase project dashboard
   - Navigate to Settings > API
   - Copy your project URL and **service role key** (required for auto-table creation)

3. **Optional**: Create a table manually in Supabase (or let the tool auto-create):
```sql
CREATE TABLE extracted_data (
  id BIGSERIAL PRIMARY KEY,
  source TEXT,
  content TEXT,
  confidence NUMERIC,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Type Inference

When auto-creating tables, the tool intelligently infers PostgreSQL types:

| Python Type | PostgreSQL Type |
|-------------|-----------------|
| `bool` | `BOOLEAN` |
| `int` | `BIGINT` |
| `float` | `NUMERIC` |
| `str` (short) | `TEXT` |
| `str` (date-like) | `TIMESTAMPTZ` |
| `list`, `dict` | `JSONB` |
| `None` | `TEXT` |

## Common Use Cases

### Agent Data Extraction Pipeline
1. Agent extracts data from documents, APIs, or web scraping
2. Agent formats extracted data into structured records
3. Agent calls this tool to persist data to Supabase
4. **Table is auto-created on first insert if it doesn't exist**
5. Data is immediately available for queries, dashboards, or downstream processing

### Dynamic Schema Discovery
- Extract data with varying structures from different sources
- Let the tool automatically create tables based on the actual data
- No need to pre-define schemas or manually create tables
- Perfect for exploratory data extraction and prototyping

### Deduplication with Upsert
Use `upsert` mode with `on_conflict` to avoid duplicate records:
- Email addresses: `on_conflict="email"`
- Compound keys: `on_conflict="user_id,date"`
- UUID-based: `on_conflict="uuid"`

## Tips

- **Use service role key** for write operations and table creation (not anon key)
- **Auto-create is enabled by default** - tables are created automatically if they don't exist
- Enable Row Level Security (RLS) policies in Supabase after table creation for security
- Set up indexes on conflict columns for better upsert performance
- Use `return_records=false` for large bulk inserts to reduce response size
- The tool auto-adds `created_at` timestamps - this column will be included in auto-created tables
- **Type inference**: The tool analyzes your data to infer appropriate PostgreSQL types
- **Flexible schema**: Different data structures can coexist - missing fields become NULL
- For production, consider manually creating tables with constraints, indexes, and RLS policies
- Set `auto_create_table=false` in production if you want to enforce pre-defined schemas
