from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.database import get_db
from app.db.services.wallet_service import wallet_service
from app.db.services.agent_service import agent_service
from app.blockchain.solana_client import SolanaClient
from app.schemas.wallet import Wallet, WalletCreate

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Solana client
solana_client = SolanaClient()

@router.post("/create/{agent_id}", response_model=Wallet, status_code=status.HTTP_201_CREATED)
async def create_agent_wallet(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new wallet for an agent
    """
    # Check if agent exists
    agent = await agent_service.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if agent already has a wallet
    existing_wallet = await wallet_service.get_by_agent(db, agent_id)
    if existing_wallet:
        raise HTTPException(status_code=400, detail="Agent already has a wallet")
    
    try:
        # Generate a new wallet address using Solana client
        wallet_keypair = await solana_client.create_wallet()
        wallet_address = wallet_keypair["public_key"]
        
        # Create wallet in database
        wallet_data = WalletCreate(
            address=wallet_address,
            agent_id=agent_id
        )
        
        wallet = await wallet_service.create(db, obj_in=wallet_data)
        
        logger.info(f"Created wallet {wallet.address} for agent {agent_id}")
        
        return wallet
    except Exception as e:
        logger.error(f"Error creating wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating wallet: {str(e)}")

@router.post("/fund/{agent_id}", response_model=Wallet)
async def fund_agent_wallet(
    agent_id: UUID,
    amount: float = Body(...),
    currency: str = Body("SOL"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fund an agent's wallet
    """
    # Check if agent exists
    agent = await agent_service.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if agent has a wallet
    wallet = await wallet_service.get_by_agent(db, agent_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Agent does not have a wallet")
    
    try:
        # Transfer funds from user's wallet to agent's wallet
        if currency == "SOL":
            # In a real implementation, this would transfer SOL from the user's wallet
            # For now, we'll just update the agent's wallet balance
            wallet = await wallet_service.update_sol_balance(db, wallet.id, amount, is_addition=True)
        elif currency == "USDC":
            wallet = await wallet_service.update_usdc_balance(db, wallet.id, amount, is_addition=True)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported currency: {currency}")
        
        logger.info(f"Funded wallet {wallet.address} with {amount} {currency}")
        
        return wallet
    except Exception as e:
        logger.error(f"Error funding wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error funding wallet: {str(e)}")

@router.post("/withdraw/{agent_id}", response_model=Wallet)
async def withdraw_from_agent_wallet(
    agent_id: UUID,
    amount: float = Body(...),
    currency: str = Body("SOL"),
    db: AsyncSession = Depends(get_db)
):
    """
    Withdraw funds from an agent's wallet
    """
    # Check if agent exists
    agent = await agent_service.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if agent has a wallet
    wallet = await wallet_service.get_by_agent(db, agent_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Agent does not have a wallet")
    
    try:
        # Check if wallet has sufficient balance
        if currency == "SOL":
            if wallet.sol_balance < amount:
                raise HTTPException(status_code=400, detail="Insufficient SOL balance")
            wallet = await wallet_service.update_sol_balance(db, wallet.id, amount, is_addition=False)
        elif currency == "USDC":
            if wallet.usdc_balance < amount:
                raise HTTPException(status_code=400, detail="Insufficient USDC balance")
            wallet = await wallet_service.update_usdc_balance(db, wallet.id, amount, is_addition=False)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported currency: {currency}")
        
        logger.info(f"Withdrew {amount} {currency} from wallet {wallet.address}")
        
        return wallet
    except Exception as e:
        logger.error(f"Error withdrawing from wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error withdrawing from wallet: {str(e)}")

@router.get("/{agent_id}", response_model=Wallet)
async def get_agent_wallet(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get an agent's wallet
    """
    wallet = await wallet_service.get_by_agent(db, agent_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Get on-chain balance
    try:
        sol_balance = await solana_client.get_account_balance(wallet.address)
        wallet.sol_balance = sol_balance / 1_000_000_000  # Convert from lamports to SOL
    except Exception as e:
        logger.warning(f"Error getting on-chain balance: {str(e)}")
    
    return wallet