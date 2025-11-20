# CSV URL Extractor Tool

This tool downloads a CSV file from a given URL and extracts its data content. It's designed to work with agents that need to process CSV data for downstream tasks.

## Features

- **URL-based CSV Download**: Downloads CSV files from any public URL
- **Flexible Parsing**: Supports custom delimiters (comma, semicolon, tab, pipe, etc.)
- **Header Detection**: Automatically handles CSVs with or without headers
- **Data Limiting**: Option to limit the number of rows returned
- **Flexible Output**: Returns data in JSON or plain text format
- **Agent-Friendly**: Output is structured for easy consumption by AI agents

## Usage

### Parameters

#### User Parameters
None required - this tool works without user configuration.

#### Tool Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `csv_url` | string | Yes | - | The URL of the CSV file to download and extract |
| `delimiter` | string | No | `,` | The delimiter used in the CSV file (e.g., ',', ';', '\t', '|') |
| `has_header` | boolean | No | `true` | Whether the CSV file has a header row |
| `max_rows` | integer | No | `0` | Maximum number of data rows to return (0 = all rows) |
| `output_format` | string | No | `json` | Output format: `json` or `text` |

### Example Usage

#### Extract data from a CSV file (JSON format):
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "csv_url": "https://example.com/data.csv",
    "delimiter": ",",
    "has_header": true,
    "max_rows": 0,
    "output_format": "json"
  }'
```

#### Extract first 100 rows from a semicolon-delimited CSV:
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "csv_url": "https://example.com/data.csv",
    "delimiter": ";",
    "has_header": true,
    "max_rows": 100,
    "output_format": "json"
  }'
```

#### Extract tab-delimited data without headers (plain text format):
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "csv_url": "https://example.com/data.tsv",
    "delimiter": "\t",
    "has_header": false,
    "output_format": "text"
  }'
```

## Output Format

### JSON Output Structure
```json
{
  "headers": ["Name", "Age", "City", "Country"],
  "data": [
    ["John Doe", "30", "New York", "USA"],
    ["Jane Smith", "25", "London", "UK"],
    ["Bob Johnson", "35", "Toronto", "Canada"]
  ],
  "metadata": {
    "total_rows": 1000,
    "total_columns": 4,
    "rows_returned": 3,
    "has_header": true,
    "delimiter": ","
  }
}
```

### Text Output Format
```
=== CSV Content ===
Total Rows: 1000
Total Columns: 4
Rows Returned: 3
Delimiter: ','

Headers:
Name | Age | City | Country
--------------------------------------------------------------------------------
Data:
John Doe | 30 | New York | USA
Jane Smith | 25 | London | UK
Bob Johnson | 35 | Toronto | Canada
```

## Integration with Agents

This tool is designed to be used by AI agents in workflows where CSV data needs to be processed:

1. **Data Extraction**: Agent calls this tool with a CSV URL
2. **Data Processing**: Agent receives structured data (headers + rows)
3. **Next Steps**: Agent can analyze, transform, or store the extracted data

Example agent workflow:
```python
# Agent receives CSV URL
csv_url = "https://example.com/sales_data.csv"

# Extract data using this tool
result = extract_csv_data(csv_url)

# Agent can now:
# - Analyze the data
# - Calculate statistics
# - Filter and transform rows
# - Store data in databases
# - Generate reports
# - Make decisions based on content
```

## Common Use Cases

### Financial Data
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "csv_url": "https://example.com/stock_prices.csv",
    "delimiter": ",",
    "has_header": true,
    "output_format": "json"
  }'
```

### Log Files
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "csv_url": "https://example.com/server_logs.csv",
    "delimiter": ",",
    "max_rows": 1000,
    "output_format": "json"
  }'
```

### Survey Data
```bash
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "csv_url": "https://example.com/survey_results.csv",
    "delimiter": ";",
    "has_header": true,
    "output_format": "json"
  }'
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
- Malformed CSV files
- Parsing errors
- Empty files

All errors are returned as descriptive error messages.

## Supported Delimiters

- **Comma** (`,`) - Standard CSV
- **Semicolon** (`;`) - Common in European data
- **Tab** (`\t`) - TSV files
- **Pipe** (`|`) - Alternative delimiter
- **Custom** - Any single character

## Limitations

- Works only with public URLs (no authentication support)
- Very large CSV files may consume significant memory
- Encoding is assumed to be UTF-8
- Does not support multi-line cell values with embedded newlines in all cases

## Performance Tips

1. **Large Files**: Use `max_rows` to limit data extraction
2. **Multiple Requests**: Cache downloaded content when possible
3. **Network Issues**: Implement retry logic in your workflow

## Testing

Test with a sample CSV:
```bash
# Create a test CSV
echo "Name,Age,City
John,30,NYC
Jane,25,LA" > /tmp/test.csv

# Upload to a public URL or use a test CSV URL
python tool.py \
  --user-params '{}' \
  --tool-params '{
    "csv_url": "https://your-test-url.com/test.csv",
    "delimiter": ",",
    "has_header": true,
    "output_format": "json"
  }'
```
