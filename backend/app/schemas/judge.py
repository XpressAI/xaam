from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.agent import Agent, AgentCreate, AgentUpdate, AgentType


class JudgeBase(BaseModel):
    """Base schema for Judge"""
    specialization: Optional[str] = None


class JudgeCreate(JudgeBase):
    """Schema for creating a Judge"""
    name: str
    description: str
    wallet_address: str
    public_key: str
    specialization: str


class JudgeUpdate(JudgeBase):
    """Schema for updating a Judge"""
    name: Optional[str] = None
    description: Optional[str] = None
    public_key: Optional[str] = None


class Judge(JudgeBase, Agent):
    """Schema for returning a Judge"""
    agent_type: AgentType = AgentType.JUDGE