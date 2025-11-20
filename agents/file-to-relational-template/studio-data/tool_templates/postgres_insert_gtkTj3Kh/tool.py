"""
PostgreSQL Data Insert Tool

This tool allows agents to insert data into PostgreSQL tables. It can:
- Insert data into existing tables
- Create new tables if they don't exist (based on the data structure)
- Handle bulk inserts with multiple rows
- Support various data types (text, numbers, dates, JSON, etc.)
- Provide detailed feedback on insertion results
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


class UserParameters(BaseModel):
    """
    Database connection parameters. These are configured once per tool instance.
    """
    connection_string: str = Field(
        description="PostgreSQL connection string in format: postgresql://user:password@host:port/database"
    )
    default_schema: Optional[str] = Field(
        default="public",
        description="Default schema to use for tables"
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
    """
    table_name: str = Field(
        description="Name of the table to insert data into"
    )
    data: List[Dict[str, Any]] = Field(
        description="List of dictionaries representing rows to insert. Each dictionary should have column names as keys and values to insert."
    )
    create_if_not_exists: bool = Field(
        default=True,
        description="If True, creates the table if it doesn't exist. If False, raises an error if table doesn't exist."
    )
    upsert: bool = Field(
        default=False,
        description="If True, performs an upsert (INSERT ... ON CONFLICT DO UPDATE). Requires primary_key to be specified."
    )
    primary_key: Optional[List[str]] = Field(
        default=None,
        description="List of column names that form the primary key. Required for upsert operations."
    )
    schema_name: Optional[str] = Field(
        default=None,
        description="Schema name for the table. If not provided, uses default_schema from config."
    )


def infer_column_type(value: Any) -> str:
    """
    Infer PostgreSQL column type from Python value.
    """
    if value is None:
        return "TEXT"
    elif isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "DOUBLE PRECISION"
    elif isinstance(value, (datetime, date)):
        return "TIMESTAMP"
    elif isinstance(value, (dict, list)):
        return "JSONB"
    else:
        return "TEXT"


def infer_table_schema(data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Infer table schema from data by examining all rows.
    Returns a dictionary mapping column names to PostgreSQL types.
    """
    schema = {}
    
    for row in data:
        for column, value in row.items():
            col_type = infer_column_type(value)
            
            if column in schema:
                # If we see conflicting types, use TEXT as fallback
                if schema[column] != col_type and value is not None:
                    schema[column] = "TEXT"
            else:
                schema[column] = col_type
    
    return schema


def create_table(cursor, table_identifier, schema: Dict[str, str], primary_key: Optional[List[str]] = None):
    """
    Create a table with the inferred schema.
    """
    columns = []
    for col_name, col_type in schema.items():
        columns.append(f"{sql.Identifier(col_name).as_string(cursor)} {col_type}")
    
    if primary_key:
        pk_cols = ", ".join([sql.Identifier(pk).as_string(cursor) for pk in primary_key])
        columns.append(f"PRIMARY KEY ({pk_cols})")
    
    create_sql = f"CREATE TABLE IF NOT EXISTS {table_identifier.as_string(cursor)} ({', '.join(columns)})"
    cursor.execute(create_sql)


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
    This helps avoid IPv6 connection issues.
    """
    if not force_ipv4:
        return connection_string
    
    try:
        parsed = urlparse(connection_string)
        hostname = parsed.hostname
        
        if hostname:
            # Try to resolve to IPv4
            try:
                ipv4_address = socket.getaddrinfo(
                    hostname, 
                    parsed.port or 5432, 
                    socket.AF_INET,  # Force IPv4
                    socket.SOCK_STREAM
                )[0][4][0]
                
                # Replace hostname with IPv4 address
                netloc = parsed.netloc.replace(hostname, ipv4_address)
                new_parsed = parsed._replace(netloc=netloc)
                return urlunparse(new_parsed)
            except socket.gaierror:
                # If IPv4 resolution fails, return original
                return connection_string
    except Exception:
        pass
    
    return connection_string


def run_tool(config: UserParameters, args: ToolParameters) -> Any:
    """
    Main tool logic for inserting data into PostgreSQL tables.
    """
    if not args.data:
        return {
            "success": False,
            "error": "No data provided to insert",
            "rows_inserted": 0
        }
    
    schema_name = args.schema_name or config.default_schema
    
    try:
        # Get connection string with IPv4 resolution if needed
        conn_string = get_ipv4_connection_string(
            config.connection_string, 
            config.force_ipv4
        )
        
        # Connect to PostgreSQL with timeout
        # Use dsn parameter explicitly to avoid parsing issues
        conn = psycopg2.connect(
            dsn=conn_string,
            connect_timeout=config.connection_timeout
        )
        cursor = conn.cursor()
        
        # Create table identifier
        table_identifier = sql.Identifier(schema_name, args.table_name)
        
        # Check if table exists
        exists = table_exists(cursor, schema_name, args.table_name)
        
        if not exists:
            if args.create_if_not_exists:
                # Infer schema from data
                inferred_schema = infer_table_schema(args.data)
                create_table(cursor, table_identifier, inferred_schema, args.primary_key)
                conn.commit()
                table_created = True
            else:
                return {
                    "success": False,
                    "error": f"Table {schema_name}.{args.table_name} does not exist and create_if_not_exists is False",
                    "rows_inserted": 0
                }
        else:
            table_created = False
        
        # Prepare insert statement
        if args.data:
            columns = list(args.data[0].keys())
            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                table_identifier,
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )
            
            # Add upsert clause if requested
            if args.upsert:
                if not args.primary_key:
                    return {
                        "success": False,
                        "error": "primary_key must be specified for upsert operations",
                        "rows_inserted": 0
                    }
                
                # Build UPDATE clause for non-primary-key columns
                update_cols = [col for col in columns if col not in args.primary_key]
                update_clause = sql.SQL(', ').join([
                    sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col))
                    for col in update_cols
                ])
                
                conflict_cols = sql.SQL(', ').join(map(sql.Identifier, args.primary_key))
                insert_query = sql.SQL("{} ON CONFLICT ({}) DO UPDATE SET {}").format(
                    insert_query,
                    conflict_cols,
                    update_clause
                )
            
            # Insert data
            rows_inserted = 0
            for row in args.data:
                # Convert special types
                values = []
                for col in columns:
                    val = row.get(col)
                    if isinstance(val, (dict, list)):
                        values.append(Json(val))
                    else:
                        values.append(val)
                
                cursor.execute(insert_query, values)
                rows_inserted += 1
            
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "table_created": table_created,
            "table_name": f"{schema_name}.{args.table_name}",
            "rows_inserted": rows_inserted,
            "columns": list(args.data[0].keys()) if args.data else [],
            "message": f"Successfully inserted {rows_inserted} row(s) into {schema_name}.{args.table_name}"
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
