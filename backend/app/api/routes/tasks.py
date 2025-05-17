from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.db.database import get_db
from app.db.services.task_service import task_service
from app.db.models.task import TaskStatus
from app.db.models.agent import Agent
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.encryption.service import encryption_service
from app.encryption.db_service import key_management_service

router = APIRouter()

@router.get("/", response_model=List[Task])
async def get_tasks(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tasks, optionally filtered by status
    """
    if status:
        try:
            task_status = TaskStatus(status)
            return await task_service.get_by_status(db, task_status, skip, limit)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    return await task_service.get_multi(db, skip=skip, limit=limit)

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific task by ID
    """
    task = await task_service.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task with encrypted payload
    """
    # Generate a mock NFT ID for now
    # In a real implementation, this would come from the blockchain service
    task_data = task_in.dict()
    task_data["nft_id"] = f"nft_{UUID().hex[:8]}"
    task_data["status"] = TaskStatus.CREATED
    
    # Get public keys for judges
    judge_public_keys = await key_management_service.get_judge_public_keys(db, task_in.judges)
    if not judge_public_keys:
        raise HTTPException(status_code=404, detail="No judge public keys found")
    
    # Encrypt payload
    try:
        encryption_result = encryption_service.encrypt_task_payload(payload, judge_public_keys)
        
        # Update task data with encrypted payload URL and encryption key
        # In a real implementation, the encrypted payload would be stored in IPFS or S3
        # For now, we'll just store the encrypted payload directly
        task_data["encrypted_payload_url"] = encryption_result["encrypted_payload"]
        
        # In a real implementation, the encryption keys would be stored in a separate table
        # For now, we'll just store the first encryption key in the task
        if encryption_result["encrypted_keys"]:
            first_judge_id = next(iter(encryption_result["encrypted_keys"]))
            task_data["encryption_key"] = encryption_result["encrypted_keys"][first_judge_id]
        
        # Create task with updated data
        task_create = TaskCreate(**task_data)
        return await task_service.create_with_judges(db, task_create)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encrypting task payload: {str(e)}")

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a task
    """
    task = await task_service.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return await task_service.update(db, db_obj=task, obj_in=task_update)

@router.put("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: UUID,
    status: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a task's status
    """
    try:
        task_status = TaskStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    task = await task_service.update_status(db, task_id, task_status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.get("/creator/{creator_id}", response_model=List[Task])
async def get_tasks_by_creator(
    creator_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get tasks created by a specific creator
    """
    return await task_service.get_by_creator(db, creator_id, skip, limit)

@router.get("/judge/{judge_id}", response_model=List[Task])
async def get_tasks_by_judge(
    judge_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get tasks assigned to a specific judge
    """
    return await task_service.get_by_judge(db, judge_id, skip, limit)

@router.post("/{task_id}/stake/{agent_id}", response_model=Dict[str, Any])
async def stake_on_task(
    task_id: UUID,
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Stake on a task and get access to the encrypted payload.
    In a real implementation, this would verify the stake on the blockchain.
    """
    # Get the task
    task = await task_service.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if agent exists
    # In a real implementation, this would check if the agent has staked
    # For now, we'll just check if the agent exists
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get the agent's private key
    private_key = await key_management_service.get_agent_private_key(agent_id)
    if not private_key:
        raise HTTPException(status_code=404, detail="Private key not found")
    
    # Get the encrypted key for this agent
    # In a real implementation, this would be stored in a stake record
    # For now, we'll just use the task's encryption_key field
    if not task.encryption_key:
        raise HTTPException(status_code=404, detail="Encryption key not found")
    
    try:
        # Decrypt the payload
        decrypted_payload = encryption_service.decrypt_task_payload(
            task.encrypted_payload_url,
            task.encryption_key,
            private_key
        )
        
        # Update task status to STAKED
        await task_service.update_status(db, task_id, TaskStatus.STAKED)
        
        return {
            "task": Task.from_orm(task),
            "payload": decrypted_payload
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting task payload: {str(e)}")

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a task
    """
    task = await task_service.remove(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return None