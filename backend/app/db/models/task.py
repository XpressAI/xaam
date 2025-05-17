from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.models.base import BaseModel
from app.db.database import Base

# Association table for many-to-many relationship between tasks and judges
task_judge_association = Table(
    'task_judge_association',
    Base.metadata,
    Column('task_id', UUID(as_uuid=True), ForeignKey('tasks.id'), primary_key=True),
    Column('judge_id', UUID(as_uuid=True), ForeignKey('agents.id'), primary_key=True)
)

class TaskStatus(enum.Enum):
    CREATED = "CREATED"
    STAKED = "STAKED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    JUDGED = "JUDGED"
    COMPLETED = "COMPLETED"

class Task(BaseModel):
    """Task model representing NFT tasks with encrypted payload links"""
    __tablename__ = "tasks"
    
    nft_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    encrypted_payload_url = Column(String, nullable=False)
    encryption_key = Column(String, nullable=True)  # Encrypted with worker's public key
    creator_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.CREATED, nullable=False)
    deadline = Column(DateTime, nullable=False)
    reward_amount = Column(Float, nullable=False)
    reward_currency = Column(String, default="USDC", nullable=False)
    
    # Relationships
    creator = relationship("Agent", foreign_keys=[creator_id], backref="created_tasks")
    judges = relationship("Agent", secondary=task_judge_association, backref="judged_tasks")
    deliverables = relationship("Deliverable", back_populates="task")
    stakes = relationship("Stake", back_populates="task")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status={self.status})>"