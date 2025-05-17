from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.models.base import BaseModel

class DeliverableStatus(enum.Enum):
    SUBMITTED = "SUBMITTED"
    JUDGED = "JUDGED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class Deliverable(BaseModel):
    """Deliverable model representing submissions from agents"""
    __tablename__ = "deliverables"
    
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    encrypted_content_url = Column(String, nullable=False)
    encryption_keys = Column(JSON, nullable=True)  # Map of judge ID -> encrypted key
    submission_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    scores = Column(JSON, nullable=True)  # Map of judge ID -> score
    feedback = Column(JSON, nullable=True)  # Map of judge ID -> feedback
    status = Column(Enum(DeliverableStatus), default=DeliverableStatus.SUBMITTED, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="deliverables")
    agent = relationship("Agent", backref="deliverables")
    
    def __repr__(self):
        return f"<Deliverable(id={self.id}, task_id={self.task_id}, agent_id={self.agent_id}, status={self.status})>"