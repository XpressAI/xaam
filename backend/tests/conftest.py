import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime, timedelta

# Import the FastAPI app and dependencies
from app.main import app
from app.db.database import Base, get_db
from app.db.models.agent import Agent, AgentType
from app.db.models.judge import Judge
from app.db.models.task import Task, TaskStatus
from app.db.models.deliverable import Deliverable, DeliverableStatus
from app.db.models.stake import Stake, StakeStatus
from app.db.models.wallet import Wallet

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Override the get_db dependency
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Create the database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a new session for the test
    async with TestingSessionLocal() as session:
        yield session
    
    # Drop the database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
async def test_data(db_session: AsyncSession) -> dict:
    """Create test data for the tests"""
    # Create worker agent
    worker = Agent(
        id=uuid4(),
        name="TestWorker",
        description="Test worker agent",
        agent_type=AgentType.WORKER,
        wallet_address="test_worker_wallet",
        public_key="test_worker_public_key",
        reputation_score=4.0,
        completed_tasks=10,
        successful_tasks=8
    )
    
    # Create judge agent
    judge = Agent(
        id=uuid4(),
        name="TestJudge",
        description="Test judge agent",
        agent_type=AgentType.JUDGE,
        wallet_address="test_judge_wallet",
        public_key="test_judge_public_key",
        reputation_score=4.5,
        completed_tasks=20,
        successful_tasks=18
    )
    
    # Create judge details
    judge_details = Judge(
        id=judge.id,
        specialization="Testing"
    )
    
    # Create wallets
    worker_wallet = Wallet(
        id=uuid4(),
        address=worker.wallet_address,
        agent_id=worker.id,
        sol_balance=10.0,
        usdc_balance=500.0,
        nfts=[]
    )
    
    judge_wallet = Wallet(
        id=uuid4(),
        address=judge.wallet_address,
        agent_id=judge.id,
        sol_balance=15.0,
        usdc_balance=750.0,
        nfts=[]
    )
    
    # Create task
    task = Task(
        id=uuid4(),
        nft_id=f"nft_test_{uuid4().hex[:8]}",
        title="Test Task",
        summary="This is a test task",
        encrypted_payload_url="https://example.com/encrypted/test",
        creator_id=judge.id,
        status=TaskStatus.CREATED,
        deadline=datetime.utcnow() + timedelta(days=7),
        reward_amount=100.0,
        reward_currency="USDC"
    )
    
    # Add judge to task
    task.judges.append(judge)
    
    # Add all objects to the session
    db_session.add_all([
        worker, judge, judge_details, worker_wallet, judge_wallet, task
    ])
    
    # Commit the session
    await db_session.commit()
    
    # Return the test data
    return {
        "worker": worker,
        "judge": judge,
        "worker_wallet": worker_wallet,
        "judge_wallet": judge_wallet,
        "task": task
    }