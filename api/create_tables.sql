-- Database Schema Creation Script for Xtractic AI
-- This script creates all necessary tables and indexes for the application
-- Run this script manually before starting the application

-- Create schema
CREATE SCHEMA IF NOT EXISTS xtracticai;

-- File processing stats table
CREATE TABLE IF NOT EXISTS xtracticai.file_processing_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size_bytes BIGINT,
    processing_status VARCHAR(50),
    records_extracted INTEGER DEFAULT 0,
    workflow_id VARCHAR(255),
    workflow_name VARCHAR(255),
    error_message TEXT,
    processing_duration_ms FLOAT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_stats_type ON xtracticai.file_processing_stats(file_type);
CREATE INDEX IF NOT EXISTS idx_file_stats_status ON xtracticai.file_processing_stats(processing_status);
CREATE INDEX IF NOT EXISTS idx_file_stats_uploaded ON xtracticai.file_processing_stats(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_file_stats_name ON xtracticai.file_processing_stats(file_name);

COMMENT ON TABLE xtracticai.file_processing_stats IS 'Tracks file uploads and processing statistics';
COMMENT ON COLUMN xtracticai.file_processing_stats.file_type IS 'File type: pdf, csv, json, xml, etc.';
COMMENT ON COLUMN xtracticai.file_processing_stats.processing_status IS 'Status: processing, completed, failed';

-- Workflow execution stats table
CREATE TABLE IF NOT EXISTS xtracticai.workflow_execution_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id VARCHAR(255) NOT NULL,
    workflow_name VARCHAR(255) NOT NULL,
    execution_type VARCHAR(50),
    status VARCHAR(50),
    input_files_count INTEGER DEFAULT 0,
    output_records_count INTEGER DEFAULT 0,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    agents_used JSONB,
    tools_used JSONB,
    duration_ms FLOAT,
    error_message TEXT,
    metadata JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow_stats_id ON xtracticai.workflow_execution_stats(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_stats_status ON xtracticai.workflow_execution_stats(status);
CREATE INDEX IF NOT EXISTS idx_workflow_stats_started ON xtracticai.workflow_execution_stats(started_at DESC);

COMMENT ON TABLE xtracticai.workflow_execution_stats IS 'Tracks workflow execution history and performance';
COMMENT ON COLUMN xtracticai.workflow_execution_stats.execution_type IS 'Type: manual, scheduled, triggered';
COMMENT ON COLUMN xtracticai.workflow_execution_stats.status IS 'Status: running, success, failed';

-- Workflow submissions table (for tracking trace_id based submissions)
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
    metadata JSONB,
    submitted_at TIMESTAMP DEFAULT NOW(),
    last_polled_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow_submissions_trace_id ON xtracticai.workflow_submissions(trace_id);
CREATE INDEX IF NOT EXISTS idx_workflow_submissions_status ON xtracticai.workflow_submissions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_submissions_submitted_at ON xtracticai.workflow_submissions(submitted_at DESC);

COMMENT ON TABLE xtracticai.workflow_submissions IS 'Tracks workflow submissions to Agent Studio with trace_id for status polling';
COMMENT ON COLUMN xtracticai.workflow_submissions.trace_id IS 'Unique trace identifier returned by workflow submission';
COMMENT ON COLUMN xtracticai.workflow_submissions.status IS 'Current status: submitted, in-progress, completed, failed';
COMMENT ON COLUMN xtracticai.workflow_submissions.last_polled_at IS 'Last time status was checked via events API';
