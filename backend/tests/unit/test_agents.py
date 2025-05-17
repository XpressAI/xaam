import pytest
from fastapi.testclient import TestClient
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

# Import the FastAPI app
from app.main import app
from app.db.models.agent import Agent, AgentType

pytestmark = pytest.mark.asyncio

async def test_get_agents(client: TestClient, test_data: dict):
    """
    Test getting all agents
    """
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

async def test_get_agents_by_type(client: TestClient, test_data: dict):
    """
    Test getting agents by type
    """
    # Test worker agents
    response = client.get("/api/agents?agent_type=WORKER")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(agent["agent_type"] == "WORKER" for agent in response.json())
    
    # Test judge agents
    response = client.get("/api/agents?agent_type=JUDGE")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(agent["agent_type"] == "JUDGE" for agent in response.json())

async def test_get_agent_by_id(client: TestClient, test_data: dict):
    """
    Test getting a specific agent by ID
    """
    worker = test_data["worker"]
    
    # Get the specific agent
    response = client.get(f"/api/agents/{worker.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(worker.id)
    assert response.json()["name"] == worker.name

async def test_create_agent(client: TestClient):
    """
    Test creating a new agent
    """
    new_agent = {
        "name": "New Test Agent",
        "description": "This is a new test agent",
        "agent_type": "WORKER",
        "wallet_address": "new_test_wallet",
        "public_key": "new_test_public_key"
    }
    
    response = client.post("/api/agents", json=new_agent)
    assert response.status_code == 201
    
    created_agent = response.json()
    assert created_agent["name"] == new_agent["name"]
    assert created_agent["description"] == new_agent["description"]
    assert created_agent["agent_type"] == new_agent["agent_type"]
    assert created_agent["wallet_address"] == new_agent["wallet_address"]
    assert created_agent["public_key"] == new_agent["public_key"]
    assert created_agent["reputation_score"] == 0.0
    assert created_agent["completed_tasks"] == 0
    assert created_agent["successful_tasks"] == 0

async def test_update_agent(client: TestClient, test_data: dict):
    """
    Test updating an agent
    """
    worker = test_data["worker"]
    
    # Update the agent
    update_data = {
        "name": "Updated Test Worker",
        "description": "This is an updated test worker agent"
    }
    
    response = client.put(f"/api/agents/{worker.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["description"] == update_data["description"]

async def test_update_agent_reputation(client: TestClient, test_data: dict):
    """
    Test updating an agent's reputation
    """
    worker = test_data["worker"]
    
    # Update the agent's reputation
    update_data = {
        "task_completed": True,
        "task_successful": True,
        "reputation_delta": 5.0
    }
    
    response = client.put(f"/api/agents/{worker.id}/reputation", json=update_data)
    assert response.status_code == 200
    assert response.json()["completed_tasks"] == worker.completed_tasks + 1
    assert response.json()["successful_tasks"] == worker.successful_tasks + 1

async def test_get_agent_by_wallet(client: TestClient, test_data: dict):
    """
    Test getting an agent by wallet address
    """
    worker = test_data["worker"]
    
    response = client.get(f"/api/agents/wallet/{worker.wallet_address}")
    assert response.status_code == 200
    assert response.json()["id"] == str(worker.id)
    assert response.json()["wallet_address"] == worker.wallet_address

async def test_search_agents(client: TestClient, test_data: dict):
    """
    Test searching agents
    """
    worker = test_data["worker"]
    
    response = client.get(f"/api/agents/search/{worker.name[:4]}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert any(agent["id"] == str(worker.id) for agent in response.json())

async def test_delete_agent(client: TestClient, db_session: AsyncSession):
    """
    Test deleting an agent
    """
    # First, create a new agent
    new_agent = {
        "name": "Delete Test Agent",
        "description": "This is an agent for testing deletion",
        "agent_type": "WORKER",
        "wallet_address": "delete_test_wallet",
        "public_key": "delete_test_public_key"
    }
    
    create_response = client.post("/api/agents", json=new_agent)
    assert create_response.status_code == 201
    agent_id = create_response.json()["id"]
    
    # Delete the agent
    response = client.delete(f"/api/agents/{agent_id}")
    assert response.status_code == 204
    
    # Verify the agent is deleted
    get_response = client.get(f"/api/agents/{agent_id}")
    assert get_response.status_code == 404