from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.db.database import get_db
from app.db.services.deliverable_service import deliverable_service
from app.db.services.task_service import task_service
from app.db.models.deliverable import DeliverableStatus
from app.db.models.agent import Agent
from app.schemas.deliverable import Deliverable, DeliverableCreate, DeliverableUpdate
from app.encryption.service import encryption_service
from app.encryption.db_service import key_management_service

router = APIRouter()

@router.get("/", response_model=List[Deliverable])
async def get_deliverables(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all deliverables, optionally filtered by status
    """
    if status:
        try:
            deliverable_status = DeliverableStatus(status)
            return await deliverable_service.get_by_status(db, deliverable_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    return await deliverable_service.get_multi(db, skip=skip, limit=limit)

@router.get("/{deliverable_id}", response_model=Deliverable)
async def get_deliverable(
    deliverable_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific deliverable by ID
    """
    deliverable = await deliverable_service.get(db, deliverable_id)
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return deliverable

@router.post("/", response_model=Deliverable, status_code=status.HTTP_201_CREATED)
async def create_deliverable(
    deliverable_in: DeliverableCreate,
    content: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new deliverable with encrypted content
    """
    # Check if task exists
    task = await task_service.get(db, deliverable_in.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if agent exists
    agent = await db.get(Agent, deliverable_in.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get public keys for judges assigned to the task
    judge_public_keys = {}
    for judge in task.judges:
        public_key = await key_management_service.get_agent_public_key(db, judge.id)
        if public_key:
            judge_public_keys[str(judge.id)] = public_key
    
    if not judge_public_keys:
        raise HTTPException(status_code=404, detail="No judge public keys found")
    
    # Encrypt deliverable content
    try:
        encryption_result = encryption_service.encrypt_deliverable(content, judge_public_keys)
        
        # Update deliverable data with encrypted content URL and encryption keys
        # In a real implementation, the encrypted content would be stored in IPFS or S3
        # For now, we'll just store the encrypted content directly
        deliverable_data = deliverable_in.dict()
        deliverable_data["encrypted_content_url"] = encryption_result["encrypted_content"]
        deliverable_data["encryption_keys"] = encryption_result["encrypted_keys"]
        deliverable_data["status"] = DeliverableStatus.SUBMITTED
        
        # Create deliverable with updated data
        deliverable_create = DeliverableCreate(**deliverable_data)
        return await deliverable_service.create(db, obj_in=deliverable_create)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encrypting deliverable content: {str(e)}")

@router.put("/{deliverable_id}", response_model=Deliverable)
async def update_deliverable(
    deliverable_id: UUID,
    deliverable_update: DeliverableUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a deliverable
    """
    deliverable = await deliverable_service.get(db, deliverable_id)
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    return await deliverable_service.update(db, db_obj=deliverable, obj_in=deliverable_update)

@router.put("/{deliverable_id}/status", response_model=Deliverable)
async def update_deliverable_status(
    deliverable_id: UUID,
    status: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a deliverable's status
    """
    try:
        deliverable_status = DeliverableStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    deliverable = await deliverable_service.update_status(db, deliverable_id, deliverable_status)
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    return deliverable

@router.get("/task/{task_id}", response_model=List[Deliverable])
async def get_deliverables_by_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all deliverables for a task
    """
    return await deliverable_service.get_by_task(db, task_id)

@router.get("/agent/{agent_id}", response_model=List[Deliverable])
async def get_deliverables_by_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all deliverables submitted by an agent
    """
    return await deliverable_service.get_by_agent(db, agent_id)

@router.post("/{deliverable_id}/judge/{judge_id}", response_model=Dict[str, Any])
async def judge_deliverable(
    deliverable_id: UUID,
    judge_id: UUID,
    score: float = Body(...),
    feedback: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Judge a deliverable and decrypt its content
    """
    # Get the deliverable
    deliverable = await deliverable_service.get(db, deliverable_id)
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    # Check if judge exists and is assigned to the task
    judge = await db.get(Agent, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    
    # Get the task to check if judge is assigned
    task = await task_service.get(db, deliverable.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if judge is assigned to the task
    judge_ids = [j.id for j in task.judges]
    if judge_id not in judge_ids:
        raise HTTPException(status_code=403, detail="Judge not assigned to this task")
    
    # Get the judge's private key
    private_key = await key_management_service.get_agent_private_key(judge_id)
    if not private_key:
        raise HTTPException(status_code=404, detail="Private key not found")
    
    # Get the encrypted key for this judge
    if not deliverable.encryption_keys or str(judge_id) not in deliverable.encryption_keys:
        raise HTTPException(status_code=404, detail="Encryption key not found for this judge")
    
    encrypted_key = deliverable.encryption_keys[str(judge_id)]
    
    try:
        # Decrypt the deliverable
        decrypted_content = encryption_service.decrypt_deliverable(
            deliverable.encrypted_content_url,
            encrypted_key,
            private_key
        )
        
        # Update the deliverable with the judge's score and feedback
        updated_deliverable = await deliverable_service.update_score(
            db, deliverable_id, str(judge_id), score, feedback
        )
        
        return {
            "deliverable": Deliverable.from_orm(updated_deliverable),
            "content": decrypted_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting deliverable: {str(e)}")

@router.delete("/{deliverable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deliverable(
    deliverable_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a deliverable
    """
    deliverable = await deliverable_service.remove(db, id=deliverable_id)
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return None