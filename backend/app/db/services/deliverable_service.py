from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime

from app.db.models.deliverable import Deliverable, DeliverableStatus
from app.schemas.deliverable import DeliverableCreate, DeliverableUpdate
from app.db.services.base import BaseService


class DeliverableService(BaseService[Deliverable, DeliverableCreate, DeliverableUpdate]):
    def __init__(self):
        super().__init__(Deliverable)
    
    async def get_by_task(self, db: AsyncSession, task_id: UUID) -> List[Deliverable]:
        """
        Get all deliverables for a task
        """
        query = select(self.model).where(self.model.task_id == task_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_agent(self, db: AsyncSession, agent_id: UUID) -> List[Deliverable]:
        """
        Get all deliverables submitted by an agent
        """
        query = select(self.model).where(self.model.agent_id == agent_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_task_and_agent(self, db: AsyncSession, task_id: UUID, agent_id: UUID) -> Optional[Deliverable]:
        """
        Get a deliverable by task and agent
        """
        query = select(self.model).where(
            and_(
                self.model.task_id == task_id,
                self.model.agent_id == agent_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def update_score(
        self, 
        db: AsyncSession, 
        deliverable_id: UUID, 
        judge_id: str, 
        score: float, 
        feedback: str
    ) -> Optional[Deliverable]:
        """
        Update a deliverable's score from a judge
        """
        deliverable = await self.get(db, deliverable_id)
        if not deliverable:
            return None
        
        # Initialize scores and feedback dictionaries if they don't exist
        if not deliverable.scores:
            deliverable.scores = {}
        if not deliverable.feedback:
            deliverable.feedback = {}
        
        # Add or update score and feedback
        deliverable.scores[str(judge_id)] = score
        deliverable.feedback[str(judge_id)] = feedback
        
        # Update status to JUDGED if not already
        if deliverable.status == DeliverableStatus.SUBMITTED:
            deliverable.status = DeliverableStatus.JUDGED
        
        db.add(deliverable)
        await db.commit()
        await db.refresh(deliverable)
        return deliverable
    
    async def update_status(self, db: AsyncSession, deliverable_id: UUID, status: DeliverableStatus) -> Optional[Deliverable]:
        """
        Update a deliverable's status
        """
        deliverable = await self.get(db, deliverable_id)
        if not deliverable:
            return None
        
        deliverable.status = status
        
        db.add(deliverable)
        await db.commit()
        await db.refresh(deliverable)
        return deliverable
    
    async def get_by_status(self, db: AsyncSession, status: DeliverableStatus) -> List[Deliverable]:
        """
        Get deliverables by status
        """
        query = select(self.model).where(self.model.status == status)
        result = await db.execute(query)
        return result.scalars().all()


# Create a singleton instance
deliverable_service = DeliverableService()