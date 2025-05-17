from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
from uuid import UUID
from app.schemas.base import BaseSchema


class TaskStatus(str, Enum):
    CREATED = "CREATED"
    STAKED = "STAKED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    JUDGED = "JUDGED"
    COMPLETED = "COMPLETED"


class TaskBase(BaseModel):
    """Base schema for Task"""
    nft_id: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    encrypted_payload_url: Optional[str] = None
    encryption_key: Optional[str] = None
    creator_id: Optional[UUID] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None
    reward_amount: Optional[float] = None
    reward_currency: Optional[str] = "USDC"
    judges: Optional[List[UUID]] = None


class TaskCreate(TaskBase):
    """Schema for creating a Task"""
    title: str
    summary: str
    encrypted_payload_url: str
    creator_id: UUID
    deadline: datetime
    reward_amount: float
    judges: List[UUID]


class TaskUpdate(TaskBase):
    """Schema for updating a Task"""
    pass


class Task(TaskBase, BaseSchema):
    """Schema for returning a Task"""
    pass