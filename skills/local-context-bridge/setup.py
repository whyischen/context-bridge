"""Setup and initialization for ContextBridge Skill."""

import logging
from typing import Dict, Any, Optional
from .environment import EnvironmentDetector

logger = logging.getLogger(__name__)


class ContextBridgeSetup:
    """Handle ContextBridge setup and initialization."""

    def __init__(self):
        self.detector = EnvironmentDetector()

    def auto_setup(self, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Automatically setup based on environment detection.
        
        Delegates configuration management to core module.
        
        Args:
            workspace_dir: Optional custom workspace directory
            
        Returns:
            Setup result with status and details
        """
        try:
            from core.config import get_config, save_config, is_configured
            from .core_api_contract import CoreAPIContract, Config
            
            # Check Core availability and version
            if not CoreAPIContract.check_core_availability():
                return {
                    "status": "error",
                    "message": "ContextBridge Core module is not available",
                    "hint": "Ensure cbridge-agent is installed: pip install cbridge-agent==0.1.5"
                }
            
            # Check if already configured
            if is_configured():
                try:
                    config_dict = get_config()
                    Config.from_dict(config_dict)  # Validate
                    return {
                        "status": "already_configured",
                        "message": "ContextBridge is already configured",
                        "config": config_dict
                    }
                except ValueError as e:
                    return {
                        "status": "error",
                        "message": f"Existing configuration is invalid: {e}"
                    }
            
            # Check if cbridge-agent is installed
            if not self.detector.is_cbridge_installed():
                return {
                    "status": "error",
                    "message": "cbridge-agent is not installed. Please install manually: pip install cbridge-agent==0.1.5",
                    "hint": "Installation must be done before initializing this skill"
                }
            
            # Detect environment and setup
            env = self.detector.detect_all()
            
            config_dict = {
                "mode": "external" if (env.get("qmd_running") and env.get("openviking_running")) else "embedded",
                "workspace_dir": workspace_dir or self.detector.get_workspace_dir(),
                "watch_dirs": [],
            }
            
            if env.get("qmd_running"):
                config_dict["qmd"] = {
                    "endpoint": env["qmd_endpoint"],
                    "collection": "contextbridge_docs"
                }
            
            if env.get("openviking_running"):
                config_dict["openviking"] = {
                    "endpoint": env["openviking_endpoint"],
                    "mount_path": "viking://contextbridge/"
                }
            
            # Validate config structure before saving
            try:
                Config.from_dict(config_dict)
            except ValueError as e:
                return {
                    "status": "error",
                    "message": f"Generated configuration is invalid: {e}"
                }
            
            save_config(config_dict)
            
            return {
                "status": "success",
                "mode": config_dict["mode"],
                "workspace": config_dict["workspace_dir"],
                "message": f"ContextBridge configured in {config_dict['mode']} mode"
            }
        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import core modules: {e}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Setup failed: {e}"
            }

    def setup_embedded_mode(self, workspace_dir: str) -> Dict[str, Any]:
        """Setup embedded mode (built-in ChromaDB)."""
        try:
            from core.config import save_config
            from .core_api_contract import Config
            
            config = Config(
                mode="embedded",
                workspace_dir=workspace_dir,
                watch_dirs=[]
            )
            
            save_config(config.to_dict())
            
            return {
                "status": "success",
                "mode": "embedded",
                "workspace": workspace_dir,
                "message": "ContextBridge configured in embedded mode"
            }
        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import core modules: {e}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to setup embedded mode: {e}"
            }

    def setup_external_mode(
        self,
        workspace_dir: str,
        qmd_endpoint: str,
        openviking_endpoint: str
    ) -> Dict[str, Any]:
        """Setup external mode (connect to existing services)."""
        try:
            from core.config import save_config
            from .core_api_contract import Config
            
            config = Config(
                mode="external",
                workspace_dir=workspace_dir,
                watch_dirs=[],
                qmd={
                    "endpoint": qmd_endpoint,
                    "collection": "contextbridge_docs"
                },
                openviking={
                    "endpoint": openviking_endpoint,
                    "mount_path": "viking://contextbridge/"
                }
            )
            
            save_config(config.to_dict())
            
            return {
                "status": "success",
                "mode": "external",
                "workspace": workspace_dir,
                "qmd": config.qmd,
                "openviking": config.openviking,
                "message": "ContextBridge configured in external mode with namespace isolation"
            }
        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import core modules: {e}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to setup external mode: {e}"
            }

    def initialize_workspace(self) -> Dict[str, Any]:
        """Initialize workspace after configuration."""
        try:
            from core.config import init_workspace
            init_workspace()
            return {
                "status": "success",
                "message": "Workspace initialized successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize workspace: {e}"
            }

    def build_index(self) -> Dict[str, Any]:
        """Build initial document index."""
        try:
            from core.watcher import index_all
            index_all()
            return {
                "status": "success",
                "message": "Document index built successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to build index: {e}"
            }

    def get_setup_status(self) -> Dict[str, Any]:
        """Get current setup status."""
        try:
            from core.config import get_config, is_configured
            from .core_api_contract import CoreAPIContract, Config
            
            if not is_configured():
                return {
                    "configured": False,
                    "environment": self.detector.detect_all(),
                    "config": {},
                    "environment_summary": self.detector.get_summary(),
                    "config_summary": "No configuration found"
                }
            
            config_dict = get_config()
            
            # Validate config structure
            try:
                config = Config.from_dict(config_dict)
            except ValueError as e:
                return {
                    "configured": False,
                    "environment": self.detector.detect_all(),
                    "config": config_dict,
                    "error": f"Invalid configuration: {e}",
                    "environment_summary": self.detector.get_summary(),
                    "config_summary": "Configuration is invalid"
                }
            
            return {
                "configured": True,
                "environment": self.detector.detect_all(),
                "config": config_dict,
                "environment_summary": self.detector.get_summary(),
                "config_summary": self._get_config_summary(config)
            }
        except ImportError as e:
            return {
                "configured": False,
                "environment": {},
                "config": {},
                "error": f"Failed to import core modules: {e}"
            }
        except Exception as e:
            return {
                "configured": False,
                "environment": {},
                "config": {},
                "error": str(e)
            }

    def _get_config_summary(self, config: 'Config') -> str:
        """Get human-readable config summary."""
        if not config:
            return "No configuration found"
        
        summary = f"""
Configuration Summary:
- Mode: {config.mode}
- Workspace: {config.workspace_dir}
- Watch Dirs: {len(config.watch_dirs)} directories
        """
        return summary.strip()
