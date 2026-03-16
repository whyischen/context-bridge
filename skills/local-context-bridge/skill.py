"""Local ContextBridge Skill for OpenClaw."""

from typing import Dict, Any, Optional
from .setup import ContextBridgeSetup
from .core_api_contract import CoreAPIContract, SearchResult
from .version import __version__


class LocalContextBridgeSkill:
    """
    Local ContextBridge Skill for OpenClaw.
    
    Provides document search and context management capabilities
    for AI agents using local documents (Word, Excel, PDF, Markdown).
    """

    def __init__(self):
        self.setup = ContextBridgeSetup()
        self.context_manager = None

    def get_metadata(self) -> Dict[str, Any]:
        """Get skill metadata following OpenClaw specification."""
        return {
            "id": "local-context-bridge",
            "name": "local-context-bridge",
            "displayName": "Local Document Search (Privacy-First)",
            "version": __version__,
            "description": "Local document search, privacy-first. Index and search Word, Excel, PDF, Markdown files without uploading to external services.",
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
                "local_storage",
                "network_access"
            ]
        }

    def initialize(self, auto_setup: bool = False) -> Dict[str, Any]:
        """
        Initialize the skill (configuration only).
        
        IMPORTANT: This method only initializes the Skill. It does NOT create files or directories.
        File creation is the responsibility of Core, not the Skill.
        
        Args:
            auto_setup: Automatically configure if not configured (default: False)
            
        Returns:
            Initialization result
        """
        try:
            from core.config import is_configured
            
            if not is_configured() and auto_setup:
                result = self.setup.auto_setup()
                if result["status"] != "success":
                    return result
                # NOTE: Skill does NOT call initialize_workspace() here.
                # File creation is the responsibility of Core, not the Skill.
            elif not is_configured() and not auto_setup:
                return {
                    "status": "not_configured",
                    "message": "Skill not configured. Call setup_environment() to configure."
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
                    validated = CoreAPIContract.validate_search_result(res)
                    formatted_results.append({
                        "source": validated.uri,
                        "content": validated.content,
                        "score": validated.score
                    })
                except ValueError as e:
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
        Detect user environment and available services.
        
        Returns:
            Environment information
        """
        try:
            from core.factories import detect_services
            
            services = detect_services()
            return {
                "status": "success",
                "environment": services
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
        Setup ContextBridge environment (configuration only).
        
        IMPORTANT: This method only configures settings. It does NOT create files or directories.
        File creation is the responsibility of Core, not the Skill.
        
        Args:
            workspace_dir: Custom workspace directory
            mode: Setup mode ('auto', 'embedded', 'external')
            
        Returns:
            Setup result with configuration details
        """
        try:
            if mode == "auto":
                result = self.setup.auto_setup(workspace_dir)
            elif mode == "embedded":
                if not workspace_dir:
                    from pathlib import Path
                    workspace_dir = str(Path.home() / "ContextBridge_Workspace")
                result = self.setup.setup_embedded_mode(workspace_dir)
            elif mode == "external":
                if not workspace_dir:
                    from pathlib import Path
                    workspace_dir = str(Path.home() / "ContextBridge_Workspace")
                
                env = self.detect_environment()
                if env["status"] != "success":
                    return env
                
                services = env["environment"]
                result = self.setup.setup_external_mode(
                    workspace_dir=workspace_dir,
                    qmd_endpoint=services.get("qmd_endpoint", "http://localhost:9090"),
                    openviking_endpoint=services.get("openviking_endpoint", "http://localhost:8080")
                )
            else:
                return {
                    "status": "error",
                    "message": f"Unknown setup mode: {mode}"
                }
            
            # NOTE: Skill does NOT call initialize_workspace() here.
            # File creation is the responsibility of Core, not the Skill.
            # Users must explicitly call Core's init_workspace() if they want to create files.
            
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
            from core.config import add_watch_dir
            
            if add_watch_dir(path):
                return {
                    "status": "success",
                    "message": f"Directory added to watch list: {path}"
                }
            else:
                return {
                    "status": "info",
                    "message": f"Directory already in watch list: {path}"
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
            from core.config import remove_watch_dir
            
            if remove_watch_dir(path):
                return {
                    "status": "success",
                    "message": f"Directory removed from watch list: {path}"
                }
            else:
                return {
                    "status": "info",
                    "message": f"Directory not in watch list: {path}"
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
            from core.config import get_watch_dirs
            
            dirs = get_watch_dirs()
            return {
                "status": "success",
                "directories": [str(d) for d in dirs],
                "count": len(dirs)
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
            from core.config import is_configured, CONFIG
            
            return {
                "status": "success",
                "configured": is_configured(),
                "config": CONFIG
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get status: {e}"
            }
