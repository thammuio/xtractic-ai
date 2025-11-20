"""
Database models for SQLAlchemy
"""
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer
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
    metadata = Column(JSON)
    collection = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
