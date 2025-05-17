from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, List, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json
import base64

from app.db.database import get_db
from app.encryption.service import encryption_service
from app.encryption.db_service import key_management_service
from app.db.services.agent_service import agent_service
from app.db.services.task_service import task_service
from app.db.services.deliverable_service import deliverable_service

router = APIRouter()

@router.post("/keys/generate/{agent_id}", status_code=status.HTTP_201_CREATED)
async def generate_keys(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new key pair for an agent.
    The public key is stored in the database, and the private key is stored securely.
    """
    # Check if agent exists
    agent = await agent_service.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Generate keys
    success = await key_management_service.generate_keys_for_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to generate keys")
    
    return {"message": "Keys generated successfully"}

@router.get("/keys/public/{agent_id}")
async def get_public_key(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the public key for an agent.
    """
    # Check if agent exists
    agent = await agent_service.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get public key
    public_key = await key_management_service.get_agent_public_key(db, agent_id)
    if not public_key:
        raise HTTPException(status_code=404, detail="Public key not found")
    
    return {"public_key": public_key}

@router.post("/task/encrypt")
async def encrypt_task_payload(
    payload: Dict[str, Any] = Body(...),
    judge_ids: List[UUID] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Encrypt a task payload for multiple judges.
    """
    try:
        # Get public keys for judges
        judge_public_keys = await key_management_service.get_judge_public_keys(db, judge_ids)
        if not judge_public_keys:
            raise HTTPException(status_code=404, detail="No judge public keys found")
        
        # Encrypt payload
        encryption_result = encryption_service.encrypt_task_payload(payload, judge_public_keys)
        
        return {
            "encrypted_payload": encryption_result["encrypted_payload"],
            "encrypted_keys": encryption_result["encrypted_keys"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encrypting task payload: {str(e)}")

@router.post("/task/decrypt/{task_id}")
async def decrypt_task_payload(
    task_id: UUID,
    agent_id: UUID = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Decrypt a task payload for an agent.
    This endpoint should only be accessible to agents who have staked on the task.
    """
    try:
        # Get the task
        task = await task_service.get(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check if agent has staked on the task (this would be implemented in a real system)
        # For now, we'll just check if the agent exists
        agent = await agent_service.get(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get the agent's private key
        private_key = await key_management_service.get_agent_private_key(agent_id)
        if not private_key:
            raise HTTPException(status_code=404, detail="Private key not found")
        
        # Get the encrypted key for this agent
        # In a real system, this would be stored in a stake record
        # For now, we'll just use the task's encryption_key field
        if not task.encryption_key:
            raise HTTPException(status_code=404, detail="Encryption key not found")
        
        # Decrypt the payload
        decrypted_payload = encryption_service.decrypt_task_payload(
            task.encrypted_payload_url,
            task.encryption_key,
            private_key
        )
        
        return {"payload": decrypted_payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting task payload: {str(e)}")

@router.post("/deliverable/encrypt")
async def encrypt_deliverable(
    deliverable: Dict[str, Any] = Body(...),
    judge_ids: List[UUID] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Encrypt a deliverable for multiple judges.
    """
    try:
        # Get public keys for judges
        judge_public_keys = await key_management_service.get_judge_public_keys(db, judge_ids)
        if not judge_public_keys:
            raise HTTPException(status_code=404, detail="No judge public keys found")
        
        # Encrypt deliverable
        encryption_result = encryption_service.encrypt_deliverable(deliverable, judge_public_keys)
        
        return {
            "encrypted_content": encryption_result["encrypted_content"],
            "encrypted_keys": encryption_result["encrypted_keys"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encrypting deliverable: {str(e)}")

@router.post("/deliverable/decrypt/{deliverable_id}")
async def decrypt_deliverable(
    deliverable_id: UUID,
    judge_id: UUID = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Decrypt a deliverable for a judge.
    This endpoint should only be accessible to judges assigned to the task.
    """
    try:
        # Get the deliverable
        deliverable = await deliverable_service.get(db, deliverable_id)
        if not deliverable:
            raise HTTPException(status_code=404, detail="Deliverable not found")
        
        # Check if judge is assigned to the task (this would be implemented in a real system)
        # For now, we'll just check if the judge exists
        judge = await agent_service.get(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")
        
        # Get the judge's private key
        private_key = await key_management_service.get_agent_private_key(judge_id)
        if not private_key:
            raise HTTPException(status_code=404, detail="Private key not found")
        
        # Get the encrypted key for this judge
        if not deliverable.encryption_keys or str(judge_id) not in deliverable.encryption_keys:
            raise HTTPException(status_code=404, detail="Encryption key not found for this judge")
        
        encrypted_key = deliverable.encryption_keys[str(judge_id)]
        
        # Decrypt the deliverable
        decrypted_deliverable = encryption_service.decrypt_deliverable(
            deliverable.encrypted_content_url,
            encrypted_key,
            private_key
        )
        
        return {"deliverable": decrypted_deliverable}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting deliverable: {str(e)}")

@router.post("/encrypt")
async def encrypt_data(
    data: str = Body(...),
    public_key: str = Body(...)
):
    """
    Encrypt arbitrary data with a public key.
    """
    try:
        encrypted_data = encryption_service.encrypt_with_public_key(
            public_key,
            data.encode('utf-8')
        )
        
        return {"encrypted_data": base64.b64encode(encrypted_data).decode('utf-8')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encrypting data: {str(e)}")

@router.post("/decrypt")
async def decrypt_data(
    encrypted_data: str = Body(...),
    private_key: str = Body(...)
):
    """
    Decrypt arbitrary data with a private key.
    """
    try:
        decrypted_data = encryption_service.decrypt_with_private_key(
            private_key,
            base64.b64decode(encrypted_data)
        )
        
        return {"decrypted_data": decrypted_data.decode('utf-8')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting data: {str(e)}")