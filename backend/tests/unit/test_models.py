import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.agent import Agent, AgentType
from app.db.models.judge import Judge
from app.db.models.task import Task, TaskStatus
from app.db.models.deliverable import Deliverable, DeliverableStatus
from app.db.models.stake import Stake, StakeStatus
from app.db.models.wallet import Wallet

pytestmark = pytest.mark.asyncio

async def test_agent_model(db_session: AsyncSession):
    """
    Test the Agent model
    """
    # Create a worker agent
    agent_id = uuid.uuid4()
    agent = Agent(
        id=agent_id,
        name="Test Agent",
        description="Test agent description",
        agent_type=AgentType.WORKER,
        wallet_address="test_wallet_address",
        public_key="test_public_key",
        reputation_score=4.5,
        completed_tasks=10,
        successful_tasks=8
    )
    
    db_session.add(agent)
    await db_session.commit()
    
    # Query the agent
    result = await db_session.get(Agent, agent_id)
    assert result is not None
    assert result.id == agent_id
    assert result.name == "Test Agent"
    assert result.description == "Test agent description"
    assert result.agent_type == AgentType.WORKER
    assert result.wallet_address == "test_wallet_address"
    assert result.public_key == "test_public_key"
    assert result.reputation_score == 4.5
    assert result.completed_tasks == 10
    assert result.successful_tasks == 8

async def test_judge_model(db_session: AsyncSession):
    """
    Test the Judge model
    """
    # Create a judge agent
    agent_id = uuid.uuid4()
    agent = Agent(
        id=agent_id,
        name="Test Judge",
        description="Test judge description",
        agent_type=AgentType.JUDGE,
        wallet_address="test_judge_wallet",
        public_key="test_judge_public_key",
        reputation_score=4.8,
        completed_tasks=20,
        successful_tasks=18
    )
    
    judge = Judge(
        id=agent_id,
        specialization="Test Specialization"
    )
    
    db_session.add_all([agent, judge])
    await db_session.commit()
    
    # Query the judge
    result = await db_session.get(Judge, agent_id)
    assert result is not None
    assert result.id == agent_id
    assert result.specialization == "Test Specialization"
    
    # Query the agent
    agent_result = await db_session.get(Agent, agent_id)
    assert agent_result is not None
    assert agent_result.agent_type == AgentType.JUDGE

async def test_task_model(db_session: AsyncSession):
    """
    Test the Task model
    """
    # Create a creator agent
    creator_id = uuid.uuid4()
    creator = Agent(
        id=creator_id,
        name="Task Creator",
        description="Task creator description",
        agent_type=AgentType.JUDGE,
        wallet_address="creator_wallet",
        public_key="creator_public_key"
    )
    
    # Create a judge agent
    judge_id = uuid.uuid4()
    judge = Agent(
        id=judge_id,
        name="Task Judge",
        description="Task judge description",
        agent_type=AgentType.JUDGE,
        wallet_address="judge_wallet",
        public_key="judge_public_key"
    )
    
    # Create a task
    task_id = uuid.uuid4()
    task = Task(
        id=task_id,
        nft_id="test_nft_id",
        title="Test Task",
        summary="Test task summary",
        encrypted_payload_url="https://example.com/encrypted/test",
        creator_id=creator_id,
        status=TaskStatus.CREATED,
        deadline=datetime.utcnow() + timedelta(days=7),
        reward_amount=100.0,
        reward_currency="USDC"
    )
    
    # Add judge to task
    task.judges.append(judge)
    
    db_session.add_all([creator, judge, task])
    await db_session.commit()
    
    # Query the task
    result = await db_session.get(Task, task_id)
    assert result is not None
    assert result.id == task_id
    assert result.nft_id == "test_nft_id"
    assert result.title == "Test Task"
    assert result.summary == "Test task summary"
    assert result.encrypted_payload_url == "https://example.com/encrypted/test"
    assert result.creator_id == creator_id
    assert result.status == TaskStatus.CREATED
    assert result.reward_amount == 100.0
    assert result.reward_currency == "USDC"
    assert len(result.judges) == 1
    assert result.judges[0].id == judge_id

