from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.services.wallet_service import wallet_service
from app.db.services.stake_service import stake_service
from app.db.services.task_service import task_service
from app.db.services.agent_service import agent_service
from app.db.models.stake import StakeStatus
from app.schemas.wallet import Wallet
from app.schemas.stake import StakeCreate, Stake
from app.blockchain.solana_client import SolanaClient

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Solana client
solana_client = SolanaClient()

@router.post("/mint-nft")
async def mint_nft(
    title: str = Body(...),
    description: str = Body(...),
    creator_wallet: str = Body(...),
    metadata_url: str = Body(...),
    judges: List[str] = Body([]),
    deadline: int = Body(...),
    reward_amount: int = Body(...),
    reward_currency: str = Body("USDC"),
    db: AsyncSession = Depends(get_db)
):
    """
    Mint a new NFT for a task
    """
    try:
        # Create task NFT on Solana
        result = await solana_client.create_task_nft(
            title=title,
            summary=description,
            encrypted_payload_url=metadata_url,
            deadline=deadline,
            reward_amount=reward_amount,
            reward_currency=reward_currency,
            judges=judges
        )
        
        nft_id = result["task_nft"]
        
        # Add NFT to creator's wallet
        wallet = await wallet_service.get_by_address(db, creator_wallet)
        if wallet:
            await wallet_service.add_nft(db, wallet.id, nft_id)
        
        logger.info(f"Minted NFT {nft_id} for task '{title}'")
        
        return {
            "nft_id": nft_id,
            "title": title,
            "description": description,
            "creator_wallet": creator_wallet,
            "metadata_url": metadata_url,
            "transaction_id": result["signature"],
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error minting NFT: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error minting NFT: {str(e)}")

@router.post("/stake", response_model=Stake)
async def stake_sol(
    agent_wallet: str = Body(...),
    task_id: UUID = Body(...),
    amount: float = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Stake SOL for a task
    """
    # Verify task exists
    task = await task_service.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get agent by wallet address
    agent = await agent_service.get_by_wallet_address(db, agent_wallet)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if agent already has a stake for this task
    existing_stake = await stake_service.get_by_task_and_agent(db, task_id, agent.id)
    if existing_stake:
        raise HTTPException(status_code=400, detail="Agent already has a stake for this task")
    
    # Get agent's wallet
    wallet = await wallet_service.get_by_agent(db, agent.id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Check if agent has enough SOL
    if wallet.sol_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient SOL balance")
    
    try:
        # Stake SOL on Solana
        result = await solana_client.stake_on_task(
            agent_public_key=agent_wallet,
            task_account=str(task.nft_id),
            amount=int(amount * 1_000_000_000)  # Convert to lamports
        )
        
        # Deduct SOL from wallet
        await wallet_service.update_sol_balance(db, wallet.id, amount, is_addition=False)
        
        # Create stake
        stake_data = {
            "task_id": task_id,
            "agent_id": agent.id,
            "amount": amount,
            "status": StakeStatus.ACTIVE,
            "staked_at": datetime.utcnow(),
            "blockchain_id": result["stake_account"]
        }
        stake = await stake_service.create(db, obj_in=stake_data)
        
        # Update task status to STAKED if it was CREATED
        if task.status == "CREATED":
            await task_service.update_status(db, task_id, "STAKED")
        
        logger.info(f"Agent {agent_wallet} staked {amount} SOL for task {task_id}")
        
        return stake
    except Exception as e:
        logger.error(f"Error staking SOL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error staking SOL: {str(e)}")

@router.post("/unstake", response_model=Stake)
async def unstake_sol(
    stake_id: UUID = Body(...),
    judge_approval: bool = Body(...),
    judge_wallet: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Unstake SOL after task completion
    """
    # Get stake
    stake = await stake_service.get(db, stake_id)
    if not stake:
        raise HTTPException(status_code=404, detail="Stake not found")
    
    # Check if stake is already released
    if stake.status != StakeStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Stake is not active")
    
    # Get task
    task = await task_service.get(db, stake.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get agent
    agent = await agent_service.get(db, stake.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Return stake on Solana
        result = await solana_client.return_stake(
            judge_public_key=judge_wallet,
            stake_account=stake.blockchain_id
        )
        
        # Set stake status based on judge approval
        status = StakeStatus.RETURNED if judge_approval else StakeStatus.FORFEITED
        
        # Release stake
        stake = await stake_service.release_stake(db, stake_id, status)
        
        # If approved, return SOL to agent's wallet
        if judge_approval:
            wallet = await wallet_service.get_by_agent(db, stake.agent_id)
            if wallet:
                await wallet_service.update_sol_balance(db, wallet.id, stake.amount, is_addition=True)
        
        logger.info(f"Unstaking stake {stake_id}, judge approved: {judge_approval}")
        
        return stake
    except Exception as e:
        logger.error(f"Error unstaking SOL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error unstaking SOL: {str(e)}")

@router.post("/transfer-reward")
async def transfer_reward(
    task_id: UUID = Body(...),
    winner_wallet: str = Body(...),
    creator_wallet: str = Body(...),
    amount: float = Body(...),
    currency: str = Body("USDC"),
    db: AsyncSession = Depends(get_db)
):
    """
    Transfer reward to the winning agent
    """
    # Verify task exists
    task = await task_service.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get winner's wallet
    wallet = await wallet_service.get_by_address(db, winner_wallet)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    try:
        # Complete task on Solana
        result = await solana_client.complete_task(
            creator_public_key=creator_wallet,
            task_account=str(task.nft_id),
            winning_agent_public_key=winner_wallet
        )
        
        # Add reward to wallet
        if currency == "USDC":
            await wallet_service.update_usdc_balance(db, wallet.id, amount, is_addition=True)
        elif currency == "SOL":
            await wallet_service.update_sol_balance(db, wallet.id, amount, is_addition=True)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported currency: {currency}")
        
        # Update task status to COMPLETED
        await task_service.update_status(db, task_id, "COMPLETED")
        
        logger.info(f"Transferring {amount} {currency} to {winner_wallet} for task {task_id}")
        
        return {
            "task_id": str(task_id),
            "winner_wallet": winner_wallet,
            "amount": amount,
            "currency": currency,
            "transaction_id": result["signature"],
            "transferred_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error transferring reward: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error transferring reward: {str(e)}")

@router.post("/submit-deliverable")
async def submit_deliverable(
    agent_wallet: str = Body(...),
    task_id: UUID = Body(...),
    encrypted_content_url: str = Body(...),
    encryption_keys: Dict[str, str] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a deliverable for a task
    """
    # Verify task exists
    task = await task_service.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get agent by wallet address
    agent = await agent_service.get_by_wallet_address(db, agent_wallet)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Submit deliverable on Solana
        result = await solana_client.submit_deliverable(
            agent_public_key=agent_wallet,
            task_account=str(task.nft_id),
            encrypted_content_url=encrypted_content_url,
            encryption_keys=encryption_keys
        )
        
        # Update task status to SUBMITTED
        await task_service.update_status(db, task_id, "SUBMITTED")
        
        logger.info(f"Agent {agent_wallet} submitted deliverable for task {task_id}")
        
        return {
            "task_id": str(task_id),
            "agent_wallet": agent_wallet,
            "deliverable_account": result["deliverable_account"],
            "transaction_id": result["signature"],
            "submitted_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error submitting deliverable: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting deliverable: {str(e)}")

@router.get("/wallet/{wallet_address}", response_model=Wallet)
async def get_wallet_info(
    wallet_address: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get information about a wallet
    """
    wallet = await wallet_service.get_by_address(db, wallet_address)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Get on-chain balance
    try:
        sol_balance = await solana_client.get_account_balance(wallet_address)
        wallet.sol_balance = sol_balance / 1_000_000_000  # Convert from lamports to SOL
    except Exception as e:
        logger.warning(f"Error getting on-chain balance: {str(e)}")
    
    return wallet

@router.get("/transaction/{tx_id}")
async def get_transaction(tx_id: str):
    """
    Get information about a transaction
    """
    # In a real implementation, this would query the Solana blockchain
    # For the demo, we'll still return mock data
    return {
        "id": tx_id,
        "status": "CONFIRMED",
        "block": 12345678,
        "timestamp": datetime.utcnow().isoformat(),
        "fee": 0.000005,
        "signatures": [tx_id]
    }

@router.post("/airdrop")
async def request_airdrop(
    wallet_address: str = Body(...),
    amount: float = Body(1.0)  # Default to 1 SOL
):
    """
    Request an airdrop of SOL to a wallet (only works on devnet and testnet)
    """
    try:
        # Convert SOL to lamports
        lamports = int(amount * 1_000_000_000)
        
        logger.info(f"Requesting airdrop of {amount} SOL ({lamports} lamports) to {wallet_address}")
        
        # Request airdrop
        try:
            signature = await solana_client.airdrop(wallet_address, lamports)
            
            if not signature:
                logger.error("Airdrop returned None signature")
                raise HTTPException(status_code=500, detail="Airdrop failed: No signature returned")
            
            logger.info(f"Airdrop successful: {signature}")
            
            return {
                "wallet_address": wallet_address,
                "amount": amount,
                "transaction_id": signature,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as solana_error:
            logger.error(f"Solana client error: {str(solana_error)}")
            raise HTTPException(status_code=500, detail=f"Solana client error: {str(solana_error)}")
    except Exception as e:
        logger.error(f"Error requesting airdrop: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error requesting airdrop: {str(e)}")