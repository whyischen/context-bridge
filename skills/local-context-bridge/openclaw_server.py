"""OpenClaw Server for ContextBridge Skill.

Provides HTTP/WebSocket server for OpenClaw integration.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from .openclaw_protocol import create_protocol_handler

logger = logging.getLogger(__name__)


class OpenClawServer:
    """OpenClaw server for skill communication."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        """
        Initialize server.
        
        SECURITY: Server only accepts localhost binding to prevent network exposure.
        
        Args:
            host: Server host (must be localhost)
            port: Server port
            
        Raises:
            ValueError: If host is not a localhost address
        """
        # Validate that host is localhost for security
        localhost_addresses = ("127.0.0.1", "localhost", "::1", "[::1]")
        if host not in localhost_addresses:
            raise ValueError(
                f"SECURITY ERROR: Cannot bind to {host}. "
                "The OpenClaw server must only bind to localhost (127.0.0.1) "
                "to prevent exposing local documents to the network."
            )
        
        self.host = host
        self.port = port
        self.protocol_handler = create_protocol_handler()
        self.running = False

    async def handle_message(self, message: str) -> str:
        """
        Handle incoming message.
        
        Args:
            message: JSON-encoded message
            
        Returns:
            JSON-encoded response
        """
        try:
            request = json.loads(message)
            
            # Handle batch requests
            if isinstance(request, list):
                responses = self.protocol_handler.handle_batch_request(request)
            else:
                responses = self.protocol_handler.handle_request(request)
            
            return json.dumps(responses)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            })
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error"
                }
            })

    async def start(self):
        """Start the server."""
        try:
            import websockets
            
            async def handler(websocket, path):
                logger.info(f"Client connected from {websocket.remote_address}")
                try:
                    async for message in websocket:
                        logger.debug(f"Received: {message}")
                        response = await self.handle_message(message)
                        await websocket.send(response)
                except Exception as e:
                    logger.error(f"Error in handler: {e}")
                finally:
                    logger.info(f"Client disconnected from {websocket.remote_address}")
            
            self.running = True
            logger.info(f"Starting OpenClaw server on ws://{self.host}:{self.port}")
            
            async with websockets.serve(handler, self.host, self.port):
                await asyncio.Future()  # Run forever
        except ImportError:
            logger.error("websockets library not installed")
            raise
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            self.running = False
            raise

    def stop(self):
        """Stop the server."""
        self.running = False
        logger.info("Server stopped")


def run_server(host: str = "127.0.0.1", port: int = 8765):
    """
    Run the OpenClaw server.
    
    SECURITY WARNING: This server should only be bound to localhost (127.0.0.1)
    for local-only access. Binding to 0.0.0.0 or other network interfaces will
    expose the service to the network and allow unauthorized access to local documents.
    
    Args:
        host: Server host (default: 127.0.0.1 - localhost only)
        port: Server port (default: 8765)
        
    Raises:
        ValueError: If host is not a localhost address
    """
    # Validate that host is localhost for security
    localhost_addresses = ("127.0.0.1", "localhost", "::1", "[::1]")
    if host not in localhost_addresses:
        raise ValueError(
            f"SECURITY ERROR: Cannot bind to {host}. "
            "The OpenClaw server must only bind to localhost (127.0.0.1) "
            "to prevent exposing local documents to the network. "
            "If you need network access, use a proper authentication layer."
        )
    
    server = OpenClawServer(host, port)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Server interrupted")
        server.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_server()
