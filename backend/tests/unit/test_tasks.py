import pytest
from fastapi.testclient import TestClient
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

# Import the FastAPI app
from app.main import app
from app.db.models.task import Task, TaskStatus

pytestmark = pytest.mark.asyncio

async def test_get_tasks(client: TestClient, test_data: dict):
    """
    Test getting all tasks
    """
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

async def test_get_task_by_id(client: TestClient, test_data: dict):
    """
    Test getting a specific task by ID
    """
    task = test_data["task"]
    
    # Get the specific task
    response = client.get(f"/api/tasks/{task.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(task.id)
    assert response.json()["title"] == task.title

async def test_create_task(client: TestClient, test_data: dict):
    """
    Test creating a new task
    """
    judge = test_data["judge"]
    
    new_task = {
        "title": "New Test Task",
        "summary": "This is a new test task",
        "encrypted_payload_url": "https://example.com/encrypted/new-test",
        "creator_id": str(judge.id),
        "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
        "reward_amount": 75.0,
        "reward_currency": "USDC",
        "judges": [str(judge.id)]
    }
    
    response = client.post("/api/tasks", json=new_task)
    assert response.status_code == 201
    
    created_task = response.json()
    assert created_task["title"] == new_task["title"]
    assert created_task["summary"] == new_task["summary"]
    assert created_task["encrypted_payload_url"] == new_task["encrypted_payload_url"]
    assert created_task["creator_id"] == new_task["creator_id"]
    assert created_task["reward_amount"] == new_task["reward_amount"]
    assert created_task["reward_currency"] == new_task["reward_currency"]
    assert created_task["status"] == "CREATED"

async def test_update_task_status(client: TestClient, test_data: dict):
    """
    Test updating a task's status
    """
    task = test_data["task"]
    
    # Update the task status
    update_data = {
        "status": "STAKED"
    }
    
    response = client.put(f"/api/tasks/{task.id}/status", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "STAKED"

async def test_get_tasks_by_creator(client: TestClient, test_data: dict):
    """
    Test getting tasks by creator
    """
    judge = test_data["judge"]
    
    response = client.get(f"/api/tasks/creator/{judge.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["creator_id"] == str(judge.id)

async def test_get_tasks_by_judge(client: TestClient, test_data: dict):
    """
    Test getting tasks by judge
    """
    judge = test_data["judge"]
    
    response = client.get(f"/api/tasks/judge/{judge.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

async def test_delete_task(client: TestClient, db_session: AsyncSession, test_data: dict):
    """
    Test deleting a task
    """
    judge = test_data["judge"]
    
    # First, create a new task
    new_task = {
        "title": "Delete Test Task",
        "summary": "This is a task for testing deletion",
        "encrypted_payload_url": "https://example.com/encrypted/delete-test",
        "creator_id": str(judge.id),
        "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
        "reward_amount": 45.0,
        "reward_currency": "USDC",
        "judges": [str(judge.id)]
    }
    
    create_response = client.post("/api/tasks", json=new_task)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204
    
    # Verify the task is deleted
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404