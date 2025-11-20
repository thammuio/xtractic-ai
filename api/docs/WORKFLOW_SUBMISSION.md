# Workflow Submission and Status Tracking

## Overview
This module provides workflow submission tracking with trace_id-based status polling for Agent Studio workflows.

## Key Changes

### 1. Database Model
Added `WorkflowSubmission` model to track workflow submissions:
- `trace_id`: Unique identifier returned by workflow submission
- `workflow_url`: URL of the deployed workflow
- `uploaded_file_url`: URL of the uploaded file being processed
- `query`: User query for the workflow
- `status`: Current status (submitted, in-progress, completed, failed)
- `submitted_at`, `last_polled_at`, `completed_at`: Timestamps

### 2. API Endpoints

#### POST `/api/workflows/submit`
Submit a workflow to Agent Studio for processing.

**Request:**
```json
{
  "uploaded_file_url": "https://example.com/file.pdf",
  "query": "Extract tables and convert to relational format"
}
```

**Response:**
```json
{
  "success": true,
  "trace_id": "4f591189ef1529525ad5e95d9aef66f3",
  "submission_id": "uuid-here",
  "workflow_url": "https://workflow-xxx.cloudera.site",
  "status": "submitted",
  "submitted_at": "2025-11-20T10:30:00",
  "message": "Workflow submitted successfully"
}
```

#### GET `/api/workflows/{trace_id}/status`
Check the status of a submitted workflow. Poll this endpoint every 5 seconds.

**Response (In Progress):**
```json
{
  "success": true,
  "trace_id": "4f591189ef1529525ad5e95d9aef66f3",
  "status": "in-progress",
  "submitted_at": "2025-11-20T10:30:00",
  "events": [...],
  "message": "Workflow is still in progress"
}
```

**Response (Completed):**
```json
{
  "success": true,
  "trace_id": "4f591189ef1529525ad5e95d9aef66f3",
  "status": "completed",
  "submitted_at": "2025-11-20T10:30:00",
  "completed_at": "2025-11-20T10:35:00",
  "message": "Workflow completed successfully"
}
```

## Status Logic

The status endpoint polls the workflow events API:
```bash
curl -X GET "https://workflow-xxx.cloudera.site/api/workflow/events?trace_id={trace_id}" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $CDSW_APIV2_KEY"
```

- **If events are returned** (HTTP 200): Workflow is **in-progress**
- **If no response/error** (HTTP 400+): Workflow is **completed**

## Database Migration

Run the migration to create the table:
```sql
-- See: api/migrations/add_workflow_submissions_table.sql
```

Or using SQLAlchemy:
```python
from api.core.database import Base, rag_engine
from api.core.models import WorkflowSubmission

# Create table
async with rag_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

## Usage Example

### Submit Workflow
```javascript
const response = await fetch('/api/workflows/submit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    uploaded_file_url: 'https://example.com/document.pdf',
    query: 'Extract and analyze data'
  })
});

const { trace_id } = await response.json();
```

### Poll Status (Every 5 seconds)
```javascript
const pollStatus = async (traceId) => {
  const response = await fetch(`/api/workflows/${traceId}/status`);
  const status = await response.json();
  
  if (status.status === 'in-progress') {
    // Continue polling
    setTimeout(() => pollStatus(traceId), 5000);
  } else if (status.status === 'completed') {
    // Workflow completed
    console.log('Workflow completed!');
  } else if (status.status === 'failed') {
    // Handle error
    console.error('Workflow failed:', status.error_message);
  }
};

pollStatus(trace_id);
```

## Notes

- Removed file stats tracking from submit_workflow (now handled by agent itself)
- All submission data stored in `workflow_submissions` table
- Status polling uses the workflow events API as specified
- Frontend should poll every 5 seconds until status is completed/failed
