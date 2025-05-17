import logging
import json
import httpx
from fastapi import WebSocket
from typing import Dict, Any, List
import os

logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

async def handle_judge_message(client_id: str, message_type: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Handle messages from judge agents
    """
    logger.info(f"Judge {client_id} sent message of type {message_type}")
    
    if message_type == "list_assigned_tasks":
        await handle_list_assigned_tasks(client_id, data, websocket)
    elif message_type == "get_task_deliverables":
        await handle_get_task_deliverables(client_id, data, websocket)
    elif message_type == "submit_score":
        await handle_submit_score(client_id, data, websocket)
    elif message_type == "get_judge_stats":
        await handle_get_judge_stats(client_id, data, websocket)
    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })

async def handle_list_assigned_tasks(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    List tasks assigned to this judge
    """
    judge_id = data.get("judge_id", client_id)
    
    async with httpx.AsyncClient() as client:
        # Get tasks assigned to this judge
        response = await client.get(f"{API_BASE_URL}/api/judges/{judge_id}/tasks")
        tasks = response.json()
        
        await websocket.send_json({
            "type": "assigned_tasks",
            "tasks": tasks
        })

async def handle_get_task_deliverables(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Get deliverables for a task that needs judging
    """
    task_id = data.get("task_id")
    judge_id = data.get("judge_id", client_id)
    
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
        
        # Verify this judge is assigned to the task
        if judge_id not in task.get("judges", []):
            await websocket.send_json({
                "type": "error",
                "message": "You are not assigned to judge this task"
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
                    "encryption_key": "your_decryption_key_here",  # In real app, this would be encrypted with judge's public key
                    "submission_time": "2023-11-01T12:00:00Z",
                    "status": "SUBMITTED"
                }
            ]
        else:
            deliverables = []
        
        await websocket.send_json({
            "type": "task_deliverables",
            "task_id": task_id,
            "deliverables": deliverables
        })

async def handle_submit_score(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Submit a score and feedback for a task deliverable
    """
    task_id = data.get("task_id")
    agent_id = data.get("agent_id")
    judge_id = data.get("judge_id", client_id)
    score = data.get("score")
    feedback = data.get("feedback")
    
    if not all([task_id, agent_id, score, feedback]):
        await websocket.send_json({
            "type": "error",
            "message": "Missing required fields"
        })
        return
    
    # Validate score
    try:
        score_value = float(score)
        if not (0 <= score_value <= 5):
            raise ValueError("Score must be between 0 and 5")
    except ValueError as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        return
    
    async with httpx.AsyncClient() as client:
        # Submit score
        response = await client.post(
            f"{API_BASE_URL}/api/judges/{judge_id}/score",
            json={
                "task_id": task_id,
                "agent_id": agent_id,
                "score": score_value,
                "feedback": feedback
            }
        )
        result = response.json()
        
        # In a real implementation, we would check if all judges have submitted scores
        # and update the task status accordingly
        
        await websocket.send_json({
            "type": "score_submitted",
            "result": result
        })

async def handle_get_judge_stats(client_id: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Get statistics about this judge's activity
    """
    judge_id = data.get("judge_id", client_id)
    
    async with httpx.AsyncClient() as client:
        # Get judge details
        judge_response = await client.get(f"{API_BASE_URL}/api/judges/{judge_id}")
        judge = judge_response.json()
        
        # In a real implementation, we would calculate statistics from the database
        # For now, we'll just return mock statistics
        stats = {
            "total_tasks_judged": judge.get("completed_tasks", 0),
            "average_score_given": 4.2,
            "reputation_score": judge.get("reputation_score", 0),
            "earnings": {
                "total": 250.0,
                "currency": "USDC",
                "last_month": 75.0
            },
            "response_time": {
                "average_hours": 12.5,
                "last_month_hours": 10.2
            }
        }
        
        await websocket.send_json({
            "type": "judge_stats",
            "stats": stats
        })