import logging
import json
import httpx
from fastapi import WebSocket
from typing import Dict, Any, List
import os

logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

async def handle_worker_message(client_id: str, message_type: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Handle messages from worker agents
    """
    logger.info(f"Worker {client_id} sent message of type {message_type}")
    
    if message_type == "list_tasks":
        await handle_list_tasks(client_id, data, websocket)
    elif message_type == "get_task_details":
        await handle_get_task_details(client_id, data, websocket)
    elif message_type == "stake_for_task":
        await handle_stake_for_task(client_id, data, websocket)
    elif message_type == "submit_deliverable":
        await handle_submit_deliverable(client_id, data, websocket)
    elif message_type == "list_completed_tasks":
        await handle_list_completed_tasks(client_id, data, websocket)
    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })

async def handle_list_tasks(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    List available tasks for worker agents
    """
    status = data.get("status", "CREATED")  # Default to tasks that are newly created
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/tasks?status={status}")
        tasks = response.json()
        
        # Filter out sensitive information
        filtered_tasks = []
        for task in tasks:
            filtered_tasks.append({
                "id": task["id"],
                "title": task["title"],
                "summary": task["summary"],
                "status": task["status"],
                "deadline": task["deadline"],
                "reward_amount": task["reward_amount"],
                "reward_currency": task["reward_currency"],
                "judges": task["judges"]  # Worker needs to know judges to evaluate trust
            })
        
        await websocket.send_json({
            "type": "tasks_list",
            "tasks": filtered_tasks
        })

async def handle_get_task_details(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Get detailed information about a task, including encrypted payload if staked
    """
    task_id = data.get("task_id")
    agent_id = data.get("agent_id")
    
    if not task_id or not agent_id:
        await websocket.send_json({
            "type": "error",
            "message": "Missing task_id or agent_id"
        })
        return
    
    async with httpx.AsyncClient() as client:
        # Get task details
        task_response = await client.get(f"{API_BASE_URL}/api/tasks/{task_id}")
        task = task_response.json()
        
        # Check if agent has staked for this task
        # In a real implementation, we would check the blockchain
        # For now, we'll just check if the task status is STAKED or later
        if task["status"] in ["STAKED", "IN_PROGRESS", "SUBMITTED", "JUDGED", "COMPLETED"]:
            # Include encrypted payload URL and key
            await websocket.send_json({
                "type": "task_details",
                "task": {
                    "id": task["id"],
                    "title": task["title"],
                    "summary": task["summary"],
                    "encrypted_payload_url": task["encrypted_payload_url"],
                    "encryption_key": task["encryption_key"],  # In real app, this would be encrypted with worker's public key
                    "status": task["status"],
                    "deadline": task["deadline"],
                    "reward_amount": task["reward_amount"],
                    "reward_currency": task["reward_currency"],
                    "judges": task["judges"]
                }
            })
        else:
            # Only include public information
            await websocket.send_json({
                "type": "task_details",
                "task": {
                    "id": task["id"],
                    "title": task["title"],
                    "summary": task["summary"],
                    "status": task["status"],
                    "deadline": task["deadline"],
                    "reward_amount": task["reward_amount"],
                    "reward_currency": task["reward_currency"],
                    "judges": task["judges"]
                },
                "message": "Stake SOL to access full task details"
            })

async def handle_stake_for_task(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Stake SOL for a task to access encrypted details
    """
    task_id = data.get("task_id")
    agent_id = data.get("agent_id")
    amount = data.get("amount")
    
    if not task_id or not agent_id or not amount:
        await websocket.send_json({
            "type": "error",
            "message": "Missing task_id, agent_id, or amount"
        })
        return
    
    async with httpx.AsyncClient() as client:
        # Get agent details
        agent_response = await client.get(f"{API_BASE_URL}/api/agents/{agent_id}")
        agent = agent_response.json()
        
        # Stake SOL
        stake_response = await client.post(
            f"{API_BASE_URL}/api/blockchain/stake",
            json={
                "agent_wallet": agent["wallet_address"],
                "task_id": task_id,
                "amount": amount
            }
        )
        stake = stake_response.json()
        
        # Update task status
        await client.put(
            f"{API_BASE_URL}/api/tasks/{task_id}",
            json={"status": "STAKED"}
        )
        
        # Get updated task details
        task_response = await client.get(f"{API_BASE_URL}/api/tasks/{task_id}")
        task = task_response.json()
        
        await websocket.send_json({
            "type": "stake_confirmed",
            "stake": stake,
            "task": {
                "id": task["id"],
                "title": task["title"],
                "summary": task["summary"],
                "encrypted_payload_url": task["encrypted_payload_url"],
                "encryption_key": task["encryption_key"],  # In real app, this would be encrypted with worker's public key
                "status": task["status"],
                "deadline": task["deadline"],
                "reward_amount": task["reward_amount"],
                "reward_currency": task["reward_currency"],
                "judges": task["judges"]
            }
        })

async def handle_submit_deliverable(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Submit a deliverable for a task
    """
    task_id = data.get("task_id")
    agent_id = data.get("agent_id")
    encrypted_content_url = data.get("encrypted_content_url")
    encryption_keys = data.get("encryption_keys")
    
    if not task_id or not agent_id or not encrypted_content_url or not encryption_keys:
        await websocket.send_json({
            "type": "error",
            "message": "Missing required fields"
        })
        return
    
    async with httpx.AsyncClient() as client:
        # In a real implementation, we would store the deliverable in the database
        # For now, we'll just update the task status
        
        # Update task status
        await client.put(
            f"{API_BASE_URL}/api/tasks/{task_id}",
            json={"status": "SUBMITTED"}
        )
        
        await websocket.send_json({
            "type": "deliverable_submitted",
            "deliverable": {
                "id": f"del_{task_id}_{agent_id}",
                "task_id": task_id,
                "agent_id": agent_id,
                "status": "SUBMITTED",
                "submission_time": "2023-11-01T12:00:00Z"
            }
        })

async def handle_list_completed_tasks(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    List tasks completed by the worker agent
    """
    agent_id = data.get("agent_id")
    
    if not agent_id:
        await websocket.send_json({
            "type": "error",
            "message": "Missing agent_id"
        })
        return
    
    async with httpx.AsyncClient() as client:
        # In a real implementation, we would query the database for tasks completed by this agent
        # For now, we'll just return a mock list
        
        await websocket.send_json({
            "type": "completed_tasks",
            "tasks": [
                {
                    "id": "task123",
                    "title": "Sample completed task",
                    "status": "COMPLETED",
                    "reward_amount": 100.0,
                    "reward_currency": "USDC",
                    "completed_at": "2023-10-15T14:30:00Z",
                    "score": 4.5
                }
            ]
        })