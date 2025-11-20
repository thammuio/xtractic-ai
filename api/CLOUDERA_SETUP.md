# Cloudera AI Workflow Integration - Setup Guide

This guide will help you set up and use the Cloudera AI workflow integration with the Xtractic AI API.

## Prerequisites

1. Access to a Cloudera Machine Learning (CML) workspace
2. A deployed workflow in CML
3. Cloudera API v2 key (CDSW_APIV2_KEY)
4. Python 3.8+

## Installation

1. Install the required dependencies:

```bash
cd api
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

3. Configure your environment variables in `.env`:

```env
# Cloudera Workbench - Required for deployed workflows
CDSW_DOMAIN=your-workspace.cloudera.site
CDSW_APIV2_KEY=your_api_key_here
CDSW_PROJECT_ID=your_project_id
CDSW_APP_PORT=9000

# Deployed Workflow Settings
DEPLOYED_WORKFLOW_URL=https://workflow-xxxxx.ml-xxxxx.cloudera.site
```

## Getting Your Cloudera Credentials

### 1. Get CDSW_DOMAIN

Your CDSW_DOMAIN is the base domain of your Cloudera workspace. It looks like:
```
ml-d248e68a-04a.se-sandb.a465-9q4k.cloudera.site
```

You can find it in the URL when you access your CML workspace.

### 2. Get CDSW_APIV2_KEY

1. Log in to your CML workspace
2. Click on your user icon (top right)
3. Go to "User Settings"
4. Navigate to "API Keys"
5. Click "Create API Key"
6. Copy the generated key

### 3. Get CDSW_PROJECT_ID

1. Open your project in CML
2. Click on "Project Settings"
3. The Project ID is displayed in the settings page

### 4. Get DEPLOYED_WORKFLOW_URL

1. Deploy your workflow in CML
2. Once deployed, you'll see the workflow endpoint URL
3. It should look like: `https://workflow-{id}.{domain}.cloudera.site`

## Running the API

### Option 1: Local Development

```bash
cd api
python main.py
```

The API will be available at `http://localhost:9000`

### Option 2: Using Uvicorn

```bash
cd api
uvicorn main:create_app --factory --host 0.0.0.0 --port 9000 --reload
```

### Option 3: In Cloudera Workbench

The API is designed to run in CML/CDSW. Simply run:

```bash
python api/main.py
```

The application will automatically use `CDSW_APP_PORT` from the environment.

## API Endpoints

### 1. Start Workflow (Kickoff)

**POST** `/api/workflows/deployed/kickoff`

Start a new workflow execution with a PDF URL.

```bash
curl -X POST "http://localhost:9000/api/workflows/deployed/kickoff" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/document.pdf"
  }'
```

Response:
```json
{
  "success": true,
  "trace_id": "abc123-def456",
  "message": "Workflow started successfully"
}
```

### 2. Get Workflow Events

**GET** `/api/workflows/deployed/events?trace_id={trace_id}`

Get the status and results of a workflow execution.

```bash
curl -X GET "http://localhost:9000/api/workflows/deployed/events?trace_id=abc123-def456"
```

Response:
```json
{
  "success": true,
  "trace_id": "abc123-def456",
  "events": {
    "success": true,
    "table_created": false,
    "table_name": "xtractic-ai.employee_records",
    "rows_inserted": 20,
    "columns": ["EmployeeID", "FirstName", "LastName", "Department", "Salary"],
    "message": "Successfully inserted 20 row(s) into xtractic-ai.employee_records"
  }
}
```

### 3. Get Cloudera Environment Info

**GET** `/api/workflows/cloudera/env`

Get information about configured Cloudera environment variables (for debugging).

```bash
curl -X GET "http://localhost:9000/api/workflows/cloudera/env"
```

### 4. Get Cloudera Credentials Status

**GET** `/api/workflows/cloudera/credentials`

Check if Cloudera credentials are properly configured.

```bash
curl -X GET "http://localhost:9000/api/workflows/cloudera/credentials"
```

### 5. Setup Cloudera Applications

**POST** `/api/workflows/cloudera/setup-apps`

Configure and restart Cloudera applications with custom subdomains.

```bash
curl -X POST "http://localhost:9000/api/workflows/cloudera/setup-apps" \
  -H "Content-Type: application/json" \
  -d '{
    "api_subdomain": "xtracticai-api",
    "ui_subdomain": "xtracticai-ui"
  }'
```

## Python Client Example

