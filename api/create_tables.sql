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

-- Workflow submissions table (for tracking trace_id based submissions)
CREATE TABLE IF NOT EXISTS xtracticai.workflow_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR NOT NULL UNIQUE,
    workflow_url VARCHAR NOT NULL,
    uploaded_file_url VARCHAR NOT NULL,
    file_name VARCHAR(500) NOT NULL,
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
