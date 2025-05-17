from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum
from datetime import datetime
from uuid import UUID
from app.schemas.base import BaseSchema


class DeliverableStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    JUDGED = "JUDGED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class DeliverableBase(BaseModel):
    """Base schema for Deliverable"""
    task_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    encrypted_content_url: Optional[str] = None
    encryption_keys: Optional[Dict[str, str]] = None  # Judge ID -> Encrypted key
    submission_time: Optional[datetime] = None
    scores: Optional[Dict[str, float]] = None  # Judge ID -> Score
    feedback: Optional[Dict[str, str]] = None  # Judge ID -> Feedback
    status: Optional[DeliverableStatus] = None


class DeliverableCreate(DeliverableBase):
    """Schema for creating a Deliverable"""
    task_id: UUID
    agent_id: UUID
    encrypted_content_url: str
    encryption_keys: Dict[str, str]
    submission_time: datetime = Field(default_factory=datetime.utcnow)
    status: DeliverableStatus = DeliverableStatus.SUBMITTED


class DeliverableUpdate(DeliverableBase):
    """Schema for updating a Deliverable"""
    pass


class Deliverable(DeliverableBase, BaseSchema):
    """Schema for returning a Deliverable"""
    pass