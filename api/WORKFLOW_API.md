# Deployed Workflow API Documentation

This document describes the API endpoints for interacting with the deployed Cloudera workflow agent.

## Base URL

```
http://localhost:8000/api/workflows
```

## Authentication

All requests require the `CDSW_APIV2_KEY` to be configured in your environment variables.

## Endpoints

### 1. Start Workflow Execution (Kickoff)

Initiates a new workflow execution with a PDF URL.

**Endpoint:** `POST /deployed/kickoff`

**Request Body:**
```json
{
  "pdf_url": "https://example.com/document.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "trace_id": "abc123-def456-ghi789",
  "message": "Workflow started successfully"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/workflows/deployed/kickoff" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/sample.pdf"
  }'
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/workflows/deployed/kickoff"
payload = {
    "pdf_url": "https://example.com/sample.pdf"
}

response = requests.post(url, json=payload)
result = response.json()
print(f"Trace ID: {result['trace_id']}")
```

---

### 2. Get Workflow Events

Retrieves real-time events and progress updates for a workflow execution.

**Endpoint:** `GET /deployed/events`

**Query Parameters:**
- `trace_id` (required): The trace ID returned from the kickoff endpoint

**Response:**
```json
{
  "success": true,
  "trace_id": "abc123-def456-ghi789",
  "events": {
    "success": true,
    "table_created": false,
    "table_name": "xtractic-ai.employee_records",
    "rows_inserted": 20,
    "columns": [
      "EmployeeID",
      "FirstName",
      "LastName",
      "Department",
      "Salary"
    ],
    "message": "Successfully inserted 20 row(s) into xtractic-ai.employee_records"
  }
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/workflows/deployed/events?trace_id=abc123-def456-ghi789" \
  -H "Accept: application/json"
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/workflows/deployed/events"
params = {
    "trace_id": "abc123-def456-ghi789"
}

response = requests.get(url, params=params)
events = response.json()
print(f"Rows inserted: {events['events']['rows_inserted']}")
print(f"Table name: {events['events']['table_name']}")
```

---

## Complete Workflow Example

### Full End-to-End Flow

```python
import requests
import time

# 1. Start the workflow
kickoff_url = "http://localhost:8000/api/workflows/deployed/kickoff"
kickoff_payload = {
    "pdf_url": "https://example.com/employee-data.pdf"
}

print("Starting workflow...")
kickoff_response = requests.post(kickoff_url, json=kickoff_payload)
kickoff_result = kickoff_response.json()

if kickoff_result["success"]:
    trace_id = kickoff_result["trace_id"]
    print(f"✓ Workflow started with trace ID: {trace_id}")
    
    # 2. Poll for events
    events_url = "http://localhost:8000/api/workflows/deployed/events"
    max_attempts = 30
    attempt = 0
    
    print("\nWaiting for workflow to complete...")
    while attempt < max_attempts:
        time.sleep(2)  # Wait 2 seconds between polls
        
        events_response = requests.get(
            events_url,
            params={"trace_id": trace_id}
        )
        events_result = events_response.json()
        
        if events_result["success"] and events_result.get("events"):
            events = events_result["events"]
            
            # Check if workflow completed
            if events.get("success"):
                print("\n✓ Workflow completed successfully!")
                print(f"  Table: {events.get('table_name')}")
                print(f"  Rows inserted: {events.get('rows_inserted')}")
                print(f"  Columns: {', '.join(events.get('columns', []))}")
                print(f"  Message: {events.get('message')}")
                break
        
        attempt += 1
        print(f"  Attempt {attempt}/{max_attempts}...")
    
    if attempt >= max_attempts:
        print("\n✗ Workflow did not complete within expected time")
else:
    print("✗ Failed to start workflow")
```

---

## Frontend Integration

### React Example with Axios

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/workflows';

