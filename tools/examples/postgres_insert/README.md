# PostgreSQL Data Insert Tool

A powerful agent tool for inserting data into PostgreSQL databases. This tool intelligently handles both existing tables and creates new tables on-the-fly based on your data structure.

## Features

- ✅ **Insert into existing tables** - Works with your current database schema
- ✅ **Auto-create tables** - Automatically creates tables if they don't exist
- ✅ **Smart type inference** - Detects appropriate column types from your data
- ✅ **Bulk inserts** - Insert multiple rows in a single operation
- ✅ **Upsert support** - Update existing rows or insert new ones
- ✅ **Multi-schema support** - Work with different database schemas
- ✅ **JSON support** - Store complex objects as JSONB
- ✅ **Flexible data types** - Handles text, numbers, dates, booleans, and JSON

## Configuration

### User Parameters (Set Once)

```json
{
  "connection_string": "postgresql://postgres:password@host:port/database",
  "default_schema": "public",
  "force_ipv4": true,
  "connection_timeout": 30
}
```

**For your database:**
```json
{
  "connection_string": "postgresql://postgres:dbpass@dbname:5432/postgres",
  "default_schema": "public",
  "force_ipv4": true,
  "connection_timeout": 30
}
```

**Connection Parameters:**
- `connection_string`: PostgreSQL connection URL
- `default_schema`: Default schema to use (default: "public")
- `force_ipv4`: Force IPv4 to avoid IPv6 network issues (default: true, recommended for Supabase)
- `connection_timeout`: Connection timeout in seconds (default: 30)

## Usage Examples

### Example 1: Insert into Existing Table

```json
{
  "table_name": "users",
  "data": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30,
      "active": true
    },
    {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "age": 25,
      "active": true
    }
  ],
  "create_if_not_exists": false
}
```

### Example 2: Auto-Create Table and Insert

```json
{
  "table_name": "products",
  "data": [
    {
      "product_id": "P001",
      "name": "Laptop",
      "price": 999.99,
      "in_stock": true,
      "specs": {
        "ram": "16GB",
        "storage": "512GB SSD"
      }
    }
  ],
  "create_if_not_exists": true,
  "primary_key": ["product_id"]
}
```

### Example 3: Upsert (Update or Insert)

```json
{
  "table_name": "inventory",
  "data": [
    {
      "item_id": "ITEM001",
      "quantity": 100,
      "last_updated": "2025-11-19T10:00:00"
    }
  ],
  "upsert": true,
  "primary_key": ["item_id"],
  "create_if_not_exists": true
}
```

### Example 4: Working with Custom Schema

```json
{
  "table_name": "analytics_events",
  "schema_name": "analytics",
  "data": [
    {
      "event_id": "evt_123",
      "event_type": "page_view",
      "user_id": "user_456",
      "timestamp": "2025-11-19T12:30:00",
      "metadata": {
        "page": "/home",
        "referrer": "google.com"
      }
    }
  ],
  "create_if_not_exists": true
}
```

### Example 5: Complex Data with JSON

```json
{
  "table_name": "api_logs",
  "data": [
    {
      "request_id": "req_789",
      "endpoint": "/api/v1/data",
      "method": "POST",
      "status_code": 200,
      "request_body": {
        "query": "search term",
        "filters": ["active", "verified"]
      },
      "response_data": {
        "results": 42,
        "time_ms": 156
      }
    }
  ],
  "create_if_not_exists": true
}
```

## Tool Parameters Reference

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `table_name` | string | Yes | - | Name of the table to insert into |
| `data` | array of objects | Yes | - | List of rows to insert (each row is a dictionary) |
| `create_if_not_exists` | boolean | No | `true` | Create table if it doesn't exist |
| `upsert` | boolean | No | `false` | Perform upsert instead of insert |
| `primary_key` | array of strings | No | `null` | Columns that form the primary key |
| `schema_name` | string | No | `"public"` | Database schema name |

## Response Format

### Success Response

```json
{
  "success": true,
  "table_created": true,
  "table_name": "public.users",
  "rows_inserted": 2,
  "columns": ["name", "email", "age", "active"],
  "message": "Successfully inserted 2 row(s) into public.users"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Table does not exist and create_if_not_exists is False",
  "error_type": "TableNotFoundError",
  "rows_inserted": 0
}
```

## Supported Data Types

The tool automatically infers PostgreSQL types from Python values:

| Python Type | PostgreSQL Type |
|-------------|-----------------|
| `bool` | `BOOLEAN` |
| `int` | `INTEGER` |
| `float` | `DOUBLE PRECISION` |
| `str` | `TEXT` |
| `datetime/date` | `TIMESTAMP` |
| `dict/list` | `JSONB` |

## Best Practices

1. **Use Primary Keys**: Always specify `primary_key` when creating new tables
2. **Batch Inserts**: Insert multiple rows at once for better performance
3. **Schema Management**: Use different schemas to organize your tables
4. **Upserts for Updates**: Use `upsert=true` when you want to update existing records
5. **JSON for Complex Data**: Store nested objects as JSONB for flexibility

## Error Handling

The tool provides detailed error messages:
- Missing table when `create_if_not_exists=false`
- Invalid connection string
- Missing primary key for upsert operations
- Data type mismatches
- **Network issues** (IPv6 unreachable - automatically resolved with `force_ipv4=true`)
- **Connection timeouts** (adjustable via `connection_timeout`)
- **Authentication failures** (check credentials)

### Common Errors and Solutions

**Network is unreachable / IPv6 issues:**
```json
{
  "force_ipv4": true
}
```

**Connection timeout:**
```json
{
  "connection_timeout": 60
}
```

**Authentication failed:**
Check your connection string credentials are correct.

## Installation

Ensure the required dependencies are installed:

```bash
pip install -r requirements.txt
```

## Testing the Tool

You can test the tool from command line:

```bash
python tool.py \
  --user-params '{"connection_string": "postgresql://postgres:password@dbname:5432/postgres", "force_ipv4": true}' \
  --tool-params '{"table_name": "test_table", "data": [{"id": 1, "name": "Test"}], "create_if_not_exists": true, "primary_key": ["id"]}'
```

## Agent Integration

When integrated with an agent, the tool allows natural language commands like:

- "Insert this customer data into the customers table"
- "Create a new table called orders and add these records"
- "Update the inventory table with these quantities"
- "Store this API response in the api_logs table"

The agent will automatically format the data and call the tool with appropriate parameters.
