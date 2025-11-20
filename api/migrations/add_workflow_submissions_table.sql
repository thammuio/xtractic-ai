-- Migration: Add workflow_submissions table
-- Description: Tracks workflow submissions with trace_id for status polling

CREATE TABLE IF NOT EXISTS xtracticai.workflow_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR NOT NULL UNIQUE,
    workflow_url VARCHAR NOT NULL,
    uploaded_file_url VARCHAR NOT NULL,
    query TEXT,
    status VARCHAR DEFAULT 'submitted',
    workflow_id VARCHAR,
    workflow_name VARCHAR,
    execution_id UUID,
    file_id UUID,
    error_message TEXT,
    meta_data JSONB,
    submitted_at TIMESTAMP DEFAULT NOW(),
    last_polled_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create index on trace_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_workflow_submissions_trace_id 
ON xtracticai.workflow_submissions(trace_id);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_workflow_submissions_status 
ON xtracticai.workflow_submissions(status);

-- Create index on submitted_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_workflow_submissions_submitted_at 
ON xtracticai.workflow_submissions(submitted_at DESC);

-- Add comments
COMMENT ON TABLE xtracticai.workflow_submissions IS 'Tracks workflow submissions to Agent Studio with trace_id for status polling';
COMMENT ON COLUMN xtracticai.workflow_submissions.trace_id IS 'Unique trace identifier returned by workflow submission';
COMMENT ON COLUMN xtracticai.workflow_submissions.status IS 'Current status: submitted, in-progress, completed, failed';
COMMENT ON COLUMN xtracticai.workflow_submissions.last_polled_at IS 'Last time status was checked via events API';
