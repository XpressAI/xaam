import asyncio
import logging
import os
import json
import sys
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Protocol compliance check
def check_protocol_compliance():
    """
    Check if the developer has acknowledged reading the XAAM protocol whitepaper.
    This is a safeguard to ensure all implementations adhere to the protocol specification.
    """
    whitepaper_read = os.getenv("XAAM_WHITEPAPER_READ", "").lower() == "true"
    
    if not whitepaper_read:
        warning_message = """
        ╔════════════════════════════════════════════════════════════════════════════╗
        ║                               WARNING                                      ║
        ║                                                                            ║
        ║  You MUST read the XAAM Protocol Whitepaper before proceeding with         ║
        ║  implementation. The whitepaper contains the definitive protocol           ║
        ║  specification that all implementations must adhere to.                    ║
        ║                                                                            ║
        ║  To acknowledge that you have read and understood the whitepaper,          ║
        ║  set the XAAM_WHITEPAPER_READ environment variable to "true".              ║
        ║                                                                            ║
        ║  Example:                                                                  ║
        ║    export XAAM_WHITEPAPER_READ=true                                        ║
        ║                                                                            ║
        ║  The whitepaper can be found at: XAAM_Whitepaper.md                        ║
        ╚════════════════════════════════════════════════════════════════════════════╝
        """
        logger.warning(warning_message)
        print(warning_message, file=sys.stderr)
        
        # In development mode, we'll just show a warning
        # In production, you might want to raise an exception or exit
        if os.getenv("ENVIRONMENT", "development") == "production":
            raise RuntimeError("XAAM Protocol Whitepaper must be read before running in production")
    else:
        logger.info("XAAM Protocol Whitepaper compliance check passed")

# Create FastAPI app
app = FastAPI(
    title="XAAM MCP Server",
    description="Model Context Protocol server for XAAM",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

# Connected clients
connected_clients = {}

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

# WebSocket endpoint for MCP connections
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = None
    
    try:
        # Wait for initial connection message with client ID
        data = await websocket.receive_json()
        client_id = data.get("client_id")
        client_type = data.get("client_type")  # "worker", "sponsor", or "judge"
        
        if not client_id or not client_type:
            await websocket.send_json({"error": "Missing client_id or client_type"})
            await websocket.close()
            return
        
        # Store client connection
        connected_clients[client_id] = {
            "websocket": websocket,
            "type": client_type
        }
        
        logger.info(f"Client {client_id} ({client_type}) connected")
        await websocket.send_json({"status": "connected", "message": f"Welcome, {client_id}"})
        
        # Main message loop
        while True:
            data = await websocket.receive_json()
            await process_message(client_id, client_type, data, websocket)
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
        if client_id and client_id in connected_clients:
            del connected_clients[client_id]
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
        if client_id and client_id in connected_clients:
            del connected_clients[client_id]

async def process_message(client_id: str, client_type: str, data: Dict[str, Any], websocket: WebSocket):
    """
    Process incoming messages based on client type and message type
    """
    message_type = data.get("type")
    
    if not message_type:
        await websocket.send_json({"error": "Missing message type"})
        return
    
    # Import handlers based on client type
    if client_type == "worker":
        from interfaces.worker import handle_worker_message
        await handle_worker_message(client_id, message_type, data, websocket)
    elif client_type == "sponsor":
        from interfaces.sponsor import handle_sponsor_message
        await handle_sponsor_message(client_id, message_type, data, websocket)
    elif client_type == "judge":
        from interfaces.judge import handle_judge_message
        await handle_judge_message(client_id, message_type, data, websocket)
    else:
        await websocket.send_json({"error": f"Unknown client type: {client_type}"})

# MCP tool endpoints
@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, data: Dict[str, Any]):
    """
    Execute an MCP tool
    """
    if tool_name == "list_tasks":
        return await list_tasks(data.get("status"))
    elif tool_name == "get_task_details":
        return await get_task_details(data.get("task_id"))
    elif tool_name == "stake_for_task":
        return await stake_for_task(
            data.get("task_id"),
            data.get("agent_id"),
            data.get("amount")
        )
    elif tool_name == "submit_deliverable":
        return await submit_deliverable(
            data.get("task_id"),
            data.get("agent_id"),
            data.get("encrypted_content_url"),
            data.get("encryption_keys")
        )
    elif tool_name == "create_task":
        return await create_task(data)
    elif tool_name == "judge_deliverable":
        return await judge_deliverable(
            data.get("task_id"),
            data.get("agent_id"),
            data.get("judge_id"),
            data.get("score"),
            data.get("feedback")
        )
    else:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

# Tool implementations
async def list_tasks(status: Optional[str] = None):
    """
    List available tasks
    """
    async with httpx.AsyncClient() as client:
        url = f"{API_BASE_URL}/api/tasks"
        if status:
            url += f"?status={status}"
        response = await client.get(url)
        return response.json()

async def get_task_details(task_id: str):
    """
    Get detailed information about a task
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/tasks/{task_id}")
        return response.json()

async def stake_for_task(task_id: str, agent_id: str, amount: float):
    """
    Stake SOL for a task
    """
    # Get agent wallet address
    async with httpx.AsyncClient() as client:
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
        
        # Update task status
        await client.put(
            f"{API_BASE_URL}/api/tasks/{task_id}",
            json={"status": "STAKED"}
        )
        
        return stake_response.json()

async def submit_deliverable(task_id: str, agent_id: str, encrypted_content_url: str, encryption_keys: Dict[str, str]):
    """
    Submit a deliverable for a task
    """
    async with httpx.AsyncClient() as client:
        # Create deliverable record
        deliverable_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "encrypted_content_url": encrypted_content_url,
            "encryption_keys": encryption_keys
        }
        
        # In a real implementation, we would store this in the database
        # For now, we'll just return a success message
        
        # Update task status
        await client.put(
            f"{API_BASE_URL}/api/tasks/{task_id}",
            json={"status": "SUBMITTED"}
        )
        
        return {
            "id": f"del_{task_id}_{agent_id}",
            "status": "SUBMITTED",
            "submission_time": "2023-11-01T12:00:00Z"
        }

async def create_task(data: Dict[str, Any]):
    """
    Create a new task
    """
    async with httpx.AsyncClient() as client:
        # Create task
        response = await client.post(
            f"{API_BASE_URL}/api/tasks",
            json=data
        )
        task = response.json()
        
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
        
        return {
            "task": task,
            "nft": nft_response.json()
        }

async def judge_deliverable(task_id: str, agent_id: str, judge_id: str, score: float, feedback: str):
    """
    Judge a deliverable
    """
    async with httpx.AsyncClient() as client:
        # Submit score
        response = await client.post(
            f"{API_BASE_URL}/api/judges/{judge_id}/score",
            json={
                "task_id": task_id,
                "agent_id": agent_id,
                "score": score,
                "feedback": feedback
            }
        )
        
        return response.json()

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting XAAM MCP Server")
    
    # Check protocol compliance
    check_protocol_compliance()

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=9000, reload=True)