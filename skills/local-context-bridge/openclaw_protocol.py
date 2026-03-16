"""OpenClaw Protocol Handler for ContextBridge Skill.

Handles OpenClaw RPC protocol for skill communication.
"""

import json
import logging
from typing import Dict, Any, Optional, Callable
from .openclaw_adapter import get_adapter, initialize_adapter

logger = logging.getLogger(__name__)


class OpenClawProtocolHandler:
    """Handle OpenClaw protocol requests."""

    def __init__(self):
        """Initialize protocol handler."""
        self.adapter = get_adapter()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle OpenClaw protocol request.
        
        Args:
            request: OpenClaw protocol request
            
        Returns:
            OpenClaw protocol response
        """
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            logger.info(f"Handling request: {method}")
            
            if method == "skill.initialize":
                result = initialize_adapter(params)
            elif method == "skill.getInfo":
                result = self.adapter.get_skill_info()
            elif method == "skill.getStatus":
                result = self.adapter.get_status_info()
            elif method == "skill.call":
                capability = params.get("capability")
                capability_params = params.get("parameters", {})
                result = self.adapter.call_capability(capability, capability_params)
            elif method == "skill.shutdown":
                result = self.adapter.shutdown()
            else:
                result = {
                    "status": "error",
                    "message": f"Unknown method: {method}"
                }
            
            return self._format_response(result, request_id)
        except Exception as e:
            logger.error(f"Protocol error: {e}", exc_info=True)
            return self._format_error_response(str(e), request_id)

    def _format_response(
        self,
        result: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format successful response."""
        response = {
            "jsonrpc": "2.0",
            "result": result
        }
        if request_id:
            response["id"] = request_id
        return response

    def _format_error_response(
        self,
        error_message: str,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format error response."""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -1,
                "message": error_message
            }
        }
        if request_id:
            response["id"] = request_id
        return response

    def handle_batch_request(
        self,
        requests: list
    ) -> list:
        """Handle batch requests."""
        return [self.handle_request(req) for req in requests]


def create_protocol_handler() -> OpenClawProtocolHandler:
    """Create a new protocol handler."""
    return OpenClawProtocolHandler()