// Start workflow
export const startWorkflow = async (pdfUrl) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/deployed/kickoff`, {
      pdf_url: pdfUrl
    });
    return response.data;
  } catch (error) {
    console.error('Error starting workflow:', error);
    throw error;
  }
};

// Get workflow events
export const getWorkflowEvents = async (traceId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/deployed/events`, {
      params: { trace_id: traceId }
    });
    return response.data;
  } catch (error) {
    console.error('Error getting workflow events:', error);
    throw error;
  }
};

// React Component Example
import React, { useState } from 'react';

function WorkflowExecutor() {
  const [pdfUrl, setPdfUrl] = useState('');
  const [traceId, setTraceId] = useState(null);
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleStartWorkflow = async () => {
    setLoading(true);
    try {
      const result = await startWorkflow(pdfUrl);
      setTraceId(result.trace_id);
      
      // Start polling for events
      pollEvents(result.trace_id);
    } catch (error) {
      alert('Failed to start workflow');
    } finally {
      setLoading(false);
    }
  };

  const pollEvents = async (id) => {
    const interval = setInterval(async () => {
      try {
        const result = await getWorkflowEvents(id);
        setEvents(result.events);
        
        // Stop polling if workflow completed
        if (result.events?.success) {
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Error polling events:', error);
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <div>
      <h2>Workflow Executor</h2>
      <input
        type="text"
        value={pdfUrl}
        onChange={(e) => setPdfUrl(e.target.value)}
        placeholder="Enter PDF URL"
      />
      <button onClick={handleStartWorkflow} disabled={loading}>
        {loading ? 'Starting...' : 'Start Workflow'}
      </button>
      
      {traceId && (
        <div>
          <p>Trace ID: {traceId}</p>
        </div>
      )}
      
      {events && (
        <div>
          <h3>Results</h3>
          <p>Status: {events.success ? 'Success' : 'Failed'}</p>
          <p>Table: {events.table_name}</p>
          <p>Rows Inserted: {events.rows_inserted}</p>
          <p>Columns: {events.columns?.join(', ')}</p>
        </div>
      )}
    </div>
  );
}

export default WorkflowExecutor;
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Error Codes:**
- `400`: Bad Request - Invalid input parameters
- `401`: Unauthorized - Missing or invalid API key
- `404`: Not Found - Trace ID not found
- `500`: Internal Server Error - Workflow execution failed

---

## Environment Variables

Make sure to set these environment variables:

```bash
# Required for deployed workflow
DEPLOYED_WORKFLOW_URL=https://workflow-0421b0de-eec0-4dab-9a72-00e31453cf14.ml-d248e68a-04a.se-sandb.a465-9q4k.cloudera.site
CDSW_APIV2_KEY=your_api_key_here
```

---

## Response Schema

### Workflow Result Schema

The events endpoint returns a result with the following structure:

```typescript
interface WorkflowResult {
  success: boolean;
  table_created: boolean;
  table_name: string;
  rows_inserted: number;
  columns: string[];
  message: string;
}
```

---

## Testing

### Test with cURL

1. Start a workflow:
```bash
curl -X POST "http://localhost:8000/api/workflows/deployed/kickoff" \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://example.com/test.pdf"}'
```

2. Get the trace_id from the response, then query events:
```bash
curl -X GET "http://localhost:8000/api/workflows/deployed/events?trace_id=YOUR_TRACE_ID" \
  -H "Accept: application/json"
```

### Test with Python

```bash
cd api
python -c "
import requests
import json

# Start workflow
resp = requests.post('http://localhost:8000/api/workflows/deployed/kickoff', 
                     json={'pdf_url': 'https://example.com/test.pdf'})
print('Kickoff:', json.dumps(resp.json(), indent=2))

# Get events (use trace_id from above)
trace_id = resp.json()['trace_id']
resp = requests.get(f'http://localhost:8000/api/workflows/deployed/events?trace_id={trace_id}')
print('Events:', json.dumps(resp.json(), indent=2))
"
```

---

## Support

For issues or questions, please refer to the main API documentation or contact the development team.
