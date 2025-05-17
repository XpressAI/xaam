import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.services.agent_service import agent_service
from app.db.services.judge_service import judge_service
from app.db.services.task_service import task_service
from app.db.services.deliverable_service import deliverable_service
from app.db.services.stake_service import stake_service
from app.db.services.wallet_service import wallet_service

from app.db.models.agent import AgentType
from app.db.models.task import TaskStatus
from app.db.models.deliverable import DeliverableStatus
from app.db.models.stake import StakeStatus

from app.schemas.agent import AgentCreate, AgentUpdate
from app.schemas.judge import JudgeCreate, JudgeUpdate
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.deliverable import DeliverableCreate, DeliverableUpdate
from app.schemas.stake import StakeCreate, StakeUpdate
from app.schemas.wallet import WalletCreate, WalletUpdate

pytestmark = pytest.mark.asyncio

async def test_agent_service(db_session: AsyncSession):
    """
    Test the AgentService
    """
    # Create an agent
    agent_data = AgentCreate(
        name="Service Test Agent",
        description="Service test agent description",
        agent_type=AgentType.WORKER,
        wallet_address="service_test_wallet",
        public_key="service_test_public_key"
    )
    
    agent = await agent_service.create(db_session, obj_in=agent_data)
    assert agent.name == agent_data.name
    assert agent.description == agent_data.description
    assert agent.agent_type == agent_data.agent_type
    assert agent.wallet_address == agent_data.wallet_address
    assert agent.public_key == agent_data.public_key
    
    # Get the agent by ID
    retrieved_agent = await agent_service.get(db_session, agent.id)
    assert retrieved_agent is not None
    assert retrieved_agent.id == agent.id
    
    # Get the agent by wallet address
    wallet_agent = await agent_service.get_by_wallet_address(db_session, agent.wallet_address)
    assert wallet_agent is not None
    assert wallet_agent.id == agent.id
    
    # Update the agent
    update_data = AgentUpdate(
        name="Updated Service Test Agent",
        description="Updated service test agent description"
    )
    
    updated_agent = await agent_service.update(db_session, db_obj=agent, obj_in=update_data)
    assert updated_agent.name == update_data.name
    assert updated_agent.description == update_data.description
    
    # Update agent reputation
    reputation_agent = await agent_service.update_reputation(
        db_session,
        agent.id,
        task_completed=True,
        task_successful=True,
        reputation_delta=4.5
    )
    
    assert reputation_agent is not None
    assert reputation_agent.completed_tasks == 1
    assert reputation_agent.successful_tasks == 1
    assert reputation_agent.reputation_score == 4.5
    
    # Get agents by type
    worker_agents = await agent_service.get_by_type(db_session, AgentType.WORKER)
    assert len(worker_agents) > 0
    assert all(a.agent_type == AgentType.WORKER for a in worker_agents)
    
    # Search agents
    search_results = await agent_service.search_agents(db_session, "Updated")
    assert len(search_results) > 0
    assert any(a.id == agent.id for a in search_results)
    
    # Delete the agent
    deleted_agent = await agent_service.remove(db_session, id=agent.id)
    assert deleted_agent is not None
    assert deleted_agent.id == agent.id
    
    # Verify the agent is deleted
    deleted_check = await agent_service.get(db_session, agent.id)
    assert deleted_check is None

async def test_judge_service(db_session: AsyncSession):
    """
    Test the JudgeService
    """
    # Create a judge
    judge_data = JudgeCreate(
        name="Service Test Judge",
        description="Service test judge description",
        wallet_address="service_test_judge_wallet",
        public_key="service_test_judge_public_key",
        specialization="Service Testing"
    )
    
    judge = await judge_service.create_judge(db_session, obj_in=judge_data)
    assert judge is not None
    
    # Get all judges
    judges = await judge_service.get_all_judges(db_session)
    assert len(judges) > 0
    assert any(j.id == judge.id for j in judges)
    
    # Get judge with details
    judge_details = await judge_service.get_judge_with_details(db_session, judge.id)
    assert judge_details is not None
    assert judge_details.id == judge.id
    assert judge_details.specialization == judge_data.specialization
    
    # Get judges by specialization
    spec_judges = await judge_service.get_judges_by_specialization(db_session, judge_data.specialization)
    assert len(spec_judges) > 0
    assert any(j.id == judge.id for j in spec_judges)

