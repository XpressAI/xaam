from sqlalchemy import Column, String, Float, Integer, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.models.base import BaseModel

class AgentType(enum.Enum):
    WORKER = "WORKER"
    JUDGE = "JUDGE"

class Agent(BaseModel):
    """Agent model representing worker agents and judges"""
    __tablename__ = "agents"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    wallet_address = Column(String, nullable=False, unique=True)
    public_key = Column(String, nullable=False)
    reputation_score = Column(Float, default=0.0, nullable=False)
    completed_tasks = Column(Integer, default=0, nullable=False)
    successful_tasks = Column(Integer, default=0, nullable=False)
    social_profiles = Column(JSON, nullable=True)
    portfolio_url = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type={self.agent_type})>"