async def test_deliverable_model(db_session: AsyncSession):
    """
    Test the Deliverable model
    """
    # Create a task
    task_id = uuid.uuid4()
    task = Task(
        id=task_id,
        nft_id="deliverable_test_nft",
        title="Deliverable Test Task",
        summary="Deliverable test task summary",
        encrypted_payload_url="https://example.com/encrypted/deliverable-test",
        creator_id=uuid.uuid4(),
        status=TaskStatus.CREATED,
        deadline=datetime.utcnow() + timedelta(days=7),
        reward_amount=100.0,
        reward_currency="USDC"
    )
    
    # Create an agent
    agent_id = uuid.uuid4()
    agent = Agent(
        id=agent_id,
        name="Deliverable Agent",
        description="Deliverable agent description",
        agent_type=AgentType.WORKER,
        wallet_address="deliverable_agent_wallet",
        public_key="deliverable_agent_public_key"
    )
    
    # Create a deliverable
    deliverable_id = uuid.uuid4()
    deliverable = Deliverable(
        id=deliverable_id,
        task_id=task_id,
        agent_id=agent_id,
        encrypted_content_url="https://example.com/encrypted/deliverable-content",
        encryption_keys={"judge1": "encrypted_key1", "judge2": "encrypted_key2"},
        submission_time=datetime.utcnow(),
        scores={"judge1": 4.5, "judge2": 4.0},
        feedback={"judge1": "Good work", "judge2": "Could be improved"},
        status=DeliverableStatus.JUDGED
    )
    
    db_session.add_all([task, agent, deliverable])
    await db_session.commit()
    
    # Query the deliverable
    result = await db_session.get(Deliverable, deliverable_id)
    assert result is not None
    assert result.id == deliverable_id
    assert result.task_id == task_id
    assert result.agent_id == agent_id
    assert result.encrypted_content_url == "https://example.com/encrypted/deliverable-content"
    assert result.encryption_keys == {"judge1": "encrypted_key1", "judge2": "encrypted_key2"}
    assert result.scores == {"judge1": 4.5, "judge2": 4.0}
    assert result.feedback == {"judge1": "Good work", "judge2": "Could be improved"}
    assert result.status == DeliverableStatus.JUDGED

async def test_stake_model(db_session: AsyncSession):
    """
    Test the Stake model
    """
    # Create a task
    task_id = uuid.uuid4()
    task = Task(
        id=task_id,
        nft_id="stake_test_nft",
        title="Stake Test Task",
        summary="Stake test task summary",
        encrypted_payload_url="https://example.com/encrypted/stake-test",
        creator_id=uuid.uuid4(),
        status=TaskStatus.CREATED,
        deadline=datetime.utcnow() + timedelta(days=7),
        reward_amount=100.0,
        reward_currency="USDC"
    )
    
    # Create an agent
    agent_id = uuid.uuid4()
    agent = Agent(
        id=agent_id,
        name="Stake Agent",
        description="Stake agent description",
        agent_type=AgentType.WORKER,
        wallet_address="stake_agent_wallet",
        public_key="stake_agent_public_key"
    )
    
    # Create a stake
    stake_id = uuid.uuid4()
    stake = Stake(
        id=stake_id,
        task_id=task_id,
        agent_id=agent_id,
        amount=5.0,
        status=StakeStatus.ACTIVE,
        staked_at=datetime.utcnow()
    )
    
    db_session.add_all([task, agent, stake])
    await db_session.commit()
    
    # Query the stake
    result = await db_session.get(Stake, stake_id)
    assert result is not None
    assert result.id == stake_id
    assert result.task_id == task_id
    assert result.agent_id == agent_id
    assert result.amount == 5.0
    assert result.status == StakeStatus.ACTIVE
    assert result.released_at is None

async def test_wallet_model(db_session: AsyncSession):
    """
    Test the Wallet model
    """
    # Create an agent
    agent_id = uuid.uuid4()
    agent = Agent(
        id=agent_id,
        name="Wallet Agent",
        description="Wallet agent description",
        agent_type=AgentType.WORKER,
        wallet_address="wallet_agent_address",
        public_key="wallet_agent_public_key"
    )
    
    # Create a wallet
    wallet_id = uuid.uuid4()
    wallet = Wallet(
        id=wallet_id,
        address="wallet_address",
        agent_id=agent_id,
        sol_balance=10.0,
        usdc_balance=500.0,
        nfts=["nft1", "nft2", "nft3"]
    )
    
    db_session.add_all([agent, wallet])
    await db_session.commit()
    
    # Query the wallet
    result = await db_session.get(Wallet, wallet_id)
    assert result is not None
    assert result.id == wallet_id
    assert result.address == "wallet_address"
    assert result.agent_id == agent_id
    assert result.sol_balance == 10.0
    assert result.usdc_balance == 500.0
    assert result.nfts == ["nft1", "nft2", "nft3"]