```python
import requests
import time

class WorkflowClient:
    def __init__(self, base_url="http://localhost:9000"):
        self.base_url = base_url
        
    def start_workflow(self, pdf_url):
        """Start a workflow execution"""
        response = requests.post(
            f"{self.base_url}/api/workflows/deployed/kickoff",
            json={"pdf_url": pdf_url}
        )
        response.raise_for_status()
        return response.json()
    
    def get_events(self, trace_id):
        """Get workflow events"""
        response = requests.get(
            f"{self.base_url}/api/workflows/deployed/events",
            params={"trace_id": trace_id}
        )
        response.raise_for_status()
        return response.json()
    
    def execute_and_wait(self, pdf_url, max_wait=60, poll_interval=2):
        """Execute workflow and wait for completion"""
        # Start workflow
        result = self.start_workflow(pdf_url)
        trace_id = result["trace_id"]
        print(f"Workflow started: {trace_id}")
        
        # Poll for completion
        elapsed = 0
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            events = self.get_events(trace_id)
            if events.get("events", {}).get("success"):
                print(f"Workflow completed!")
                return events
            
            print(f"Waiting... ({elapsed}s)")
        
        raise TimeoutError(f"Workflow did not complete within {max_wait}s")

# Usage
client = WorkflowClient()

# Execute workflow
result = client.execute_and_wait(
    pdf_url="https://example.com/sample.pdf"
)

print(f"Table: {result['events']['table_name']}")
print(f"Rows: {result['events']['rows_inserted']}")
print(f"Columns: {result['events']['columns']}")
```

## Frontend Integration (React)

```javascript
// api/workflowApi.js
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:9000';

export const workflowApi = {
  async kickoff(pdfUrl) {
    const response = await axios.post(
      `${API_BASE}/api/workflows/deployed/kickoff`,
      { pdf_url: pdfUrl }
    );
    return response.data;
  },

  async getEvents(traceId) {
    const response = await axios.get(
      `${API_BASE}/api/workflows/deployed/events`,
      { params: { trace_id: traceId } }
    );
    return response.data;
  },

  async executeAndPoll(pdfUrl, onProgress) {
    const kickoffResult = await this.kickoff(pdfUrl);
    const traceId = kickoffResult.trace_id;
    
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const events = await this.getEvents(traceId);
          
          if (onProgress) {
            onProgress(events);
          }
          
          if (events.events?.success) {
            clearInterval(interval);
            resolve(events);
          }
        } catch (error) {
          clearInterval(interval);
          reject(error);
        }
      }, 2000);
    });
  }
};

// Component example
import React, { useState } from 'react';
import { workflowApi } from './api/workflowApi';

function WorkflowExecutor() {
  const [pdfUrl, setPdfUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState('');

  const handleExecute = async () => {
    setLoading(true);
    setProgress('Starting workflow...');
    
    try {
      const result = await workflowApi.executeAndPoll(
        pdfUrl,
        (events) => {
          setProgress('Processing...');
        }
      );
      
      setResult(result.events);
      setProgress('Complete!');
    } catch (error) {
      console.error('Error:', error);
      setProgress('Error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={pdfUrl}
        onChange={(e) => setPdfUrl(e.target.value)}
        placeholder="PDF URL"
        disabled={loading}
      />
      <button onClick={handleExecute} disabled={loading}>
        {loading ? 'Processing...' : 'Execute Workflow'}
      </button>
      
      {progress && <p>{progress}</p>}
      
      {result && (
        <div>
          <h3>Results</h3>
          <p>Table: {result.table_name}</p>
          <p>Rows Inserted: {result.rows_inserted}</p>
          <p>Columns: {result.columns.join(', ')}</p>
        </div>
      )}
    </div>
  );
}
```

## Troubleshooting

### Error: "Environment variable X not set"

Make sure all required environment variables are set in your `.env` file:
- CDSW_DOMAIN
- CDSW_APIV2_KEY
- CDSW_PROJECT_ID

### Error: "Failed to start workflow"

1. Check that your workflow is deployed and running in CML
2. Verify the DEPLOYED_WORKFLOW_URL is correct
3. Ensure your CDSW_APIV2_KEY has the necessary permissions

### Error: "API error occurred"

1. Check that your API key is valid
2. Verify you have access to the project
3. Check CML logs for more details

## Testing

Run the test suite:

```bash
cd api
pytest tests/test_workflows.py -v
```

## API Documentation

Once the API is running, visit:
- Swagger UI: `http://localhost:9000/docs`
- ReDoc: `http://localhost:9000/redoc`

## Support

For more information, see:
- [Cloudera CML Documentation](https://docs.cloudera.com/machine-learning/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Main API docs: `api/README.md`
- Workflow API docs: `api/WORKFLOW_API.md`
