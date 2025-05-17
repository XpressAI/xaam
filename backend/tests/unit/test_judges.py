import pytest
from fastapi.testclient import TestClient
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

# Import the FastAPI app
from app.main import app
from app.db.models.agent import Agent, AgentType
from app.db.models.judge import Judge

pytestmark = pytest.mark.asyncio

async def test_get_judges(client: TestClient, test_data: dict):
    """
    Test getting all judges
    """
    response = client.get("/api/judges")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(judge["agent_type"] == "JUDGE" for judge in response.json())

async def test_get_judge_by_id(client: TestClient, test_data: dict):
    """
    Test getting a specific judge by ID
    """
    judge = test_data["judge"]
    
    # Get the specific judge
    response = client.get(f"/api/judges/{judge.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(judge.id)
    assert response.json()["name"] == judge.name
    assert response.json()["agent_type"] == "JUDGE"

async def test_create_judge(client: TestClient):
    """
    Test creating a new judge
    """
    new_judge = {
        "name": "New Test Judge",
        "description": "This is a new test judge",
        "wallet_address": "new_test_judge_wallet",
        "public_key": "new_test_judge_public_key",
        "specialization": "Testing"
    }
    
    response = client.post("/api/judges", json=new_judge)
    assert response.status_code == 201
    
    created_judge = response.json()
    assert created_judge["name"] == new_judge["name"]
    assert created_judge["description"] == new_judge["description"]
    assert created_judge["wallet_address"] == new_judge["wallet_address"]
    assert created_judge["public_key"] == new_judge["public_key"]
    assert created_judge["agent_type"] == "JUDGE"
    assert created_judge["reputation_score"] == 0.0
    assert created_judge["completed_tasks"] == 0
    assert created_judge["successful_tasks"] == 0

async def test_get_judge_tasks(client: TestClient, test_data: dict):
    """
    Test getting tasks assigned to a judge
    """
    judge = test_data["judge"]
    
    response = client.get(f"/api/judges/{judge.id}/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

async def test_submit_score(client: TestClient, db_session: AsyncSession, test_data: dict):
    """
    Test submitting a score for a task deliverable
    """
    judge = test_data["judge"]
    task = test_data["task"]
    worker = test_data["worker"]
    
    # First, create a deliverable
    from app.db.models.deliverable import Deliverable, DeliverableStatus
    from datetime import datetime
    
    deliverable = Deliverable(
        id=uuid.uuid4(),
        task_id=task.id,
        agent_id=worker.id,
        encrypted_content_url="https://example.com/encrypted/test-deliverable",
        encryption_keys={str(judge.id): "encrypted_key_for_judge"},
        submission_time=datetime.utcnow(),
        status=DeliverableStatus.SUBMITTED
    )
    
    db_session.add(deliverable)
    await db_session.commit()
    await db_session.refresh(deliverable)
    
    # Submit a score
    score_data = {
        "task_id": str(task.id),
        "agent_id": str(worker.id),
        "score": 4.5,
        "feedback": "Good work, but could be improved"
    }
    
    response = client.post(f"/api/judges/{judge.id}/score", json=score_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Score submitted successfully"
    assert response.json()["task_id"] == str(task.id)
    assert response.json()["agent_id"] == str(worker.id)
    assert response.json()["judge_id"] == str(judge.id)
    assert response.json()["score"] == 4.5
    assert response.json()["feedback"] == "Good work, but could be improved"

async def test_get_judges_by_specialization(client: TestClient, test_data: dict):
    """
    Test getting judges by specialization
    """
    # Get the judge's specialization from the test data
    judge_id = test_data["judge"].id
    
    # Query the judge details to get the specialization
    from sqlalchemy.future import select
    from app.db.models.judge import Judge
    
    async with db_session as session:
        result = await session.execute(select(Judge).where(Judge.id == judge_id))
        judge_details = result.scalars().first()
        
        if judge_details and judge_details.specialization:
            response = client.get(f"/api/judges/specialization/{judge_details.specialization}")
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0
            assert any(judge["id"] == str(judge_id) for judge in response.json())

async def test_update_judge(client: TestClient, test_data: dict):
    """
    Test updating a judge
    """
    judge = test_data["judge"]
    
    # Update the judge
    update_data = {
        "name": "Updated Test Judge",
        "description": "This is an updated test judge"
    }
    
    response = client.put(f"/api/judges/{judge.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["description"] == update_data["description"]
    assert response.json()["agent_type"] == "JUDGE"