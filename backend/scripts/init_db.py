#!/usr/bin/env python3
"""
Script to initialize the database with sample data
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.db.database import AsyncSessionLocal
from app.db.models.agent import Agent, AgentType
from app.db.models.judge import Judge
from app.db.models.task import Task, TaskStatus
from app.db.models.deliverable import Deliverable, DeliverableStatus
from app.db.models.stake import Stake, StakeStatus
from app.db.models.wallet import Wallet

async def init_db():
    """Initialize the database with sample data"""
    async with AsyncSessionLocal() as db:
        # Create worker agents
        worker1 = Agent(
            id=uuid4(),
            name="TextAnalyzer",
            description="Specialized in text analysis and sentiment classification",
            agent_type=AgentType.WORKER,
            wallet_address="8ZJ6BLQAVygmMBiKrZUUULRZMRnk9S7tLps6pP3K5eCd",
            public_key="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
            reputation_score=4.8,
            completed_tasks=24,
            successful_tasks=22
        )
        
        worker2 = Agent(
            id=uuid4(),
            name="CodeReviewer",
            description="Expert in reviewing and optimizing code across multiple languages",
            agent_type=AgentType.WORKER,
            wallet_address="9ZJ6BLQAVygmMBiKrZUUULRZMRnk9S7tLps6pP3K5eCe",
            public_key="NIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
            reputation_score=4.5,
            completed_tasks=18,
            successful_tasks=15
        )
        
        # Create judges
        judge1 = Agent(
            id=uuid4(),
            name="QualityJudge",
            description="Expert in evaluating AI task outputs with high precision",
            agent_type=AgentType.JUDGE,
            wallet_address="6ZJ6BLQAVygmMBiKrZUUULRZMRnk9S7tLps6pP3K5eCe",
            public_key="NIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
            reputation_score=4.9,
            completed_tasks=50,
            successful_tasks=48
        )
        
        judge1_details = Judge(
            id=judge1.id,
            specialization="Natural Language Processing"
        )
        
        judge2 = Agent(
            id=uuid4(),
            name="CodeExpert",
            description="Specialized in evaluating code quality and performance",
            agent_type=AgentType.JUDGE,
            wallet_address="7ZJ6BLQAVygmMBiKrZUUULRZMRnk9S7tLps6pP3K5eCf",
            public_key="OIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
            reputation_score=4.7,
            completed_tasks=35,
            successful_tasks=32
        )
        
        judge2_details = Judge(
            id=judge2.id,
            specialization="Software Engineering"
        )
        
        # Create wallets
        wallet1 = Wallet(
            id=uuid4(),
            address=worker1.wallet_address,
            agent_id=worker1.id,
            sol_balance=15.0,
            usdc_balance=1000.0,
            nfts=[]
        )
        
        wallet2 = Wallet(
            id=uuid4(),
            address=worker2.wallet_address,
            agent_id=worker2.id,
            sol_balance=10.0,
            usdc_balance=750.0,
            nfts=[]
        )
        
        wallet3 = Wallet(
            id=uuid4(),
            address=judge1.wallet_address,
            agent_id=judge1.id,
            sol_balance=20.0,
            usdc_balance=1500.0,
            nfts=[]
        )
        
        wallet4 = Wallet(
            id=uuid4(),
            address=judge2.wallet_address,
            agent_id=judge2.id,
            sol_balance=18.0,
            usdc_balance=1200.0,
            nfts=[]
        )
        
        # Create tasks
        task1 = Task(
            id=uuid4(),
            nft_id=f"nft_{uuid4().hex[:8]}",
            title="Analyze sentiment in customer reviews",
            summary="Analyze 1000 customer reviews and classify sentiment",
            encrypted_payload_url="https://example.com/encrypted/task1",
            creator_id=judge1.id,
            status=TaskStatus.CREATED,
            deadline=datetime.utcnow() + timedelta(days=7),
            reward_amount=100.0,
            reward_currency="USDC"
        )
        
        task2 = Task(
            id=uuid4(),
            nft_id=f"nft_{uuid4().hex[:8]}",
            title="Optimize Python code for performance",
            summary="Review and optimize a Python data processing script for better performance",
            encrypted_payload_url="https://example.com/encrypted/task2",
            creator_id=judge2.id,
            status=TaskStatus.STAKED,
            deadline=datetime.utcnow() + timedelta(days=5),
            reward_amount=150.0,
            reward_currency="USDC"
        )
        
        # Add judges to tasks
        task1.judges.append(judge1)
        task2.judges.append(judge2)
        
        # Create stakes
        stake1 = Stake(
            id=uuid4(),
            task_id=task2.id,
            agent_id=worker2.id,
            amount=5.0,
            status=StakeStatus.ACTIVE,
            staked_at=datetime.utcnow() - timedelta(days=1)
        )
        
        # Create deliverables
        deliverable1 = Deliverable(
            id=uuid4(),
            task_id=task2.id,
            agent_id=worker2.id,
            encrypted_content_url="https://example.com/encrypted/deliverable1",
            encryption_keys={str(judge2.id): "encrypted_key_for_judge2"},
            submission_time=datetime.utcnow() - timedelta(hours=12),
            status=DeliverableStatus.SUBMITTED
        )
        
        # Add all objects to the session
        db.add_all([
            worker1, worker2, judge1, judge2, judge1_details, judge2_details,
            wallet1, wallet2, wallet3, wallet4,
            task1, task2, stake1, deliverable1
        ])
        
        # Commit the session
        await db.commit()
        
        print("Database initialized with sample data")

if __name__ == "__main__":
    asyncio.run(init_db())