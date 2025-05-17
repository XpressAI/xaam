from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.db.models.agent import Agent, AgentType
from app.db.models.judge import Judge
from app.schemas.judge import JudgeCreate, JudgeUpdate
from app.db.services.base import BaseService
from app.db.services.agent_service import agent_service


class JudgeService(BaseService[Judge, JudgeCreate, JudgeUpdate]):
    def __init__(self):
        super().__init__(Judge)
    
    async def create_judge(self, db: AsyncSession, obj_in: JudgeCreate) -> Judge:
        """
        Create a new judge (which is a specialized agent)
        """
        # First create the agent
        agent_data = {
            "name": obj_in.name,
            "description": obj_in.description,
            "agent_type": AgentType.JUDGE,
            "wallet_address": obj_in.wallet_address,
            "public_key": obj_in.public_key,
            "reputation_score": 0.0,
            "completed_tasks": 0,
            "successful_tasks": 0
        }
        agent = await agent_service.create(db, obj_in=agent_data)
        
        # Then create the judge with the same ID
        judge_data = {
            "id": agent.id,
            "specialization": obj_in.specialization
        }
        db_obj = self.model(**judge_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_all_judges(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        Get all judges
        """
        query = select(Agent).where(Agent.agent_type == AgentType.JUDGE).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_judge_with_details(self, db: AsyncSession, judge_id: UUID) -> Optional[Judge]:
        """
        Get a judge with all details
        """
        query = select(Judge).where(Judge.id == judge_id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_judges_by_specialization(self, db: AsyncSession, specialization: str, skip: int = 0, limit: int = 100) -> List[Judge]:
        """
        Get judges by specialization
        """
        query = select(Judge).where(Judge.specialization == specialization).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# Create a singleton instance
judge_service = JudgeService()