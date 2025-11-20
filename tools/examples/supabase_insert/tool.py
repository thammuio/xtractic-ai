"""
Supabase Insert Tool - Insert extracted data into Supabase tables.

This tool allows agents to insert data into Supabase tables. It supports:
- Auto-create tables on the fly based on data structure
- Single record insertion
- Bulk record insertion
- Auto-handling of timestamps
- Upsert operations (insert or update on conflict)
- Custom conflict resolution columns
- Intelligent type inference from data
"""

from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict, Union
import json
import argparse
from supabase import create_client, Client
from datetime import datetime
import re


def infer_postgres_type(value: Any) -> str:
    """
    Infer PostgreSQL data type from Python value.
    """
    if value is None:
        return "TEXT"
    elif isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, int):
        return "BIGINT"
    elif isinstance(value, float):
        return "NUMERIC"
    elif isinstance(value, str):
        # Check if it looks like a timestamp
        if re.match(r'\d{4}-\d{2}-\d{2}', value):
            return "TIMESTAMPTZ"
        # Check if it's a long text
        if len(value) > 255:
            return "TEXT"
        return "TEXT"
    elif isinstance(value, (list, dict)):
        return "JSONB"
    else:
        return "TEXT"


def create_table_from_data(supabase: Client, table_name: str, sample_record: Dict[str, Any], primary_key: str = "id") -> Dict[str, Any]:
    """
    Create a table based on the structure of a sample record.
    """
    try:
        # Build column definitions
        columns = []
        
        # Add primary key if not in data
        if primary_key not in sample_record:
            columns.append(f"{primary_key} BIGSERIAL PRIMARY KEY")
        
        # Add columns based on data structure
        for key, value in sample_record.items():
            if key == primary_key:
                # If primary key is in data, make it PRIMARY KEY
                pg_type = infer_postgres_type(value)
                columns.append(f"{key} {pg_type} PRIMARY KEY")
            else:
                pg_type = infer_postgres_type(value)
                columns.append(f"{key} {pg_type}")
        
        # Build CREATE TABLE statement
        columns_sql = ",\n  ".join(columns)
        create_table_sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
  {columns_sql}
);"""
        
        print(f"Creating table with SQL:\n{create_table_sql}")
        
        # Execute SQL via Supabase RPC or direct query
        # Note: This requires service role key and proper permissions
        supabase.postgrest.session.post(
            f"{supabase.postgrest.url.rstrip('/')}/",
            json={"query": create_table_sql}
        )
        
        return {
            "created": True,
            "table": table_name,
            "columns": list(sample_record.keys()),
            "sql": create_table_sql
        }
    except Exception as e:
        return {
            "created": False,
            "error": str(e),
            "note": "Table creation requires service role key with proper permissions"
        }


class UserParameters(BaseModel):
    """
    User configuration parameters for Supabase connection.
    These are typically set once per tool instance.
    """
    supabase_url: str = Field(description="Supabase project URL (e.g., https://xxx.supabase.co)")
    supabase_key: str = Field(description="Supabase API key (anon or service role key)")
    default_table: Optional[str] = Field(
        default=None,
        description="Optional default table name to use if not specified in tool parameters"
    )
    auto_create_table: Optional[bool] = Field(
        default=True,
        description="If True, automatically creates table if it doesn't exist based on data structure"
    )


class ToolParameters(BaseModel):
    """
    Parameters passed for each tool call.
    """
    table_name: Optional[str] = Field(
        default=None,
        description="Name of the Supabase table to insert data into. If not provided, uses default_table from user config."
    )
    data: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(
        description="Data to insert. Can be a single record (dict) or multiple records (list of dicts)."
    )
    upsert: Optional[bool] = Field(
        default=False,
        description="If True, performs an upsert (insert or update on conflict). Requires on_conflict to be set."
    )
    on_conflict: Optional[str] = Field(
        default=None,
        description="Column name(s) to use for conflict resolution in upsert. Comma-separated for multiple columns (e.g., 'id' or 'email,user_id')."
    )
    return_records: Optional[bool] = Field(
        default=True,
        description="If True, returns the inserted/updated records. If False, returns count only."
    )
    add_timestamp: Optional[bool] = Field(
        default=True,
        description="If True, automatically adds 'created_at' timestamp to records if not present."
    )
    primary_key: Optional[str] = Field(
        default="id",
        description="Primary key column name for auto-created tables. Defaults to 'id' (auto-increment)."
    )


def run_tool(config: UserParameters, args: ToolParameters) -> Any:
    """
    Main tool logic: Insert data into Supabase table.
    """
    try:
        # Initialize Supabase client
        supabase: Client = create_client(config.supabase_url, config.supabase_key)
        
        # Determine table name
        table_name = args.table_name or config.default_table
        if not table_name:
            return {
                "success": False,
                "error": "No table name provided. Specify table_name in tool parameters or default_table in user config."
            }
        
        # Normalize data to list format
        records = args.data if isinstance(args.data, list) else [args.data]
        
        # Add timestamps if requested
        if args.add_timestamp:
            current_time = datetime.utcnow().isoformat()
            for record in records:
                if 'created_at' not in record:
                    record['created_at'] = current_time
        
        # Track if table was created
        table_created = False
        table_creation_info = None
        
        # Try to insert, create table if it doesn't exist
        try:
            query = supabase.table(table_name)
            
            # Perform insert or upsert
            if args.upsert and args.on_conflict:
                # Parse on_conflict columns
                conflict_cols = [col.strip() for col in args.on_conflict.split(',')]
                response = query.upsert(
                    records,
                    on_conflict=','.join(conflict_cols)
                ).execute()
            else:
                response = query.insert(records).execute()
                
        except Exception as insert_error:
            # Check if error is due to table not existing
            error_msg = str(insert_error).lower()
            if config.auto_create_table and ('does not exist' in error_msg or 'relation' in error_msg or 'table' in error_msg):
                print(f"Table '{table_name}' not found. Attempting to create...")
                
                # Create table based on first record
                table_creation_info = create_table_from_data(
                    supabase, 
                    table_name, 
                    records[0],
                    args.primary_key or "id"
                )
                
                if table_creation_info.get("created"):
                    table_created = True
                    print(f"Table '{table_name}' created successfully. Retrying insert...")
                    
                    # Retry insert after table creation
                    query = supabase.table(table_name)
                    if args.upsert and args.on_conflict:
                        conflict_cols = [col.strip() for col in args.on_conflict.split(',')]
                        response = query.upsert(
                            records,
                            on_conflict=','.join(conflict_cols)
                        ).execute()
                    else:
                        response = query.insert(records).execute()
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create table: {table_creation_info.get('error')}",
                        "note": table_creation_info.get('note', ''),
                        "original_error": str(insert_error)
                    }
            else:
                # Re-raise if it's a different error or auto_create is disabled
                raise insert_error
        
        # Prepare result
        result = {
            "success": True,
            "table": table_name,
            "operation": "upsert" if args.upsert else "insert",
            "count": len(records)
        }
        
        if table_created:
            result["table_created"] = True
            result["inferred_schema"] = table_creation_info
        
        if args.return_records:
            result["records"] = response.data
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


OUTPUT_KEY = "tool_output"
"""
Only content after this key is passed back to the agent as structured output.
"""


if __name__ == "__main__":
    """
    Tool entrypoint.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-params", required=True, help="User configuration (JSON)")
    parser.add_argument("--tool-params", required=True, help="Tool parameters (JSON)")
    args = parser.parse_args()
    
    # Parse JSON into dictionaries
    user_dict = json.loads(args.user_params)
    tool_dict = json.loads(args.tool_params)
    
    # Validate dictionaries against Pydantic models
    config = UserParameters(**user_dict)
    params = ToolParameters(**tool_dict)
    
    # Run the tool
    output = run_tool(config, params)
    print(OUTPUT_KEY, json.dumps(output, indent=2))
