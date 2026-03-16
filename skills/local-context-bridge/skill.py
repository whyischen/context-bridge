"""Local ContextBridge Skill for OpenClaw."""

from typing import Dict, Any, List, Optional
from .setup import ContextBridgeSetup
from .environment import EnvironmentDetector
from .core_api_contract import CoreAPIContract, SearchResult, Config


class LocalContextBridgeSkill:
    """
    Local ContextBridge Skill for OpenClaw.
    
    Provides document search and context management capabilities
    for AI agents using local documents (Word, Excel, PDF, Markdown).
    """

    def __init__(self):
        self.setup = ContextBridgeSetup()
        self.detector = EnvironmentDetector()
        self.context_manager = None

    def get_metadata(self) -> Dict[str, Any]:
        """Get skill metadata following OpenClaw specification."""
        return {
            "id": "local-context-bridge",
            "name": "local-context-bridge",
            "displayName": "Local ContextBridge",
            "version": "1.0.0",
            "description": "Local document search and context management for AI agents",
            "author": "whyischen",
            "license": "MIT",
            "capabilities": [
                "search_documents",
                "setup_environment",
                "detect_environment",
                "manage_watch_dirs"
            ],
            "permissions": [
                "file_read",
                "file_write",
                "process_execution",
                "local_storage",
                "network_access"
            ]
        }

    def initialize(self, auto_setup: bool = False) -> Dict[str, Any]:
        """
        Initialize the skill.
        
        IMPORTANT: cbridge-agent must be installed before calling this method.
        Install with: pip install cbridge-agent==0.1.5
        
        When auto_setup=True, this will:
        - Detect environment and available services
        - Create ~/.cbridge/ configuration directory
        - Probe local network endpoints to detect services
        - Create workspace directories
        - Write configuration files
        
        For security-conscious deployments, set auto_setup=False and call
        setup_environment() explicitly after reviewing the operations.
        
        Args:
            auto_setup: Automatically setup if not configured (default: False)
                       Set to True only after ensuring cbridge-agent is installed
                       and you have reviewed the setup operations
            
        Returns:
            Initialization result
        """
        try:
            status = self.setup.get_setup_status()
            
            if not status["configured"] and auto_setup:
                result = self.setup.auto_setup()
                if result["status"] != "success":
                    return result
                
                # Initialize workspace
                self.setup.initialize_workspace()
            elif not status["configured"] and not auto_setup:
                return {
                    "status": "not_configured",
                    "message": "Skill not configured. Call setup_environment() to configure.",
                    "hint": "First ensure cbridge-agent is installed: pip install cbridge-agent==0.1.5",
                    "next_steps": [
                        "1. Install cbridge-agent: pip install cbridge-agent==0.1.5",
                        "2. Call detect_environment() to review available services",
                        "3. Call setup_environment(mode='embedded' or 'external') to configure"
                    ]
                }
            
            # Load context manager
            self._load_context_manager()
            
            return {
                "status": "success",
                "message": "Skill initialized successfully",
                "metadata": self.get_metadata()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize skill: {e}"
            }

    def _load_context_manager(self):
        """Load context manager from core."""
        try:
            from core.factories import initialize_system
            self.context_manager = initialize_system()
        except Exception as e:
            raise RuntimeError(f"Failed to load context manager: {e}")

    def search_documents(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Search through local documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            Search results
        """
        if not self.context_manager:
            self._load_context_manager()
        
        try:
            results = self.context_manager.recursive_retrieve(query, top_k=top_k)
            
            if not results:
                return {
                    "status": "success",
                    "results": [],
                    "message": "No relevant documents found"
                }
            
            formatted_results = []
            for res in results:
                try:
                    # Validate result format using contract
                    validated = CoreAPIContract.validate_search_result(res)
                    formatted_results.append({
                        "source": validated.uri,
                        "content": validated.content,
                        "score": validated.score
                    })
                except ValueError as e:
                    # Log validation error but continue with other results
                    return {
                        "status": "error",
                        "message": f"Invalid search result format from Core: {e}"
                    }
            
            return {
                "status": "success",
                "results": formatted_results,
                "count": len(formatted_results)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Search failed: {e}"
            }

    def detect_environment(self) -> Dict[str, Any]:
        """
        Detect user environment.
        
        Returns:
            Environment information
        """
        try:
            env = self.detector.detect_all()
            return {
                "status": "success",
                "environment": env,
                "summary": self.detector.get_summary()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Environment detection failed: {e}"
            }

    def setup_environment(
        self,
        workspace_dir: Optional[str] = None,
        mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        Setup ContextBridge environment.
        
        Args:
            workspace_dir: Custom workspace directory
            mode: Setup mode ('auto', 'embedded', 'external')
            
        Returns:
            Setup result
        """
        try:
            if mode == "auto":
                result = self.setup.auto_setup(workspace_dir)
            elif mode == "embedded":
                if not workspace_dir:
                    workspace_dir = self.detector.get_workspace_dir()
                result = self.setup.setup_embedded_mode(workspace_dir)
            elif mode == "external":
                if not workspace_dir:
                    workspace_dir = self.detector.get_workspace_dir()
                
                env = self.detector.detect_all()
                result = self.setup.setup_external_mode(
                    workspace_dir=workspace_dir,
                    qmd_endpoint=env["qmd_endpoint"],
                    openviking_endpoint=env["openviking_endpoint"]
                )
            else:
                return {
                    "status": "error",
                    "message": f"Unknown setup mode: {mode}"
                }
            
            if result["status"] == "success":
                self.setup.initialize_workspace()
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Setup failed: {e}"
            }

    def add_watch_directory(self, path: str) -> Dict[str, Any]:
        """
        Add directory to watch list.
        
        Args:
            path: Directory path to monitor
            
        Returns:
            Operation result
        """
        try:
            from core.config import get_config, save_config
            
            config_dict = get_config()
            
            # Validate config structure
            try:
                config = CoreAPIContract.validate_config(config_dict)
            except ValueError as e:
                return {
                    "status": "error",
                    "message": f"Invalid configuration from Core: {e}"
                }
            
            if path not in config.watch_dirs:
                config.watch_dirs.append(path)
                save_config(config.to_dict())
                return {
                    "status": "success",
                    "message": f"Directory added to watch list: {path}"
                }
            else:
                return {
                    "status": "info",
                    "message": f"Directory already in watch list: {path}"
                }
        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import core.config: {e}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to add watch directory: {e}"
            }

    def remove_watch_directory(self, path: str) -> Dict[str, Any]:
        """
        Remove directory from watch list.
        
        Args:
            path: Directory path to remove
            
        Returns:
            Operation result
        """
        try:
            from core.config import get_config, save_config
            
            config_dict = get_config()
            
            # Validate config structure
            try:
                config = CoreAPIContract.validate_config(config_dict)
            except ValueError as e:
                return {
                    "status": "error",
                    "message": f"Invalid configuration from Core: {e}"
                }
            
            if path in config.watch_dirs:
                config.watch_dirs.remove(path)
                save_config(config.to_dict())
                return {
                    "status": "success",
                    "message": f"Directory removed from watch list: {path}"
                }
            else:
                return {
                    "status": "info",
                    "message": f"Directory not in watch list: {path}"
                }
        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import core.config: {e}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to remove watch directory: {e}"
            }

    def get_watch_directories(self) -> Dict[str, Any]:
        """
        Get list of monitored directories.
        
        Returns:
            List of watch directories
        """
        try:
            from core.config import get_config
            
            config_dict = get_config()
            
            # Validate config structure
            try:
                config = CoreAPIContract.validate_config(config_dict)
            except ValueError as e:
                return {
                    "status": "error",
                    "message": f"Invalid configuration from Core: {e}"
                }
            
            return {
                "status": "success",
                "directories": config.watch_dirs,
                "count": len(config.watch_dirs)
            }
        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import core.config: {e}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get watch directories: {e}"
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current skill status.
        
        Returns:
            Status information
        """
        try:
            setup_status = self.setup.get_setup_status()
            watch_dirs = self.config_manager.get_watch_dirs()
            
            return {
                "status": "success",
                "configured": setup_status["configured"],
                "environment": setup_status["environment"],
                "config": setup_status["config"],
                "watch_directories": watch_dirs,
                "environment_summary": setup_status["environment_summary"],
                "config_summary": setup_status["config_summary"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get status: {e}"
            }
