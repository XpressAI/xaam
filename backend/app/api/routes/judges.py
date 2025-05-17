from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.services.judge_service import judge_service
from app.db.services.task_service import task_service
from app.db.services.agent_service import agent_service
from app.db.services.deliverable_service import deliverable_service
from app.db.models.agent import AgentType
from app.schemas.judge import Judge, JudgeCreate, JudgeUpdate
from app.schemas.task import Task
from app.schemas.agent import Agent

router = APIRouter()

@router.get("/", response_model=List[Agent])
async def get_judges(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all judges
    """
    return await judge_service.get_all_judges(db, skip, limit)

@router.get("/{judge_id}", response_model=Agent)
async def get_judge(
    judge_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific judge by ID
    """
    judge = await agent_service.get(db, judge_id)
    if not judge or judge.agent_type != AgentType.JUDGE:
        raise HTTPException(status_code=404, detail="Judge not found")
    return judge

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_judge(
    judge_in: JudgeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new judge
    """
    # Check if wallet address already exists
    existing_agent = await agent_service.get_by_wallet_address(db, judge_in.wallet_address)
    if existing_agent:
        raise HTTPException(
            status_code=400,
            detail=f"Agent with wallet address {judge_in.wallet_address} already exists"
        )
    
    # Create judge (which creates an agent with type JUDGE)
    return await judge_service.create_judge(db, judge_in)

@router.get("/{judge_id}/tasks", response_model=List[Task])
async def get_judge_tasks(
    judge_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tasks assigned to a judge
    """
    # Verify judge exists
    judge = await agent_service.get(db, judge_id)
    if not judge or judge.agent_type != AgentType.JUDGE:
        raise HTTPException(status_code=404, detail="Judge not found")
    
    # Get tasks assigned to this judge
    return await task_service.get_by_judge(db, judge_id, skip, limit)

@router.post("/{judge_id}/score")
async def submit_score(
    judge_id: UUID,
    task_id: UUID = Body(...),
    agent_id: UUID = Body(...),
    score: float = Body(..., ge=0, le=5),  # Score between 0 and 5
    feedback: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a score and feedback for a task deliverable
    """
    # Verify judge exists
    judge = await agent_service.get(db, judge_id)
    if not judge or judge.agent_type != AgentType.JUDGE:
        raise HTTPException(status_code=404, detail="Judge not found")
    
    # Find the task
    task = await task_service.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify judge is assigned to this task
    judge_ids = [j.id for j in task.judges]
    if judge_id not in judge_ids:
        raise HTTPException(status_code=403, detail="Judge not assigned to this task")
    
    # Find the deliverable
    deliverable = await deliverable_service.get_by_task_and_agent(db, task_id, agent_id)
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    # Update deliverable with score and feedback
    await deliverable_service.update_score(db, deliverable.id, str(judge_id), score, feedback)
    
    # Update agent reputation based on score
    task_successful = score >= 3.0  # Consider task successful if score is at least 3.0
    await agent_service.update_reputation(
        db,
        agent_id,
        task_completed=True,
        task_successful=task_successful,
        reputation_delta=score
    )
    
    return {
        "message": "Score submitted successfully",
        "task_id": str(task_id),
        "agent_id": str(agent_id),
        "judge_id": str(judge_id),
        "score": score,
        "feedback": feedback
    }

@router.get("/specialization/{specialization}", response_model=List[Judge])
async def get_judges_by_specialization(
    specialization: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get judges by specialization
    """
    return await judge_service.get_judges_by_specialization(db, specialization, skip, limit)

@router.put("/{judge_id}", response_model=Agent)
async def update_judge(
    judge_id: UUID,
    judge_update: JudgeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a judge's information
    """
    # First check if the judge exists
    judge = await agent_service.get(db, judge_id)
    if not judge or judge.agent_type != AgentType.JUDGE:
        raise HTTPException(status_code=404, detail="Judge not found")
    
    # Update the agent information
    return await agent_service.update(db, db_obj=judge, obj_in=judge_update)