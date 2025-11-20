"""
PDF URL Extractor Tool

This tool downloads a PDF from a given URL and extracts its text content.
It supports both simple text extraction and structured data extraction with tables.

The tool handles:
- Downloading PDFs from public URLs
- Extracting text content from all pages
- Extracting tables from PDFs
- Returning formatted data that can be used by agents for further processing

Args:
    pdf_url (str): The URL of the PDF file to download and extract
    extract_tables (bool): Whether to extract tables from the PDF (default: True)
    output_format (str): Format of the output - 'text' or 'json' (default: 'json')

Returns:
    dict or str: Extracted content from the PDF, including text and optionally tables
"""

from typing import Literal, Optional, Dict, List, Any
from pydantic import BaseModel, Field, HttpUrl
import json
import argparse
import requests
import tempfile
import pdfplumber
from pathlib import Path


class UserParameters(BaseModel):
    """User configuration parameters (empty for this tool)"""
    pass


class ToolParameters(BaseModel):
    """Tool execution parameters"""
    pdf_url: str = Field(
        description="The URL of the PDF file to download and extract data from"
    )
    extract_tables: bool = Field(
        description="Whether to extract tables from the PDF",
        default=True
    )
    output_format: Literal["text", "json"] = Field(
        description="Output format: 'text' for plain text or 'json' for structured data",
        default="json"
    )


def download_pdf(url: str, temp_path: Path) -> None:
    """
    Download PDF from URL to a temporary file
    
    Args:
        url: URL of the PDF file
        temp_path: Path where to save the downloaded PDF
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    # Verify content type
    content_type = response.headers.get('content-type', '')
    if 'application/pdf' not in content_type.lower() and not url.lower().endswith('.pdf'):
        raise ValueError(f"URL does not appear to be a PDF file. Content-Type: {content_type}")
    
    temp_path.write_bytes(response.content)


def extract_pdf_content(pdf_path: Path, extract_tables: bool = True) -> Dict[str, Any]:
    """
    Extract text and optionally tables from PDF
    
    Args:
        pdf_path: Path to the PDF file
        extract_tables: Whether to extract tables
        
    Returns:
        Dictionary containing extracted content
    """
    result = {
        "pages": [],
        "full_text": "",
        "tables": [],
        "metadata": {}
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        # Extract metadata
        result["metadata"] = {
            "num_pages": len(pdf.pages),
            "pdf_path": str(pdf_path)
        }
        
        all_text = []
        
        for page_num, page in enumerate(pdf.pages, start=1):
            page_data = {
                "page_number": page_num,
                "text": "",
                "tables": []
            }
            
            # Extract text
            text = page.extract_text() or ""
            page_data["text"] = text
            all_text.append(text)
            
            # Extract tables if requested
            if extract_tables:
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if table:  # Only add non-empty tables
                        table_data = {
                            "page": page_num,
                            "table_index": table_idx + 1,
                            "data": table
                        }
                        page_data["tables"].append(table_data)
                        result["tables"].append(table_data)
            
            result["pages"].append(page_data)
        
        result["full_text"] = "\n\n".join(all_text)
    
    return result


def format_output(content: Dict[str, Any], output_format: str) -> str:
    """
    Format the extracted content based on the requested format
    
    Args:
        content: Extracted PDF content
        output_format: Desired output format ('text' or 'json')
        
    Returns:
        Formatted string output
    """
    if output_format == "text":
        output_lines = []
        output_lines.append(f"=== PDF Content ({content['metadata']['num_pages']} pages) ===\n")
        output_lines.append(content["full_text"])
        
        if content["tables"]:
            output_lines.append(f"\n\n=== Tables Found ({len(content['tables'])}) ===\n")
            for table in content["tables"]:
                output_lines.append(f"\nTable on Page {table['page']}:")
                for row in table['data']:
                    output_lines.append(" | ".join(str(cell or "") for cell in row))
                output_lines.append("")
        
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
        Extracted PDF content in the requested format
    """
    try:
        # Create temporary file for PDF download
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            # Download the PDF
            print(f"Downloading PDF from: {args.pdf_url}")
            download_pdf(args.pdf_url, temp_path)
            print(f"PDF downloaded successfully ({temp_path.stat().st_size} bytes)")
            
            # Extract content
            print("Extracting PDF content...")
            content = extract_pdf_content(temp_path, args.extract_tables)
            print(f"Extraction complete: {content['metadata']['num_pages']} pages, {len(content['tables'])} tables")
            
            # Format output
            output = format_output(content, args.output_format)
            return output
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
                
    except requests.RequestException as e:
        return f"Error downloading PDF: {str(e)}"
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


OUTPUT_KEY = "tool_output"
"""Tool output key used for identifying the output"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract data from a PDF file at a given URL"
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
