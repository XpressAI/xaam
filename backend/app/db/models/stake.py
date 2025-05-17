from sqlalchemy import Column, Float, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.models.base import BaseModel

class StakeStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    FORFEITED = "FORFEITED"

class Stake(BaseModel):
    """Stake model tracking agent stakes for tasks"""
    __tablename__ = "stakes"
    
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(StakeStatus), default=StakeStatus.ACTIVE, nullable=False)
    staked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    released_at = Column(DateTime, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="stakes")
    agent = relationship("Agent", backref="stakes")
    
    def __repr__(self):
        return f"<Stake(id={self.id}, task_id={self.task_id}, agent_id={self.agent_id}, amount={self.amount}, status={self.status})>"