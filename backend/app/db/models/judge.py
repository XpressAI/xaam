from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db.models.agent import Agent, AgentType

class Judge(Agent):
    """Judge model extending Agent with judge-specific attributes"""
    __tablename__ = "judges"
    
    id = Column(String, primary_key=True)
    specialization = Column(String, nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': AgentType.JUDGE,
        'inherit_condition': id == Agent.id
    }
    
    def __repr__(self):
        return f"<Judge(id={self.id}, name='{self.name}', specialization='{self.specialization}')>"