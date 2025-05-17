from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict
from enum import Enum
from app.schemas.base import BaseSchema


class AgentType(str, Enum):
    WORKER = "WORKER"
    JUDGE = "JUDGE"


class SocialProfiles(BaseModel):
    """Schema for social profiles"""
    github: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None


class AgentBase(BaseModel):
    """Base schema for Agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[AgentType] = None
    wallet_address: Optional[str] = None
    public_key: Optional[str] = None
    reputation_score: Optional[float] = 0.0
    completed_tasks: Optional[int] = 0
    successful_tasks: Optional[int] = 0
    social_profiles: Optional[SocialProfiles] = None
    portfolio_url: Optional[str] = None


class AgentCreate(AgentBase):
    """Schema for creating an Agent"""
    name: str
    description: str
    agent_type: AgentType
    wallet_address: str
    public_key: str


class AgentUpdate(AgentBase):
    """Schema for updating an Agent"""
    pass


class Agent(AgentBase, BaseSchema):
    """Schema for returning an Agent"""
    pass