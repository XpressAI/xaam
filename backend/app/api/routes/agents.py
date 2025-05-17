from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.services.agent_service import agent_service
from app.db.models.agent import AgentType
from app.schemas.agent import Agent, AgentCreate, AgentUpdate

router = APIRouter()

@router.get("/", response_model=List[Agent])
async def get_agents(
    agent_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all agents, optionally filtered by type (WORKER or JUDGE)
    """
    if agent_type:
        try:
            agent_type_enum = AgentType(agent_type)
            return await agent_service.get_by_type(db, agent_type_enum, skip, limit)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
    return await agent_service.get_multi(db, skip=skip, limit=limit)

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific agent by ID
    """
    agent = await agent_service.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_in: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new agent
    """
    # Check if wallet address already exists
    existing_agent = await agent_service.get_by_wallet_address(db, agent_in.wallet_address)
    if existing_agent:
        raise HTTPException(
            status_code=400,
            detail=f"Agent with wallet address {agent_in.wallet_address} already exists"
        )
    
    return await agent_service.create(db, obj_in=agent_in)

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: UUID,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an agent's information
    """
    agent = await agent_service.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return await agent_service.update(db, db_obj=agent, obj_in=agent_update)

@router.put("/{agent_id}/reputation", response_model=Agent)
async def update_agent_reputation(
    agent_id: UUID,
    task_completed: bool = Body(...),
    task_successful: bool = Body(...),
    reputation_delta: float = Body(...)
):
    """
    Update an agent's reputation after task completion
    """
    db = next(get_db())
    agent = await agent_service.update_reputation(
        db, 
        agent_id, 
        task_completed, 
        task_successful, 
        reputation_delta
    )
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent

@router.get("/wallet/{wallet_address}", response_model=Agent)
async def get_agent_by_wallet(
    wallet_address: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get an agent by wallet address
    """
    agent = await agent_service.get_by_wallet_address(db, wallet_address)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/search/{search_term}", response_model=List[Agent])
async def search_agents(
    search_term: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Search agents by name or description
    """
    return await agent_service.search_agents(db, search_term, skip, limit)

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an agent
    """
    agent = await agent_service.remove(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return None