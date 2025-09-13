from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Block(Base):
    __tablename__ = "blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_prompt = Column(Text, nullable=False)
    title = Column(String, nullable=True)
    current_version = Column(Integer, default=1)
    refresh_interval = Column(Integer, default=3600)  # seconds
    layout_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(String, default="active")  # active, error, disabled
    
    # Relationships
    versions = relationship("BlockVersion", back_populates="block", cascade="all, delete-orphan")
    data_cache = relationship("BlockData", back_populates="block", cascade="all, delete-orphan")
    execution_logs = relationship("ExecutionLog", back_populates="block", cascade="all, delete-orphan")


class BlockVersion(Base):
    __tablename__ = "block_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    version = Column(Integer, nullable=False)
    backend_code = Column(Text, nullable=True)
    frontend_code = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="active")  # active, deprecated, failed
    
    # Relationships
    block = relationship("Block", back_populates="versions")


class BlockData(Base):
    __tablename__ = "block_data"
    
    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    data = Column(JSON, nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    block = relationship("Block", back_populates="data_cache")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    version = Column(Integer, nullable=False)
    execution_type = Column(String, nullable=False)  # fetch, process, heal
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    block = relationship("Block", back_populates="execution_logs")