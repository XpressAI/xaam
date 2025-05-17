import pytest
from fastapi.testclient import TestClient
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# Import the FastAPI app
from app.main import app
from app.db.models.wallet import Wallet
from app.db.models.stake import Stake, StakeStatus

pytestmark = pytest.mark.asyncio

async def test_mint_nft(client: TestClient, test_data: dict):
    """
    Test minting an NFT
    """
    creator_wallet = test_data["judge_wallet"]
    
    mint_data = {
        "title": "Test NFT",
        "description": "This is a test NFT",
        "creator_wallet": creator_wallet.address,
        "metadata_url": "https://example.com/metadata/test-nft"
    }
    
    response = client.post("/api/blockchain/mint-nft", json=mint_data)
    assert response.status_code == 200
    assert "nft_id" in response.json()
    assert response.json()["title"] == mint_data["title"]
    assert response.json()["description"] == mint_data["description"]
    assert response.json()["creator_wallet"] == mint_data["creator_wallet"]
    assert response.json()["metadata_url"] == mint_data["metadata_url"]
    assert "transaction_id" in response.json()
    assert "created_at" in response.json()

async def test_stake_sol(client: TestClient, test_data: dict):
    """
    Test staking SOL for a task
    """
    worker = test_data["worker"]
    worker_wallet = test_data["worker_wallet"]
    task = test_data["task"]
    
    stake_data = {
        "agent_wallet": worker_wallet.address,
        "task_id": str(task.id),
        "amount": 2.0
    }
    
    response = client.post("/api/blockchain/stake", json=stake_data)
    assert response.status_code == 200
    assert response.json()["task_id"] == str(task.id)
    assert response.json()["agent_id"] == str(worker.id)
    assert response.json()["amount"] == 2.0
    assert response.json()["status"] == "ACTIVE"
    assert "staked_at" in response.json()

async def test_unstake_sol(client: TestClient, db_session: AsyncSession, test_data: dict):
    """
    Test unstaking SOL
    """
    worker = test_data["worker"]
    task = test_data["task"]
    
    # First, create a stake
    stake = Stake(
        id=uuid.uuid4(),
        task_id=task.id,
        agent_id=worker.id,
        amount=3.0,
        status=StakeStatus.ACTIVE,
        staked_at=datetime.utcnow()
    )
    
    db_session.add(stake)
    await db_session.commit()
    await db_session.refresh(stake)
    
    # Unstake with judge approval
    unstake_data = {
        "stake_id": str(stake.id),
        "judge_approval": True
    }
    
    response = client.post("/api/blockchain/unstake", json=unstake_data)
    assert response.status_code == 200
    assert response.json()["stake_id"] == str(stake.id)
    assert response.json()["status"] == "RETURNED"
    assert "released_at" in response.json()

async def test_transfer_reward(client: TestClient, test_data: dict):
    """
    Test transferring a reward
    """
    worker = test_data["worker"]
    worker_wallet = test_data["worker_wallet"]
    task = test_data["task"]
    
    transfer_data = {
        "task_id": str(task.id),
        "winner_wallet": worker_wallet.address,
        "amount": 100.0,
        "currency": "USDC"
    }
    
    response = client.post("/api/blockchain/transfer-reward", json=transfer_data)
    assert response.status_code == 200
    assert response.json()["task_id"] == str(task.id)
    assert response.json()["winner_wallet"] == worker_wallet.address
    assert response.json()["amount"] == 100.0
    assert response.json()["currency"] == "USDC"
    assert "transaction_id" in response.json()
    assert "transferred_at" in response.json()

async def test_get_wallet_info(client: TestClient, test_data: dict):
    """
    Test getting wallet information
    """
    worker_wallet = test_data["worker_wallet"]
    
    response = client.get(f"/api/blockchain/wallet/{worker_wallet.address}")
    assert response.status_code == 200
    assert response.json()["address"] == worker_wallet.address
    assert response.json()["agent_id"] == str(worker_wallet.agent_id)
    assert "sol_balance" in response.json()
    assert "usdc_balance" in response.json()
    assert "nfts" in response.json()

async def test_get_transaction(client: TestClient):
    """
    Test getting transaction information
    """
    # Generate a mock transaction ID
    tx_id = f"tx_{uuid.uuid4().hex}"
    
    response = client.get(f"/api/blockchain/transaction/{tx_id}")
    assert response.status_code == 200
    assert response.json()["id"] == tx_id
    assert "status" in response.json()
    assert "block" in response.json()
    assert "timestamp" in response.json()
    assert "fee" in response.json()
    assert "signatures" in response.json()