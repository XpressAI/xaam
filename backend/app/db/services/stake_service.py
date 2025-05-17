from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime

from app.db.models.stake import Stake, StakeStatus
from app.schemas.stake import StakeCreate, StakeUpdate
from app.db.services.base import BaseService


class StakeService(BaseService[Stake, StakeCreate, StakeUpdate]):
    def __init__(self):
        super().__init__(Stake)
    
    async def get_by_task(self, db: AsyncSession, task_id: UUID) -> List[Stake]:
        """
        Get all stakes for a task
        """
        query = select(self.model).where(self.model.task_id == task_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_agent(self, db: AsyncSession, agent_id: UUID) -> List[Stake]:
        """
        Get all stakes by an agent
        """
        query = select(self.model).where(self.model.agent_id == agent_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_task_and_agent(self, db: AsyncSession, task_id: UUID, agent_id: UUID) -> Optional[Stake]:
        """
        Get a stake by task and agent
        """
        query = select(self.model).where(
            and_(
                self.model.task_id == task_id,
                self.model.agent_id == agent_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_active_stakes(self, db: AsyncSession) -> List[Stake]:
        """
        Get all active stakes
        """
        query = select(self.model).where(self.model.status == StakeStatus.ACTIVE)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def release_stake(self, db: AsyncSession, stake_id: UUID, status: StakeStatus) -> Optional[Stake]:
        """
        Release a stake (return or forfeit)
        """
        stake = await self.get(db, stake_id)
        if not stake:
            return None
        
        stake.status = status
        stake.released_at = datetime.utcnow()
        
        db.add(stake)
        await db.commit()
        await db.refresh(stake)
        return stake
    
    async def get_agent_active_stakes_total(self, db: AsyncSession, agent_id: UUID) -> float:
        """
        Get the total amount of active stakes for an agent
        """
        query = select(self.model).where(
            and_(
                self.model.agent_id == agent_id,
                self.model.status == StakeStatus.ACTIVE
            )
        )
        result = await db.execute(query)
        stakes = result.scalars().all()
        
        return sum(stake.amount for stake in stakes)


# Create a singleton instance
stake_service = StakeService()