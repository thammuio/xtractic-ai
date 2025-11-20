# 🚀 Workflow API - Quick Start

This API enables your frontend to interact with deployed Cloudera AI workflows for PDF processing.

## 📋 What's Been Created

1. **API Endpoints** (`/api/workflows/deployed/`)
   - `POST /kickoff` - Start workflow with PDF URL
   - `GET /events` - Get workflow results by trace_id

2. **Utilities** (`utils/cloudera_utils.py`)
   - Cloudera environment variable management
   - CML API client helpers
   - Application setup utilities

3. **Configuration** (`.env.example`)
   - All required Cloudera environment variables
   - Workflow endpoint configuration

4. **Documentation**
   - `WORKFLOW_API.md` - Complete API reference
   - `CLOUDERA_SETUP.md` - Detailed setup guide

5. **Testing** (`test_workflow.py`)
   - Automated test suite for workflow API

## 🎯 Quick Start

### 1. Configure Environment

```bash
cd api
cp .env.example .env
```

Edit `.env` and add your Cloudera credentials:

```env
# Required
CDSW_DOMAIN=ml-xxxxx.cloudera.site
CDSW_APIV2_KEY=your_api_key
CDSW_PROJECT_ID=your_project_id
DEPLOYED_WORKFLOW_URL=https://workflow-xxxxx.cloudera.site
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API

**Option A: Using the start script (recommended)**
```bash
./start.sh
```

**Option B: Manual start**
```bash
python main.py
```

The API will run on `http://localhost:9000`

### 4. Test the Integration

```bash
# Basic tests (no workflow execution)
python test_workflow.py

# Full tests with workflow execution
python test_workflow.py --pdf-url "https://example.com/sample.pdf"
```

## 📡 API Usage

### From Frontend (React/JavaScript)

```javascript
// Start workflow
const response = await fetch('http://localhost:9000/api/workflows/deployed/kickoff', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pdf_url: 'https://example.com/doc.pdf' })
});
const { trace_id } = await response.json();

// Poll for results
const checkEvents = async () => {
  const res = await fetch(
    `http://localhost:9000/api/workflows/deployed/events?trace_id=${trace_id}`
  );
  const data = await res.json();
  
  if (data.events?.success) {
    console.log('Complete!', data.events);
    return data.events;
  }
  
  // Continue polling
  setTimeout(checkEvents, 2000);
};

checkEvents();
```

### From Python

```python
import requests
import time

# Start workflow
response = requests.post(
    'http://localhost:9000/api/workflows/deployed/kickoff',
    json={'pdf_url': 'https://example.com/doc.pdf'}
)
trace_id = response.json()['trace_id']

# Wait for completion
while True:
    response = requests.get(
        'http://localhost:9000/api/workflows/deployed/events',
        params={'trace_id': trace_id}
    )
    data = response.json()
    
    if data['events'].get('success'):
        print('Results:', data['events'])
        break
    
    time.sleep(2)
```

### Using cURL

```bash
# Start workflow
TRACE_ID=$(curl -X POST "http://localhost:9000/api/workflows/deployed/kickoff" \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://example.com/doc.pdf"}' | jq -r '.trace_id')

# Get results
curl "http://localhost:9000/api/workflows/deployed/events?trace_id=$TRACE_ID"
```

## 📊 Expected Response

When the workflow completes, you'll receive:

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

## 🔍 Additional Endpoints

### Check Configuration

```bash
# Get environment status
curl http://localhost:9000/api/workflows/cloudera/env

# Check credentials
curl http://localhost:9000/api/workflows/cloudera/credentials
```

### Setup Applications

```bash
curl -X POST "http://localhost:9000/api/workflows/cloudera/setup-apps" \
  -H "Content-Type: application/json" \
  -d '{
    "api_subdomain": "xtracticai-api",
    "ui_subdomain": "xtracticai-ui"
  }'
```

## 📚 Documentation

- **API Reference**: See `WORKFLOW_API.md` for complete endpoint documentation
- **Setup Guide**: See `CLOUDERA_SETUP.md` for detailed configuration instructions
- **Swagger Docs**: Visit `http://localhost:9000/docs` when API is running

## 🐛 Troubleshooting

### API won't start
```bash
# Check environment variables
python -c "from utils.cloudera_utils import get_all_cloudera_env_vars; print(get_all_cloudera_env_vars())"

# Verify dependencies
pip install -r requirements.txt
```

### Workflow fails to start
1. Verify `DEPLOYED_WORKFLOW_URL` is correct
2. Check `CDSW_APIV2_KEY` has permissions
3. Ensure workflow is deployed and running in CML

### Can't get events
1. Verify the `trace_id` is correct
2. Workflow may still be processing (keep polling)
3. Check workflow logs in CML for errors

## 🔗 Integration with Frontend

Your frontend should:

1. **Call `/kickoff`** with PDF URL when user uploads/submits
2. **Store `trace_id`** from response
3. **Poll `/events`** every 2-3 seconds with the trace_id
4. **Display results** when `events.success` is `true`
5. **Handle errors** if workflow fails

## 📁 File Structure

```
api/
├── main.py                    # FastAPI application
├── start.sh                   # Quick start script
├── test_workflow.py           # Test suite
├── .env.example               # Environment template
├── WORKFLOW_API.md            # API documentation
├── CLOUDERA_SETUP.md          # Setup guide
├── README_WORKFLOW.md         # This file
├── routers/
│   └── workflows.py           # Workflow endpoints
├── services/
│   └── cloudera_service.py    # Cloudera integration
└── utils/
    └── cloudera_utils.py      # Helper utilities
```

## ✅ Next Steps

1. ✓ Configure `.env` with your Cloudera credentials
2. ✓ Run `./start.sh` to start the API
3. ✓ Test with `python test_workflow.py --pdf-url <url>`
4. ✓ Integrate with your frontend
5. ✓ Deploy to production

## 💡 Tips

- Use environment variables for all sensitive data
- Poll events every 2-3 seconds (not too frequently)
- Implement timeout handling (workflows may take time)
- Show progress indicators in your UI
- Log trace_id for debugging

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review `CLOUDERA_SETUP.md` for detailed configuration
3. Run tests: `python test_workflow.py`
4. Check API logs for errors
5. Verify workflow is running in CML

Happy coding! 🎉
