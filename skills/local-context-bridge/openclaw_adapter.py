"""OpenClaw Skill Adapter for Local ContextBridge.

This module provides the integration layer between OpenClaw and the ContextBridge Skill.
It handles:
- Skill lifecycle management
- OpenClaw protocol compliance
- Request/response transformation
- Error handling and logging
"""

import json
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from .skill import LocalContextBridgeSkill

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillStatus(Enum):
    """Skill lifecycle status."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"


class OpenClawAdapter:
    """
    OpenClaw Skill Adapter for ContextBridge.
    
    Implements the OpenClaw Skill protocol and manages the lifecycle
    of the LocalContextBridgeSkill.
    """

    def __init__(self):
        """Initialize the adapter."""
        self.skill = LocalContextBridgeSkill()
        self.status = SkillStatus.UNINITIALIZED
        self.error_message: Optional[str] = None
        self.initialized = False

    def get_skill_info(self) -> Dict[str, Any]:
        """
        Get skill information for OpenClaw discovery.
        
        Returns:
            Skill metadata and capabilities
        """
        return {
            "id": "local-context-bridge",
            "name": "Local ContextBridge",
            "version": "1.0.0",
            "description": "Local document search and context management for AI agents",
            "author": "whyischen",
            "license": "MIT",
            "capabilities": [
                {
                    "name": "search_documents",
                    "description": "Search through local documents",
                    "parameters": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                            "required": True
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5,
                            "required": False
                        }
                    }
                },
                {
                    "name": "setup_environment",
                    "description": "Setup ContextBridge environment",
                    "parameters": {
                        "workspace_dir": {
                            "type": "string",
                            "description": "Custom workspace directory",
                            "required": False
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["auto", "embedded", "external"],
                            "description": "Setup mode",
                            "default": "auto",
                            "required": False
                        }
                    }
                },
                {
                    "name": "detect_environment",
                    "description": "Detect user environment and available services",
                    "parameters": {}
                },
                {
                    "name": "add_watch_directory",
                    "description": "Add directory to watch list",
                    "parameters": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to monitor",
                            "required": True
                        }
                    }
                },
                {
                    "name": "remove_watch_directory",
                    "description": "Remove directory from watch list",
                    "parameters": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to remove",
                            "required": True
                        }
                    }
                },
                {
                    "name": "get_watch_directories",
                    "description": "Get list of monitored directories",
                    "parameters": {}
                },
                {
                    "name": "get_status",
                    "description": "Get current skill status",
                    "parameters": {}
                }
            ],
            "status": self.status.value,
            "initialized": self.initialized
        }

    def initialize(self, config: Optional[Dict[str, Any]] = None, auto_setup: bool = False) -> Dict[str, Any]:
        """
        Initialize the skill.
        
        IMPORTANT: auto_setup is now False by default for security.
        Users must explicitly enable auto_setup or manually call setup_environment().
        
        Args:
            config: Optional configuration overrides
            auto_setup: Enable automatic setup (default: False for security)
                       Set to True only after reviewing the operations
            
        Returns:
            Initialization result
        """
        try:
            self.status = SkillStatus.INITIALIZING
            logger.info(f"Initializing Local ContextBridge Skill (auto_setup={auto_setup})")
            
            # Initialize the skill with specified auto_setup setting
            result = self.skill.initialize(auto_setup=auto_setup)
            
            if result["status"] == "success":
                self.status = SkillStatus.READY
                self.initialized = True
                self.error_message = None
                logger.info("Skill initialized successfully")
            elif result["status"] == "not_configured":
                self.status = SkillStatus.UNINITIALIZED
                self.initialized = False
                self.error_message = result.get("message", "Not configured")
                logger.info(f"Skill not configured: {self.error_message}")
            else:
                self.status = SkillStatus.ERROR
                self.error_message = result.get("message", "Unknown error")
                logger.error(f"Skill initialization failed: {self.error_message}")
            
            return {
                "status": result["status"],
                "message": result.get("message", ""),
                "skill_status": self.status.value,
                "initialized": self.initialized
            }
        except Exception as e:
            self.status = SkillStatus.ERROR
            self.error_message = str(e)
            logger.error(f"Initialization error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Initialization failed: {e}",
                "skill_status": self.status.value
            }

    def call_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a skill capability.
        
        Args:
            capability_name: Name of the capability to call
            parameters: Parameters for the capability
            
        Returns:
            Capability execution result
        """
        if not self.initialized:
            return {
                "status": "error",
                "message": "Skill not initialized. Call initialize() first."
            }
        
        try:
            logger.info(f"Calling capability: {capability_name}")
            
            # Route to appropriate capability handler
            if capability_name == "search_documents":
                return self._handle_search_documents(parameters)
            elif capability_name == "setup_environment":
                return self._handle_setup_environment(parameters)
            elif capability_name == "detect_environment":
                return self._handle_detect_environment(parameters)
            elif capability_name == "add_watch_directory":
                return self._handle_add_watch_directory(parameters)
            elif capability_name == "remove_watch_directory":
                return self._handle_remove_watch_directory(parameters)
            elif capability_name == "get_watch_directories":
                return self._handle_get_watch_directories(parameters)
            elif capability_name == "get_status":
                return self._handle_get_status(parameters)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown capability: {capability_name}"
                }
        except Exception as e:
            logger.error(f"Error calling capability {capability_name}: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Capability execution failed: {e}"
            }

    def _handle_search_documents(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_documents capability."""
        query = parameters.get("query")
        if not query:
            return {
                "status": "error",
                "message": "Missing required parameter: query"
            }
        
        top_k = parameters.get("top_k", 5)
        result = self.skill.search_documents(query, top_k=top_k)
        
        # Transform result for OpenClaw
        return {
            "status": result["status"],
            "message": result.get("message", ""),
            "results": result.get("results", []),
            "count": result.get("count", 0)
        }

    def _handle_setup_environment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle setup_environment capability."""
        workspace_dir = parameters.get("workspace_dir")
        mode = parameters.get("mode", "auto")
        
        result = self.skill.setup_environment(workspace_dir, mode)
        
        return {
            "status": result["status"],
            "message": result.get("message", ""),
            "config": result.get("config", {})
        }

    def _handle_detect_environment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle detect_environment capability."""
        result = self.skill.detect_environment()
        
        return {
            "status": result["status"],
            "message": result.get("message", ""),
            "environment": result.get("environment", {}),
            "summary": result.get("summary", "")
        }

    def _handle_add_watch_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_watch_directory capability."""
        path = parameters.get("path")
        if not path:
            return {
                "status": "error",
                "message": "Missing required parameter: path"
            }
        
        result = self.skill.add_watch_directory(path)
        
        return {
            "status": result["status"],
            "message": result.get("message", "")
        }

    def _handle_remove_watch_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle remove_watch_directory capability."""
        path = parameters.get("path")
        if not path:
            return {
                "status": "error",
                "message": "Missing required parameter: path"
            }
        
        result = self.skill.remove_watch_directory(path)
        
        return {
            "status": result["status"],
            "message": result.get("message", "")
        }

    def _handle_get_watch_directories(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_watch_directories capability."""
        result = self.skill.get_watch_directories()
        
        return {
            "status": result["status"],
            "message": result.get("message", ""),
            "directories": result.get("directories", []),
            "count": result.get("count", 0)
        }

    def _handle_get_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_status capability."""
        result = self.skill.get_status()
        
        return {
            "status": result["status"],
            "message": result.get("message", ""),
            "configured": result.get("configured", False),
            "environment": result.get("environment", {}),
            "config": result.get("config", {}),
            "watch_directories": result.get("watch_directories", []),
            "environment_summary": result.get("environment_summary", ""),
            "config_summary": result.get("config_summary", "")
        }

    def get_status_info(self) -> Dict[str, Any]:
        """Get current adapter status."""
        return {
            "adapter_status": self.status.value,
            "initialized": self.initialized,
            "error": self.error_message,
            "skill_info": self.get_skill_info()
        }

    def shutdown(self) -> Dict[str, Any]:
        """Shutdown the skill gracefully."""
        try:
            logger.info("Shutting down Local ContextBridge Skill")
            self.status = SkillStatus.DISABLED
            self.initialized = False
            return {
                "status": "success",
                "message": "Skill shutdown successfully"
            }
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            return {
                "status": "error",
                "message": f"Shutdown error: {e}"
            }


# Global adapter instance
_adapter_instance: Optional[OpenClawAdapter] = None


def get_adapter() -> OpenClawAdapter:
    """Get or create the global adapter instance."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = OpenClawAdapter()
    return _adapter_instance


def initialize_adapter(config: Optional[Dict[str, Any]] = None, auto_setup: bool = False) -> Dict[str, Any]:
    """
    Initialize the adapter.
    
    Args:
        config: Optional configuration overrides
        auto_setup: Enable automatic setup (default: False for security)
        
    Returns:
        Initialization result
    """
    adapter = get_adapter()
    return adapter.initialize(config, auto_setup=auto_setup)


def call_capability(
    capability_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Call a capability on the adapter."""
    adapter = get_adapter()
    return adapter.call_capability(capability_name, parameters)


def get_skill_info() -> Dict[str, Any]:
    """Get skill information."""
    adapter = get_adapter()
    return adapter.get_skill_info()


def get_status() -> Dict[str, Any]:
    """Get adapter status."""
    adapter = get_adapter()
    return adapter.get_status_info()
