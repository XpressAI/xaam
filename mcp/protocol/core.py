import logging
import json
from typing import Dict, Any, List, Optional, Callable, Awaitable
import asyncio

logger = logging.getLogger(__name__)

class MCPProtocol:
    """
    Core implementation of the Model Context Protocol for XAAM
    """
    
    def __init__(self):
        self.tools = {}
        self.resources = {}
    
    def register_tool(self, name: str, handler: Callable[[Dict[str, Any]], Awaitable[Any]]):
        """
        Register a tool with the protocol
        """
        self.tools[name] = handler
        logger.info(f"Registered tool: {name}")
    
    def register_resource(self, uri: str, resource: Any):
        """
        Register a resource with the protocol
        """
        self.resources[uri] = resource
        logger.info(f"Registered resource: {uri}")
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered tool
        """
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        
        logger.info(f"Executing tool: {name}")
        try:
            result = await self.tools[name](arguments)
            return {
                "status": "success",
                "result": result
            }
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def access_resource(self, uri: str) -> Dict[str, Any]:
        """
        Access a registered resource
        """
        if uri not in self.resources:
            raise ValueError(f"Resource not found: {uri}")
        
        logger.info(f"Accessing resource: {uri}")
        try:
            resource = self.resources[uri]
            if callable(resource):
                result = await resource()
            else:
                result = resource
                
            return {
                "status": "success",
                "resource": result
            }
        except Exception as e:
            logger.error(f"Error accessing resource {uri}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def parse_message(self, message: str) -> Dict[str, Any]:
        """
        Parse an incoming MCP message
        """
        try:
            data = json.loads(message)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing message: {str(e)}")
            return {
                "status": "error",
                "error": "Invalid JSON message"
            }
    
    def format_response(self, data: Dict[str, Any]) -> str:
        """
        Format an outgoing MCP response
        """
        try:
            return json.dumps(data)
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return json.dumps({
                "status": "error",
                "error": "Error formatting response"
            })
    
    async def handle_message(self, message: str) -> str:
        """
        Handle an incoming MCP message
        """
        data = self.parse_message(message)
        
        if "type" not in data:
            return self.format_response({
                "status": "error",
                "error": "Missing message type"
            })
        
        message_type = data["type"]
        
        if message_type == "tool_call":
            if "tool" not in data or "arguments" not in data:
                return self.format_response({
                    "status": "error",
                    "error": "Missing tool name or arguments"
                })
            
            tool_name = data["tool"]
            arguments = data["arguments"]
            
            result = await self.execute_tool(tool_name, arguments)
            return self.format_response(result)
        
        elif message_type == "resource_access":
            if "uri" not in data:
                return self.format_response({
                    "status": "error",
                    "error": "Missing resource URI"
                })
            
            uri = data["uri"]
            result = await self.access_resource(uri)
            return self.format_response(result)
        
        else:
            return self.format_response({
                "status": "error",
                "error": f"Unknown message type: {message_type}"
            })