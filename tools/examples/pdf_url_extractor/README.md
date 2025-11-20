# PDF URL Extractor Tool

This tool downloads a PDF from a given URL and extracts its text content and tables. It's designed to work with agents that need to process PDF data for downstream tasks.

## Features

- **URL-based PDF Download**: Downloads PDF files from any public URL
- **Text Extraction**: Extracts all text content from the PDF
- **Table Extraction**: Optionally extracts tables with structured data
- **Flexible Output**: Returns data in JSON or plain text format
- **Agent-Friendly**: Output is structured for easy consumption by AI agents

## Usage

### Parameters

#### User Parameters
None required - this tool works without user configuration.

#### Tool Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pdf_url` | string | Yes | - | The URL of the PDF file to download and extract |
| `extract_tables` | boolean | No | `true` | Whether to extract tables from the PDF |
| `output_format` | string | No | `json` | Output format: `text` or `json` |

### Example Usage

#### Extract data from the employee records PDF (JSON format):
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "pdf_url": "https://ru1xauqqi4bfrekr.public.blob.vercel-storage.com/pdfs/employee_records.pdf",
    "extract_tables": true,
    "output_format": "json"
  }'
```

#### Extract only text without tables (plain text format):
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "pdf_url": "https://example.com/document.pdf",
    "extract_tables": false,
    "output_format": "text"
  }'
```

## Output Format

### JSON Output Structure
```json
{
  "pages": [
    {
      "page_number": 1,
      "text": "Page content...",
      "tables": [
        {
          "page": 1,
          "table_index": 1,
          "data": [
            ["Header1", "Header2", "Header3"],
            ["Row1Col1", "Row1Col2", "Row1Col3"]
          ]
        }
      ]
    }
  ],
  "full_text": "Complete text from all pages...",
  "tables": [...],
  "metadata": {
    "num_pages": 5,
    "pdf_path": "/tmp/..."
  }
}
```

### Text Output Format
```
=== PDF Content (5 pages) ===

[Full text content from all pages]

=== Tables Found (3) ===

Table on Page 1:
Header1 | Header2 | Header3
Value1 | Value2 | Value3
```

## Integration with Agents

This tool is designed to be used by AI agents in workflows where PDF data needs to be processed:

1. **Data Extraction**: Agent calls this tool with a PDF URL
2. **Data Processing**: Agent receives structured data (text + tables)
3. **Next Steps**: Agent can analyze, transform, or store the extracted data

Example agent workflow:
```python
# Agent receives PDF URL
pdf_url = "https://example.com/report.pdf"

# Extract data using this tool
result = extract_pdf_data(pdf_url)

# Agent can now:
# - Analyze the text content
# - Process tables
# - Generate summaries
# - Store data in databases
# - Make decisions based on content
```

## Requirements

Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Error Handling

The tool handles common errors gracefully:
- Invalid URLs
- Network timeouts
- Non-PDF files
- Corrupted PDFs
- Extraction failures

All errors are returned as descriptive error messages.

## Limitations

- Works only with text-based PDFs (not scanned images)
- Requires public URLs (no authentication support)
- Large PDFs may take longer to download and process
- Table extraction works best with well-formatted tables

## Testing

Test with the provided employee records PDF:
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "pdf_url": "https://ru1xauqqi4bfrekr.public.blob.vercel-storage.com/pdfs/employee_records.pdf",
    "extract_tables": true,
    "output_format": "json"
  }'
```
