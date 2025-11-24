"""
Stats PostgreSQL Insert Tool

This tool allows agents to dynamically insert statistics data into the XtracticAI stats tables.
The agent can decide which table and columns to use based on the context of collected information.

Supported Stats Tables:
- file_processing_stats: Track file uploads and processing
- workflow_submissions: Track workflow submission and polling status
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
import json
import argparse
import psycopg2
from psycopg2.extras import Json
from psycopg2 import sql
from datetime import datetime, date
import socket
from urllib.parse import urlparse, urlunparse
import uuid


class UserParameters(BaseModel):
    """
    Database connection parameters configured once per tool instance.
    """
    connection_string: str = Field(
        description="PostgreSQL connection string in format: postgresql://user:password@host:port/database"
    )
    force_ipv4: bool = Field(
        default=True,
        description="Force IPv4 connections to avoid IPv6 network issues"
    )
    connection_timeout: int = Field(
        default=30,
        description="Connection timeout in seconds"
    )


class ToolParameters(BaseModel):
    """
    Parameters for each tool invocation by the agent.
    The agent can dynamically choose which stats table and what data to insert.
    """
    stats_table: str = Field(
        description="Stats table to insert into. Options: 'file_processing_stats', 'workflow_submissions'"
    )
    data: Dict[str, Any] = Field(
        description="Dictionary with column names as keys and values to insert. Agent can include any relevant columns based on collected information."
    )
    update_if_exists: bool = Field(
        default=False,
        description="If True, updates existing record if it exists (based on unique key field). If False, always inserts new record."
    )


def convert_value_for_postgres(value: Any) -> Any:
    """
    Convert Python values to PostgreSQL-compatible format.
    """
    if value is None:
        return None
    elif isinstance(value, (dict, list)):
        return Json(value)
    elif isinstance(value, datetime):
        return value
    elif isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    elif isinstance(value, uuid.UUID):
        return str(value)
    else:
        return value


def get_table_identifier(stats_table: str) -> tuple:
    """
    Get schema and table name for stats tables.
    All stats tables are in xtracticai schema.
    """
    return ("xtracticai", stats_table)


def get_primary_key_column(stats_table: str) -> str:
    """
    Get the unique identifier column for each stats table for update operations.
    """
    table_keys = {
        "file_processing_stats": "id",
        "workflow_submissions": "trace_id"
    }
    return table_keys.get(stats_table, "id")


def get_expected_columns(stats_table: str) -> list:
    """
    Get the expected columns for each stats table.
    """
    table_columns = {
        "file_processing_stats": [
            "id", "file_name", "file_type", "file_size_bytes", "processing_status",
            "records_extracted", "workflow_id", "workflow_name", "error_message",
            "processing_duration_ms", "uploaded_at", "completed_at"
        ],
        "workflow_submissions": [
            "id", "trace_id", "workflow_url", "uploaded_file_url", "file_name",
            "query", "status", "workflow_id", "workflow_name", "execution_id",
            "file_id", "error_message", "metadata", "submitted_at", "last_polled_at",
            "completed_at"
        ]
    }
    return table_columns.get(stats_table, [])


def table_exists(cursor, schema_name: str, table_name: str) -> bool:
    """
    Check if a table exists in the database.
    """
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_name = %s
        )
    """, (schema_name, table_name))
    return cursor.fetchone()[0]


def get_ipv4_connection_string(connection_string: str, force_ipv4: bool = True) -> str:
    """
    Resolve hostname to IPv4 address if force_ipv4 is True.
    """
    if not force_ipv4:
        return connection_string
    
    try:
        parsed = urlparse(connection_string)
        hostname = parsed.hostname
        
        if hostname:
            try:
                ipv4_address = socket.getaddrinfo(
                    hostname, 
                    parsed.port or 5432, 
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )[0][4][0]
                
                netloc = parsed.netloc.replace(hostname, ipv4_address)
                new_parsed = parsed._replace(netloc=netloc)
                return urlunparse(new_parsed)
            except socket.gaierror:
                return connection_string
    except Exception:
        pass
    
    return connection_string


def check_existing_record(cursor, schema_name: str, table_name: str, key_column: str, key_value: Any) -> Optional[str]:
    """
    Check if a record exists based on the key column.
    Returns the id if exists, None otherwise.
    """
    try:
        query = sql.SQL("SELECT id FROM {}.{} WHERE {} = %s").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name),
            sql.Identifier(key_column)
        )
        cursor.execute(query, (key_value,))
        result = cursor.fetchone()
        return str(result[0]) if result else None
    except Exception:
        return None