async def test_task_service(db_session: AsyncSession):
    """
    Test the TaskService
    """
    # Create a judge for the task
    judge_data = JudgeCreate(
        name="Task Service Test Judge",
        description="Task service test judge description",
        wallet_address="task_service_judge_wallet",
        public_key="task_service_judge_public_key",
        specialization="Task Service Testing"
    )
    
    judge = await judge_service.create_judge(db_session, obj_in=judge_data)
    
    # Create a task
    task_data = TaskCreate(
        title="Service Test Task",
        summary="Service test task summary",
        encrypted_payload_url="https://example.com/encrypted/service-test",
        creator_id=judge.id,
        deadline=datetime.utcnow() + timedelta(days=7),
        reward_amount=100.0,
        reward_currency="USDC",
        judges=[judge.id]
    )
    
    task = await task_service.create_with_judges(db_session, obj_in=task_data)
    assert task.title == task_data.title
    assert task.summary == task_data.summary
    assert task.encrypted_payload_url == task_data.encrypted_payload_url
    assert task.creator_id == task_data.creator_id
    assert task.reward_amount == task_data.reward_amount
    assert task.reward_currency == task_data.reward_currency
    assert len(task.judges) == 1
    assert task.judges[0].id == judge.id
    
    # Get the task by ID
    retrieved_task = await task_service.get(db_session, task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    
    # Get tasks by status
    status_tasks = await task_service.get_by_status(db_session, TaskStatus.CREATED)
    assert len(status_tasks) > 0
    assert any(t.id == task.id for t in status_tasks)
    
    # Get tasks by creator
    creator_tasks = await task_service.get_by_creator(db_session, judge.id)
    assert len(creator_tasks) > 0
    assert any(t.id == task.id for t in creator_tasks)
    
    # Get tasks by judge
    judge_tasks = await task_service.get_by_judge(db_session, judge.id)
    assert len(judge_tasks) > 0
    assert any(t.id == task.id for t in judge_tasks)
    
    # Update task status
    updated_task = await task_service.update_status(db_session, task.id, TaskStatus.STAKED)
    assert updated_task is not None
    assert updated_task.status == TaskStatus.STAKED
    
    # Search tasks
    search_results = await task_service.search_tasks(db_session, "Service")
    assert len(search_results) > 0
    assert any(t.id == task.id for t in search_results)
    
    # Get active tasks
    active_tasks = await task_service.get_active_tasks(db_session)
    assert len(active_tasks) > 0
    assert any(t.id == task.id for t in active_tasks)

async def test_deliverable_service(db_session: AsyncSession):
    """
    Test the DeliverableService
    """
    # Create a judge
    judge_data = JudgeCreate(
        name="Deliverable Service Judge",
        description="Deliverable service judge description",
        wallet_address="deliverable_service_judge_wallet",
        public_key="deliverable_service_judge_public_key",
        specialization="Deliverable Service Testing"
    )
    
    judge = await judge_service.create_judge(db_session, obj_in=judge_data)
    
    # Create a worker agent
    worker_data = AgentCreate(
        name="Deliverable Service Worker",
        description="Deliverable service worker description",
        agent_type=AgentType.WORKER,
        wallet_address="deliverable_service_worker_wallet",
        public_key="deliverable_service_worker_public_key"
    )
    
    worker = await agent_service.create(db_session, obj_in=worker_data)
    
    # Create a task
    task_data = TaskCreate(
        title="Deliverable Service Task",
        summary="Deliverable service task summary",
        encrypted_payload_url="https://example.com/encrypted/deliverable-service",
        creator_id=judge.id,
        deadline=datetime.utcnow() + timedelta(days=7),
        reward_amount=100.0,
        reward_currency="USDC",
        judges=[judge.id]
    )
    
    task = await task_service.create_with_judges(db_session, obj_in=task_data)
    
    # Create a deliverable
    deliverable_data = DeliverableCreate(
        task_id=task.id,
        agent_id=worker.id,
        encrypted_content_url="https://example.com/encrypted/deliverable-service-content",
        encryption_keys={str(judge.id): "encrypted_key_for_judge"},
        submission_time=datetime.utcnow()
    )
    
    deliverable = await deliverable_service.create(db_session, obj_in=deliverable_data)
    assert deliverable.task_id == deliverable_data.task_id
    assert deliverable.agent_id == deliverable_data.agent_id
    assert deliverable.encrypted_content_url == deliverable_data.encrypted_content_url
    assert deliverable.encryption_keys == deliverable_data.encryption_keys
    assert deliverable.status == DeliverableStatus.SUBMITTED
    
    # Get deliverables by task
    task_deliverables = await deliverable_service.get_by_task(db_session, task.id)
    assert len(task_deliverables) > 0
    assert any(d.id == deliverable.id for d in task_deliverables)
    
    # Get deliverables by agent
    agent_deliverables = await deliverable_service.get_by_agent(db_session, worker.id)
    assert len(agent_deliverables) > 0
    assert any(d.id == deliverable.id for d in agent_deliverables)
    
    # Get deliverable by task and agent
    task_agent_deliverable = await deliverable_service.get_by_task_and_agent(db_session, task.id, worker.id)
    assert task_agent_deliverable is not None
    assert task_agent_deliverable.id == deliverable.id
    
    # Update deliverable score
    scored_deliverable = await deliverable_service.update_score(
        db_session,
        deliverable.id,
        str(judge.id),
        4.5,
        "Good work, but could be improved"
    )
    
    assert scored_deliverable is not None
    assert scored_deliverable.scores == {str(judge.id): 4.5}
    assert scored_deliverable.feedback == {str(judge.id): "Good work, but could be improved"}
    assert scored_deliverable.status == DeliverableStatus.JUDGED
    
    # Update deliverable status
    status_deliverable = await deliverable_service.update_status(db_session, deliverable.id, DeliverableStatus.ACCEPTED)
    assert status_deliverable is not None
    assert status_deliverable.status == DeliverableStatus.ACCEPTED
    
    # Get deliverables by status
    status_deliverables = await deliverable_service.get_by_status(db_session, DeliverableStatus.ACCEPTED)
    assert len(status_deliverables) > 0
    assert any(d.id == deliverable.id for d in status_deliverables)

async def test_stake_service(db_session: AsyncSession):
    """
    Test the StakeService
    """
    # Create a worker agent
    worker_data = AgentCreate(
        name="Stake Service Worker",
        description="Stake service worker description",
        agent_type=AgentType.WORKER,
        wallet_address="stake_service_worker_wallet",
        public_key="stake_service_worker_public_key"
    )
    
    worker = await agent_service.create(db_session, obj_in=worker_data)
    
    # Create a judge
    judge_data = JudgeCreate(
        name="Stake Service Judge",
        description="Stake service judge description",
        wallet_address="stake_service_judge_wallet",
        public_key="stake_service_judge_public_key",
        specialization="Stake Service Testing"
    )
    
    judge = await judge_service.create_judge(db_session, obj_in=judge_data)
    
    # Create a task
    task_data = TaskCreate(
        title="Stake Service Task",
        summary="Stake service task summary",
        encrypted_payload_url="https://example.com/encrypted/stake-service",
        creator_id=judge.id,
        deadline=datetime.utcnow() + timedelta(days=7),
        reward_amount=100.0,
        reward_currency="USDC",
        judges=[judge.id]
    )
    
    task = await task_service.create_with_judges(db_session, obj_in=task_data)
    
    # Create a stake
    stake_data = StakeCreate(
        task_id=task.id,
        agent_id=worker.id,
        amount=5.0,
        staked_at=datetime.utcnow()
    )
    
    stake = await stake_service.create(db_session, obj_in=stake_data)
    assert stake.task_id == stake_data.task_id
    assert stake.agent_id == stake_data.agent_id
    assert stake.amount == stake_data.amount
    assert stake.status == StakeStatus.ACTIVE
    
    # Get stakes by task
    task_stakes = await stake_service.get_by_task(db_session, task.id)
    assert len(task_stakes) > 0
    assert any(s.id == stake.id for s in task_stakes)
    
    # Get stakes by agent
    agent_stakes = await stake_service.get_by_agent(db_session, worker.id)
    assert len(agent_stakes) > 0
    assert any(s.id == stake.id for s in agent_stakes)
    
    # Get stake by task and agent
    task_agent_stake = await stake_service.get_by_task_and_agent(db_session, task.id, worker.id)
    assert task_agent_stake is not None
    assert task_agent_stake.id == stake.id
    
    # Get active stakes
    active_stakes = await stake_service.get_active_stakes(db_session)
    assert len(active_stakes) > 0
    assert any(s.id == stake.id for s in active_stakes)
    
    # Get agent active stakes total
    active_total = await stake_service.get_agent_active_stakes_total(db_session, worker.id)
    assert active_total == 5.0
    
    # Release stake
    released_stake = await stake_service.release_stake(db_session, stake.id, StakeStatus.RETURNED)
    assert released_stake is not None
    assert released_stake.status == StakeStatus.RETURNED
    assert released_stake.released_at is not None

async def test_wallet_service(db_session: AsyncSession):
    """
    Test the WalletService
    """
    # Create an agent
    agent_data = AgentCreate(
        name="Wallet Service Agent",
        description="Wallet service agent description",
        agent_type=AgentType.WORKER,
        wallet_address="wallet_service_agent_wallet",
        public_key="wallet_service_agent_public_key"
    )
    
    agent = await agent_service.create(db_session, obj_in=agent_data)
    
    # Create a wallet
    wallet_data = WalletCreate(
        address="wallet_service_address",
        agent_id=agent.id
    )
    
    wallet = await wallet_service.create(db_session, obj_in=wallet_data)
    assert wallet.address == wallet_data.address
    assert wallet.agent_id == wallet_data.agent_id
    assert wallet.sol_balance == 0.0
    assert wallet.usdc_balance == 0.0
    assert wallet.nfts == []
    
    # Get wallet by address
    address_wallet = await wallet_service.get_by_address(db_session, wallet.address)
    assert address_wallet is not None
    assert address_wallet.id == wallet.id
    
    # Get wallet by agent
    agent_wallet = await wallet_service.get_by_agent(db_session, agent.id)
    assert agent_wallet is not None
    assert agent_wallet.id == wallet.id
    
    # Update SOL balance
    sol_wallet = await wallet_service.update_sol_balance(db_session, wallet.id, 10.0, is_addition=True)
    assert sol_wallet is not None
    assert sol_wallet.sol_balance == 10.0
    
    # Update USDC balance
    usdc_wallet = await wallet_service.update_usdc_balance(db_session, wallet.id, 500.0, is_addition=True)
    assert usdc_wallet is not None
    assert usdc_wallet.usdc_balance == 500.0
    
    # Add NFT
    nft_wallet = await wallet_service.add_nft(db_session, wallet.id, "test_nft_id")
    assert nft_wallet is not None
    assert "test_nft_id" in nft_wallet.nfts
    
    # Remove NFT
    remove_nft_wallet = await wallet_service.remove_nft(db_session, wallet.id, "test_nft_id")
    assert remove_nft_wallet is not None
    assert "test_nft_id" not in remove_nft_wallet.nfts