import logging
import json
import httpx
from fastapi import WebSocket
from typing import Dict, Any, List
import os

logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

async def handle_sponsor_message(client_id: str, message_type: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Handle messages from sponsor agents (task creators)
    """
    logger.info(f"Sponsor {client_id} sent message of type {message_type}")
    
    if message_type == "list_judges":
        await handle_list_judges(client_id, data, websocket)
    elif message_type == "create_task":
        await handle_create_task(client_id, data, websocket)
    elif message_type == "list_created_tasks":
        await handle_list_created_tasks(client_id, data, websocket)
    elif message_type == "get_task_deliverables":
        await handle_get_task_deliverables(client_id, data, websocket)
    elif message_type == "get_task_results":
        await handle_get_task_results(client_id, data, websocket)
    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })

async def handle_list_judges(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    List available judges for task creation
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/judges")
        judges = response.json()
        
        await websocket.send_json({
            "type": "judges_list",
            "judges": judges
        })

async def handle_create_task(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Create a new task
    """
    required_fields = ["title", "summary", "encrypted_payload_url", "deadline", 
                       "reward_amount", "reward_currency", "judges"]
    
    for field in required_fields:
        if field not in data:
            await websocket.send_json({
                "type": "error",
                "message": f"Missing required field: {field}"
            })
            return
    
    # Add creator_id to the data
    data["creator_id"] = client_id
    
    async with httpx.AsyncClient() as client:
        # Create task
        task_response = await client.post(
            f"{API_BASE_URL}/api/tasks",
            json=data
        )
        task = task_response.json()
        
        # Mint NFT
        nft_response = await client.post(
            f"{API_BASE_URL}/api/blockchain/mint-nft",
            json={
                "title": task["title"],
                "description": task["summary"],
                "creator_wallet": "creator_wallet_placeholder",  # In real app, get from auth
                "metadata_url": task["encrypted_payload_url"]
            }
        )
        nft = nft_response.json()
        
        # Update task with NFT ID
        # In a real implementation, we would update the task in the database
        
        await websocket.send_json({
            "type": "task_created",
            "task": task,
            "nft": nft
        })

async def handle_list_created_tasks(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    List tasks created by this sponsor
    """
    async with httpx.AsyncClient() as client:
        # In a real implementation, we would query the database for tasks created by this sponsor
        # For now, we'll just filter the tasks by creator_id
        response = await client.get(f"{API_BASE_URL}/api/tasks")
        all_tasks = response.json()
        
        created_tasks = [task for task in all_tasks if task.get("creator_id") == client_id]
        
        await websocket.send_json({
            "type": "created_tasks",
            "tasks": created_tasks
        })

async def handle_get_task_deliverables(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Get deliverables for a task
    """
    task_id = data.get("task_id")
    
    if not task_id:
        await websocket.send_json({
            "type": "error",
            "message": "Missing task_id"
        })
        return
    
    async with httpx.AsyncClient() as client:
        # Get task details
        task_response = await client.get(f"{API_BASE_URL}/api/tasks/{task_id}")
        task = task_response.json()
        
        # Verify this sponsor is the creator of the task
        if task.get("creator_id") != client_id:
            await websocket.send_json({
                "type": "error",
                "message": "You are not the creator of this task"
            })
            return
        
        # In a real implementation, we would query the database for deliverables
        # For now, we'll just return a mock deliverable if the task status is SUBMITTED or later
        if task["status"] in ["SUBMITTED", "JUDGED", "COMPLETED"]:
            deliverables = [
                {
                    "id": f"del_{task_id}_agent123",
                    "agent_id": "agent123",
                    "encrypted_content_url": "https://example.com/encrypted/deliverable1",
                    "encryption_key": "your_decryption_key_here",  # In real app, this would be encrypted with sponsor's public key
                    "submission_time": "2023-11-01T12:00:00Z",
                    "status": task["status"],
                    "scores": {"judge1": 4.5, "judge2": 4.2} if task["status"] in ["JUDGED", "COMPLETED"] else {}
                }
            ]
        else:
            deliverables = []
        
        await websocket.send_json({
            "type": "task_deliverables",
            "task_id": task_id,
            "deliverables": deliverables
        })

async def handle_get_task_results(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Get final results for a completed task
    """
    task_id = data.get("task_id")
    
    if not task_id:
        await websocket.send_json({
            "type": "error",
            "message": "Missing task_id"
        })
        return
    
    async with httpx.AsyncClient() as client:
        # Get task details
        task_response = await client.get(f"{API_BASE_URL}/api/tasks/{task_id}")
        task = task_response.json()
        
        # Verify this sponsor is the creator of the task
        if task.get("creator_id") != client_id:
            await websocket.send_json({
                "type": "error",
                "message": "You are not the creator of this task"
            })
            return
        
        # In a real implementation, we would query the database for results
        # For now, we'll just return mock results if the task is completed
        if task["status"] == "COMPLETED":
            results = {
                "task_id": task_id,
                "winner_agent_id": "agent123",
                "winner_score": 4.35,
                "reward_transaction_id": "tx_abc123",
                "completed_at": "2023-11-05T15:30:00Z",
                "judge_feedback": {
                    "judge1": "Excellent work, very thorough analysis.",
                    "judge2": "Good results but could improve presentation."
                }
            }
        else:
            results = {
                "task_id": task_id,
                "status": task["status"],
                "message": "Task not yet completed"
            }
        
        await websocket.send_json({
            "type": "task_results",
            "results": results
        })