from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
from uuid import UUID
from app.schemas.base import BaseSchema


class StakeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    FORFEITED = "FORFEITED"


class StakeBase(BaseModel):
    """Base schema for Stake"""
    task_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    amount: Optional[float] = None
    status: Optional[StakeStatus] = None
    staked_at: Optional[datetime] = None
    released_at: Optional[datetime] = None


class StakeCreate(StakeBase):
    """Schema for creating a Stake"""
    task_id: UUID
    agent_id: UUID
    amount: float
    status: StakeStatus = StakeStatus.ACTIVE
    staked_at: datetime = Field(default_factory=datetime.utcnow)


class StakeUpdate(StakeBase):
    """Schema for updating a Stake"""
    status: Optional[StakeStatus] = None
    released_at: Optional[datetime] = None


class Stake(StakeBase, BaseSchema):
    """Schema for returning a Stake"""
    pass