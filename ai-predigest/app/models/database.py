"""
SQLAlchemy Database Models for Predictions
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, 
    JSON, Enum, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class PredictionStatus(str, PyEnum):
    """Status enum for predictions"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Prediction(Base):
    """Main prediction table"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(String(64), unique=True, nullable=False, index=True)
    input_id = Column(String(64), nullable=False)
    
    # Person 1 details
    name = Column(String(100), nullable=False)
    sex = Column(String(10), nullable=False)
    dob = Column(String(20), nullable=False)
    tob = Column(String(10), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    timezone = Column(String(20), default="UTC+5:30")
    
    # Domain and subtopics
    domain = Column(String(50), nullable=False)
    subtopic = Column(String(200), nullable=False)
    questions = Column(JSON, default=list)
    
    # Person 2 details (for compatibility analysis)
    person2_name = Column(String(100), nullable=True)
    person2_sex = Column(String(10), nullable=True)
    person2_dob = Column(String(20), nullable=True)
    person2_tob = Column(String(10), nullable=True)
    person2_lat = Column(Float, nullable=True)
    person2_lon = Column(Float, nullable=True)
    person2_timezone = Column(String(20), nullable=True)
    
    # Status and progress
    status = Column(Enum(PredictionStatus), default=PredictionStatus.PENDING)
    progress = Column(Integer, default=0)
    progress_message = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Result data
    result = Column(JSON, nullable=True)
    
    # Metadata
    source = Column(String(50), default="api")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    events = relationship("PredictionEvent", back_populates="prediction", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Prediction(response_id={self.response_id}, status={self.status})>"


class PredictionEvent(Base):
    """Event log for prediction progress tracking"""
    __tablename__ = "prediction_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(String(64), ForeignKey("predictions.response_id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    prediction = relationship("Prediction", back_populates="events")
    
    def __repr__(self):
        return f"<PredictionEvent(response_id={self.response_id}, type={self.event_type})>"
