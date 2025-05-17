from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from datetime import datetime

from app.db.models.task import Task, TaskStatus
from app.db.models.agent import Agent
from app.schemas.task import TaskCreate, TaskUpdate
from app.db.services.base import BaseService


class TaskService(BaseService[Task, TaskCreate, TaskUpdate]):
    def __init__(self):
        super().__init__(Task)
    
    async def create_with_judges(self, db: AsyncSession, obj_in: TaskCreate) -> Task:
        """
        Create a new task with judges
        """
        # Create task
        task_data = obj_in.dict(exclude={"judges"})
        task = self.model(**task_data)
        
        # Add judges
        if obj_in.judges:
            for judge_id in obj_in.judges:
                judge = await db.get(Agent, judge_id)
                if judge and judge.agent_type == "JUDGE":
                    task.judges.append(judge)
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    async def get_by_status(self, db: AsyncSession, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get tasks by status
        """
        query = select(self.model).where(self.model.status == status).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_creator(self, db: AsyncSession, creator_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get tasks by creator
        """
        query = select(self.model).where(self.model.creator_id == creator_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_judge(self, db: AsyncSession, judge_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get tasks assigned to a judge
        """
        query = select(Task).join(Task.judges).where(Agent.id == judge_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_status(self, db: AsyncSession, task_id: UUID, status: TaskStatus) -> Optional[Task]:
        """
        Update a task's status
        """
        task = await self.get(db, task_id)
        if not task:
            return None
        
        task.status = status
        task.updated_at = datetime.utcnow()
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    async def search_tasks(self, db: AsyncSession, search_term: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Search tasks by title or summary
        """
        query = select(self.model).where(
            or_(
                self.model.title.ilike(f"%{search_term}%"),
                self.model.summary.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active_tasks(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get active tasks (created or staked)
        """
        query = select(self.model).where(
            or_(
                self.model.status == TaskStatus.CREATED,
                self.model.status == TaskStatus.STAKED
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# Create a singleton instance
task_service = TaskService()