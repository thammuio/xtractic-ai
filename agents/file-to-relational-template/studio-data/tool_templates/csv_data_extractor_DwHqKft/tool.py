"""
CSV URL Extractor Tool

This tool downloads a CSV file from a given URL and extracts its data content.
It supports various CSV formats and provides flexible data extraction options.

The tool handles:
- Downloading CSV files from public URLs
- Parsing CSV data with different delimiters
- Extracting headers and data rows
- Filtering and transforming data
- Returning formatted data that can be used by agents for further processing

Args:
    csv_url (str): The URL of the CSV file to download and extract
    delimiter (str): The delimiter used in the CSV file (default: ',')
    has_header (bool): Whether the CSV has a header row (default: True)
    max_rows (int): Maximum number of rows to return (0 = all rows, default: 0)
    output_format (str): Format of the output - 'json' or 'text' (default: 'json')

Returns:
    dict or str: Extracted content from the CSV, including headers and data rows
"""

from typing import Literal, Optional, Dict, List, Any
from pydantic import BaseModel, Field
import json
import argparse
import requests
import tempfile
import csv
from pathlib import Path
from io import StringIO


class UserParameters(BaseModel):
    """User configuration parameters (empty for this tool)"""
    pass


class ToolParameters(BaseModel):
    """Tool execution parameters"""
    csv_url: str = Field(
        description="The URL of the CSV file to download and extract data from"
    )
    delimiter: str = Field(
        description="The delimiter used in the CSV file (e.g., ',', ';', '\t', '|')",
        default=","
    )
    has_header: bool = Field(
        description="Whether the CSV file has a header row",
        default=True
    )
    max_rows: int = Field(
        description="Maximum number of data rows to return (0 = all rows)",
        default=0,
        ge=0
    )
    output_format: Literal["json", "text"] = Field(
        description="Output format: 'json' for structured data or 'text' for plain text",
        default="json"
    )


def download_csv(url: str) -> str:
    """
    Download CSV from URL and return content as string
    
    Args:
        url: URL of the CSV file
        
    Returns:
        CSV content as string
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    # Verify content type (be flexible as CSV can have various content types)
    content_type = response.headers.get('content-type', '').lower()
    valid_types = ['text/csv', 'application/csv', 'text/plain', 'application/octet-stream']
    
    if not any(ct in content_type for ct in valid_types) and not url.lower().endswith('.csv'):
        # Still try to process it, but warn
        print(f"Warning: Content-Type is '{content_type}', expected CSV format")
    
    return response.text


def extract_csv_content(csv_text: str, delimiter: str, has_header: bool, max_rows: int) -> Dict[str, Any]:
    """
    Extract data from CSV content
    
    Args:
        csv_text: CSV content as string
        delimiter: CSV delimiter character
        has_header: Whether CSV has header row
        max_rows: Maximum rows to extract (0 = all)
        
    Returns:
        Dictionary containing extracted content
    """
    result = {
        "headers": [],
        "data": [],
        "metadata": {}
    }
    
    # Parse CSV
    csv_reader = csv.reader(StringIO(csv_text), delimiter=delimiter)
    rows = list(csv_reader)
    
    if not rows:
        result["metadata"] = {
            "total_rows": 0,
            "total_columns": 0,
            "rows_returned": 0
        }
        return result
    
    # Extract headers
    if has_header and rows:
        result["headers"] = rows[0]
        data_rows = rows[1:]
    else:
        # Generate generic headers
        num_cols = len(rows[0]) if rows else 0
        result["headers"] = [f"Column_{i+1}" for i in range(num_cols)]
        data_rows = rows
    
    # Apply max_rows limit
    if max_rows > 0:
        data_rows = data_rows[:max_rows]
    
    result["data"] = data_rows
    
    # Calculate metadata
    result["metadata"] = {
        "total_rows": len(rows) - (1 if has_header else 0),
        "total_columns": len(result["headers"]),
        "rows_returned": len(data_rows),
        "has_header": has_header,
        "delimiter": delimiter
    }
    
    return result


def format_output(content: Dict[str, Any], output_format: str) -> str:
    """
    Format the extracted content based on the requested format
    
    Args:
        content: Extracted CSV content
        output_format: Desired output format ('json' or 'text')
        
    Returns:
        Formatted string output
    """
    if output_format == "text":
        output_lines = []
        metadata = content["metadata"]
        
        output_lines.append(f"=== CSV Content ===")
        output_lines.append(f"Total Rows: {metadata['total_rows']}")
        output_lines.append(f"Total Columns: {metadata['total_columns']}")
        output_lines.append(f"Rows Returned: {metadata['rows_returned']}")
        output_lines.append(f"Delimiter: '{metadata['delimiter']}'")
        output_lines.append("")
        
        # Headers
        if content["headers"]:
            output_lines.append("Headers:")
            output_lines.append(" | ".join(content["headers"]))
            output_lines.append("-" * 80)
        
        # Data rows
        if content["data"]:
            output_lines.append("Data:")
            for row in content["data"]:
                output_lines.append(" | ".join(str(cell) for cell in row))
        else:
            output_lines.append("No data rows found.")
        
        return "\n".join(output_lines)
    
    else:  # json format
        return json.dumps(content, indent=2, ensure_ascii=False)


def run_tool(config: UserParameters, args: ToolParameters) -> str:
    """
    Main tool execution function
    
    Args:
        config: User configuration
        args: Tool parameters
        
    Returns:
        Extracted CSV content in the requested format
    """
    try:
        # Download the CSV
        print(f"Downloading CSV from: {args.csv_url}")
        csv_text = download_csv(args.csv_url)
        print(f"CSV downloaded successfully ({len(csv_text)} bytes)")
        
        # Extract content
        print("Extracting CSV content...")
        content = extract_csv_content(
            csv_text,
            args.delimiter,
            args.has_header,
            args.max_rows
        )
        print(f"Extraction complete: {content['metadata']['rows_returned']} rows, {content['metadata']['total_columns']} columns")
        
        # Format output
        output = format_output(content, args.output_format)
        return output
        
    except requests.RequestException as e:
        return f"Error downloading CSV: {str(e)}"
    except csv.Error as e:
        return f"CSV parsing error: {str(e)}"
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


OUTPUT_KEY = "tool_output"
"""Tool output key used for identifying the output"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract data from a CSV file at a given URL"
    )
    parser.add_argument(
        "--user-params",
        required=True,
        help="JSON string for user configuration"
    )
    parser.add_argument(
        "--tool-params",
        required=True,
        help="JSON string for tool arguments"
    )
    args = parser.parse_args()
    
    # Parse JSON into dictionaries
    config_dict = json.loads(args.user_params)
    params_dict = json.loads(args.tool_params)
    
    # Validate dictionaries against Pydantic models
    config = UserParameters(**config_dict)
    params = ToolParameters(**params_dict)
    
    # Run the tool
    output = run_tool(config, params)
    print(OUTPUT_KEY, output)
