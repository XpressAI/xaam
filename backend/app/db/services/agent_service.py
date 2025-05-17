from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.db.models.agent import Agent, AgentType
from app.schemas.agent import AgentCreate, AgentUpdate, SocialProfiles
from app.db.services.base import BaseService


class AgentService(BaseService[Agent, AgentCreate, AgentUpdate]):
    def __init__(self):
        super().__init__(Agent)
    
    async def get_by_wallet_address(self, db: AsyncSession, wallet_address: str) -> Optional[Agent]:
        """
        Get an agent by wallet address
        """
        query = select(self.model).where(self.model.wallet_address == wallet_address)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_type(self, db: AsyncSession, agent_type: AgentType, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        Get agents by type
        """
        query = select(self.model).where(self.model.agent_type == agent_type).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def search_agents(self, db: AsyncSession, search_term: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        Search agents by name or description
        """
        query = select(self.model).where(
            or_(
                self.model.name.ilike(f"%{search_term}%"),
                self.model.description.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_reputation(
        self, 
        db: AsyncSession, 
        agent_id: UUID, 
        task_completed: bool = False, 
        task_successful: bool = False, 
        reputation_delta: float = 0.0
    ) -> Optional[Agent]:
        """
        Update an agent's reputation after task completion
        """
        agent = await self.get(db, agent_id)
        if not agent:
            return None
        
        if task_completed:
            agent.completed_tasks += 1
        
        if task_successful:
            agent.successful_tasks += 1
        
        # Update reputation score (simple weighted average)
        if agent.completed_tasks == 1:
            agent.reputation_score = reputation_delta
        else:
            agent.reputation_score = (agent.reputation_score * (agent.completed_tasks - 1) + reputation_delta) / agent.completed_tasks
        
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return agent


# Create a singleton instance
agent_service = AgentService()