def run_tool(config: UserParameters, args: ToolParameters) -> Any:
    """
    Main tool logic for inserting stats data into PostgreSQL tables.
    """
    # Validate stats table
    valid_tables = ["file_processing_stats", "workflow_submissions"]
    if args.stats_table not in valid_tables:
        return {
            "success": False,
            "error": f"Invalid stats_table. Must be one of: {', '.join(valid_tables)}",
            "rows_inserted": 0
        }
    
    if not args.data:
        return {
            "success": False,
            "error": "No data provided to insert",
            "rows_inserted": 0
        }
    
    # Validate columns match expected schema
    expected_columns = get_expected_columns(args.stats_table)
    provided_columns = set(args.data.keys())
    
    # Check for invalid columns (columns not in the schema)
    invalid_columns = provided_columns - set(expected_columns)
    
    if invalid_columns:
        # Return descriptive text when columns don't match
        return {
            "success": False,
            "message": f"Column validation failed for table '{args.stats_table}'. "
                      f"The following columns are not valid: {', '.join(sorted(invalid_columns))}. "
                      f"Expected columns are: {', '.join(expected_columns)}. "
                      f"Please ensure your data matches the table schema.",
            "invalid_columns": sorted(list(invalid_columns)),
            "expected_columns": expected_columns,
            "provided_columns": sorted(list(provided_columns))
        }
    
    try:
        # Get connection string with IPv4 resolution
        conn_string = get_ipv4_connection_string(
            config.connection_string, 
            config.force_ipv4
        )
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dsn=conn_string,
            connect_timeout=config.connection_timeout
        )
        cursor = conn.cursor()
        
        schema_name, table_name = get_table_identifier(args.stats_table)
        
        # Check if table exists
        if not table_exists(cursor, schema_name, table_name):
            return {
                "success": False,
                "error": f"Stats table {schema_name}.{table_name} does not exist. Please ensure the stats schema is initialized.",
                "rows_inserted": 0
            }
        
        # Prepare data - add auto-generated fields if not present
        data = args.data.copy()
        
        # Add id if not present
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
        
        # Add timestamps if not present
        if "uploaded_at" not in data and args.stats_table == "file_processing_stats":
            data["uploaded_at"] = datetime.now()
        
        if "submitted_at" not in data and args.stats_table == "workflow_submissions":
            data["submitted_at"] = datetime.now()
        
        # Check if we should update existing record
        operation_performed = "inserted"
        existing_id = None
        
        if args.update_if_exists:
            key_column = get_primary_key_column(args.stats_table)
            if key_column in data and key_column != "id":
                existing_id = check_existing_record(cursor, schema_name, table_name, key_column, data[key_column])
        
        if existing_id and args.update_if_exists:
            # Update existing record
            # Remove id from update data if present
            update_data = {k: v for k, v in data.items() if k != "id"}
            
            # Build UPDATE statement
            set_clause = sql.SQL(', ').join([
                sql.SQL("{} = %s").format(sql.Identifier(col))
                for col in update_data.keys()
            ])
            
            update_query = sql.SQL("UPDATE {}.{} SET {} WHERE id = %s").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                set_clause
            )
            
            # Convert values
            values = [convert_value_for_postgres(v) for v in update_data.values()]
            values.append(uuid.UUID(existing_id))
            
            cursor.execute(update_query, values)
            operation_performed = "updated"
            record_id = existing_id
        else:
            # Insert new record
            columns = list(data.keys())
            
            # Build INSERT statement
            insert_query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({}) RETURNING id").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )
            
            # Convert values
            values = [convert_value_for_postgres(data[col]) for col in columns]
            
            cursor.execute(insert_query, values)
            result = cursor.fetchone()
            record_id = str(result[0]) if result else data.get("id")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "operation": operation_performed,
            "table": f"{schema_name}.{table_name}",
            "record_id": record_id,
            "columns_inserted": list(data.keys()),
            "message": f"Successfully {operation_performed} record in {schema_name}.{table_name}"
        }
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        suggestion = ""
        
        if "Network is unreachable" in error_msg or "IPv6" in error_msg:
            suggestion = " Try setting force_ipv4=true in user parameters."
        elif "timeout" in error_msg.lower():
            suggestion = " Try increasing connection_timeout in user parameters."
        elif "authentication failed" in error_msg.lower():
            suggestion = " Check your username and password."
        
        return {
            "success": False,
            "error": error_msg + suggestion,
            "error_type": "OperationalError",
            "rows_inserted": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "rows_inserted": 0
        }


OUTPUT_KEY = "tool_output"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-params", required=True, help="Tool configuration")
    parser.add_argument("--tool-params", required=True, help="Tool arguments")
    args = parser.parse_args()
    
    # Parse JSON into dictionaries
    user_dict = json.loads(args.user_params)
    tool_dict = json.loads(args.tool_params)
    
    # Validate dictionaries against Pydantic models
    config = UserParameters(**user_dict)
    params = ToolParameters(**tool_dict)
    
    # Run the tool
    output = run_tool(config, params)
    print(OUTPUT_KEY, output)
