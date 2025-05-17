import pytest
import json
import asyncio
from unittest.mock import AsyncMock, patch

from protocol.core import MCPProtocol

@pytest.fixture
def mcp_protocol():
    """
    Create an instance of the MCPProtocol for testing
    """
    return MCPProtocol()

@pytest.mark.asyncio
async def test_register_and_execute_tool(mcp_protocol):
    """
    Test registering and executing a tool
    """
    # Create a mock tool handler
    mock_handler = AsyncMock(return_value={"result": "success"})
    
    # Register the tool
    mcp_protocol.register_tool("test_tool", mock_handler)
    
    # Verify the tool was registered
    assert "test_tool" in mcp_protocol.tools
    
    # Execute the tool
    result = await mcp_protocol.execute_tool("test_tool", {"param": "value"})
    
    # Verify the tool was called with the correct arguments
    mock_handler.assert_called_once_with({"param": "value"})
    
    # Verify the result
    assert result["status"] == "success"
    assert result["result"] == {"result": "success"}

@pytest.mark.asyncio
async def test_register_and_access_resource(mcp_protocol):
    """
    Test registering and accessing a resource
    """
    # Create a mock resource
    mock_resource = {"data": "test_data"}
    
    # Register the resource
    mcp_protocol.register_resource("test://resource", mock_resource)
    
    # Verify the resource was registered
    assert "test://resource" in mcp_protocol.resources
    
    # Access the resource
    result = await mcp_protocol.access_resource("test://resource")
    
    # Verify the result
    assert result["status"] == "success"
    assert result["resource"] == mock_resource

@pytest.mark.asyncio
async def test_handle_tool_call_message(mcp_protocol):
    """
    Test handling a tool call message
    """
    # Create a mock tool handler
    mock_handler = AsyncMock(return_value={"result": "success"})
    
    # Register the tool
    mcp_protocol.register_tool("test_tool", mock_handler)
    
    # Create a tool call message
    message = json.dumps({
        "type": "tool_call",
        "tool": "test_tool",
        "arguments": {"param": "value"}
    })
    
    # Handle the message
    response = await mcp_protocol.handle_message(message)
    
    # Parse the response
    response_data = json.loads(response)
    
    # Verify the response
    assert response_data["status"] == "success"
    assert response_data["result"] == {"result": "success"}

@pytest.mark.asyncio
async def test_handle_resource_access_message(mcp_protocol):
    """
    Test handling a resource access message
    """
    # Create a mock resource
    mock_resource = {"data": "test_data"}
    
    # Register the resource
    mcp_protocol.register_resource("test://resource", mock_resource)
    
    # Create a resource access message
    message = json.dumps({
        "type": "resource_access",
        "uri": "test://resource"
    })
    
    # Handle the message
    response = await mcp_protocol.handle_message(message)
    
    # Parse the response
    response_data = json.loads(response)
    
    # Verify the response
    assert response_data["status"] == "success"
    assert response_data["resource"] == mock_resource

@pytest.mark.asyncio
async def test_handle_invalid_message(mcp_protocol):
    """
    Test handling an invalid message
    """
    # Create an invalid message (missing type)
    message = json.dumps({
        "foo": "bar"
    })
    
    # Handle the message
    response = await mcp_protocol.handle_message(message)
    
    # Parse the response
    response_data = json.loads(response)
    
    # Verify the response
    assert response_data["status"] == "error"
    assert "Missing message type" in response_data["error"]

@pytest.mark.asyncio
async def test_handle_unknown_message_type(mcp_protocol):
    """
    Test handling a message with an unknown type
    """
    # Create a message with an unknown type
    message = json.dumps({
        "type": "unknown_type",
        "data": "test_data"
    })
    
    # Handle the message
    response = await mcp_protocol.handle_message(message)
    
    # Parse the response
    response_data = json.loads(response)
    
    # Verify the response
    assert response_data["status"] == "error"
    assert "Unknown message type" in response_data["error"]

@pytest.mark.asyncio
async def test_execute_nonexistent_tool(mcp_protocol):
    """
    Test executing a tool that doesn't exist
    """
    with pytest.raises(ValueError) as excinfo:
        await mcp_protocol.execute_tool("nonexistent_tool", {})
    
    assert "Tool not found" in str(excinfo.value)

@pytest.mark.asyncio
async def test_access_nonexistent_resource(mcp_protocol):
    """
    Test accessing a resource that doesn't exist
    """
    with pytest.raises(ValueError) as excinfo:
        await mcp_protocol.access_resource("nonexistent://resource")
    
    assert "Resource not found" in str(excinfo.value)

@pytest.mark.asyncio
async def test_callable_resource(mcp_protocol):
    """
    Test registering and accessing a callable resource
    """
    # Create a mock callable resource
    mock_resource = AsyncMock(return_value={"data": "dynamic_data"})
    
    # Register the resource
    mcp_protocol.register_resource("callable://resource", mock_resource)
    
    # Access the resource
    result = await mcp_protocol.access_resource("callable://resource")
    
    # Verify the resource was called
    mock_resource.assert_called_once()
    
    # Verify the result
    assert result["status"] == "success"
    assert result["resource"] == {"data": "dynamic_data"}