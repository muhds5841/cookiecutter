"""
WebSocket server for the Process service.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Set, Optional
from pathlib import Path

# Add parent directory to path to enable imports from process and core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

from process.process import Process
from core.config import load_config
from core.logging import get_logger, configure_logging


class WebSocketServer:
    """WebSocket server for the Process service."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the WebSocket server.
        
        Args:
            config: Server configuration
        """
        self.config = config or load_config("websocket")
        self.logger = get_logger("websocket.server")
        self.process = Process()
        
        # WebSocket configuration
        self.host = os.environ.get("WEBSOCKET_HOST", "0.0.0.0")
        self.port = int(os.environ.get("WEBSOCKET_PORT", "6789"))
        self.max_connections = int(os.environ.get("WEBSOCKET_MAX_CONNECTIONS", "100"))
        self.ping_interval = int(os.environ.get("WEBSOCKET_PING_INTERVAL", "30"))
        self.ping_timeout = int(os.environ.get("WEBSOCKET_PING_TIMEOUT", "10"))
        self.close_timeout = int(os.environ.get("WEBSOCKET_CLOSE_TIMEOUT", "10"))
        self.max_message_size = int(os.environ.get("WEBSOCKET_MAX_MESSAGE_SIZE", "1048576"))
        self.enable_compression = os.environ.get("WEBSOCKET_ENABLE_COMPRESSION", "true").lower() == "true"
        self.compression_level = int(os.environ.get("WEBSOCKET_COMPRESSION_LEVEL", "6"))
        
        # Active connections
        self.active_connections: Set[WebSocketServerProtocol] = set()
        
        self.logger.info(f"Initializing WebSocket server on {self.host}:{self.port}")
    
    async def register(self, websocket: WebSocketServerProtocol):
        """Register a new WebSocket connection."""
        self.active_connections.add(websocket)
        self.logger.info(f"New connection registered. Active connections: {len(self.active_connections)}")
    
    async def unregister(self, websocket: WebSocketServerProtocol):
        """Unregister a WebSocket connection."""
        self.active_connections.remove(websocket)
        self.logger.info(f"Connection closed. Active connections: {len(self.active_connections)}")
    
    async def handle_process_request(self, websocket: WebSocketServerProtocol, payload: Dict[str, Any]):
        """Handle a process request."""
        try:
            # Check if payload contains required fields
            if "text" not in payload:
                await self.send_error(websocket, "Missing required field 'text'", payload.get("request_id"))
                return
            
            # Get parameters
            text = payload["text"]
            options = payload.get("options", {})
            request_id = payload.get("request_id", "")
            
            # Process the text
            self.logger.info(f"Processing text: {text[:50]}...")
            result = self.process.process_text(text, **options)
            
            # Prepare response
            response = {
                "request_id": request_id,
                "result_id": result.result_id,
                "format": result.format,
                "data": result.data,
                "metadata": result.metadata
            }
            
            # Send response
            await websocket.send(json.dumps(response))
            self.logger.info(f"Sent response for request_id: {request_id}")
        
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            await self.send_error(websocket, str(e), payload.get("request_id"))
    
    async def handle_resources_request(self, websocket: WebSocketServerProtocol, payload: Dict[str, Any]):
        """Handle a resources request."""
        try:
            # Get parameters
            request_id = payload.get("request_id", "")
            
            # Get resources
            resources = self.process.get_resources()
            
            # Prepare response
            response = {
                "request_id": request_id,
                "resources": resources
            }
            
            # Send response
            await websocket.send(json.dumps(response))
            self.logger.info(f"Sent resources for request_id: {request_id}")
        
        except Exception as e:
            self.logger.error(f"Error retrieving resources: {str(e)}")
            await self.send_error(websocket, str(e), payload.get("request_id"))
    
    async def send_error(self, websocket: WebSocketServerProtocol, error_message: str, request_id: str = ""):
        """Send an error message."""
        error_response = {
            "request_id": request_id,
            "error": error_message
        }
        
        await websocket.send(json.dumps(error_response))
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a WebSocket connection."""
        await self.register(websocket)
        
        try:
            async for message in websocket:
                try:
                    # Parse JSON message
                    payload = json.loads(message)
                    
                    # Get message type
                    message_type = payload.get("type", "process")
                    
                    # Handle different message types
                    if message_type == "process":
                        await self.handle_process_request(websocket, payload)
                    elif message_type == "resources":
                        await self.handle_resources_request(websocket, payload)
                    else:
                        self.logger.warning(f"Unknown message type: {message_type}")
                        await self.send_error(
                            websocket, 
                            f"Unknown message type: {message_type}", 
                            payload.get("request_id")
                        )
                
                except json.JSONDecodeError:
                    self.logger.error("Invalid JSON format in message")
                    await self.send_error(websocket, "Invalid JSON format")
                except Exception as e:
                    self.logger.error(f"Error handling message: {str(e)}")
                    await self.send_error(websocket, f"Error handling message: {str(e)}")
        
        except ConnectionClosed:
            self.logger.info("Connection closed")
        finally:
            await self.unregister(websocket)
    
    async def start(self):
        """Start the WebSocket server."""
        # Configure WebSocket server
        extra_kwargs = {}
        if self.enable_compression:
            extra_kwargs["compression"] = self.compression_level
        
        # Create server
        server = await websockets.serve(
            self.handle_connection,
            self.host,
            self.port,
            max_size=self.max_message_size,
            ping_interval=self.ping_interval,
            ping_timeout=self.ping_timeout,
            close_timeout=self.close_timeout,
            max_queue=self.max_connections,
            **extra_kwargs
        )
        
        self.logger.info(f"WebSocket server started on {self.host}:{self.port}")
        
        # Keep server running
        await server.wait_closed()


async def main():
    """Main function for the WebSocket server."""
    # Configure logging
    log_level = os.environ.get("WEBSOCKET_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)
    
    # Start WebSocket server
    server = WebSocketServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
