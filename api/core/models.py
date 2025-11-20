"""
Database models for SQLAlchemy
"""
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from api.core.database import Base
class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    agent_config = Column(JSON)
    workflow_steps = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class ETLJob(Base):
    __tablename__ = "etl_jobs"
    
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_name = Column(String, nullable=False)
    source_type = Column(String)
    source_config = Column(JSON)
    destination_type = Column(String)
    destination_config = Column(JSON)
    status = Column(String)
    records_processed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error = Column(Text)


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON)
    collection = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentStats(Base):
    __tablename__ = "agent_stats"
    __table_args__ = {'schema': 'xtracticai'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String, nullable=False)
    agent_type = Column(String)  # workflow, chatbot, etc.
    status = Column(String)  # deployed, stopped, running
    deployment_url = Column(String)
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    last_execution_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MCPServerStats(Base):
    __tablename__ = "mcp_server_stats"
    __table_args__ = {'schema': 'xtracticai'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_name = Column(String, nullable=False)
    server_type = Column(String)  # acled, fewsnet, nifi, etc.
    status = Column(String)  # active, inactive
    endpoint_url = Column(String)
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    failed_calls = Column(Integer, default=0)
    last_call_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FileProcessingStats(Base):
    __tablename__ = "file_processing_stats"
    __table_args__ = {'schema': 'xtracticai'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, csv, json, xml, etc.
    file_size_bytes = Column(Integer)
    processing_status = Column(String)  # processing, completed, failed
    records_extracted = Column(Integer, default=0)
    workflow_id = Column(String)
    workflow_name = Column(String)
    error_message = Column(Text)
    processing_duration_ms = Column(Float)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class WorkflowExecutionStats(Base):
    __tablename__ = "workflow_execution_stats"
    __table_args__ = {'schema': 'xtracticai'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String, nullable=False)
    workflow_name = Column(String, nullable=False)
    execution_type = Column(String)  # manual, scheduled, triggered
    status = Column(String)  # running, success, failed
    input_files_count = Column(Integer, default=0)
    output_records_count = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    agents_used = Column(JSON)  # List of agents involved
    tools_used = Column(JSON)  # List of tools/MCPs used
    duration_ms = Column(Float)
    error_message = Column(Text)
    meta_data = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class WorkflowSubmission(Base):
    __tablename__ = "workflow_submissions"
    __table_args__ = {'schema': 'xtracticai'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id = Column(String, nullable=False, unique=True, index=True)
    workflow_url = Column(String, nullable=False)
    uploaded_file_url = Column(String, nullable=False)
    query = Column(Text)
    status = Column(String, default="submitted")  # submitted, in-progress, completed, failed
    workflow_id = Column(String)
    workflow_name = Column(String)
    execution_id = Column(UUID(as_uuid=True))
    file_id = Column(UUID(as_uuid=True))
    error_message = Column(Text)
    meta_data = Column(JSON)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    last_polled_at = Column(DateTime)
    completed_at = Column(DateTime)
