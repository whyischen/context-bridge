"""
ContextBridge Core API Contract

This module defines the expected interfaces and data structures
that the Skill expects from the ContextBridge Core module.

This is a documentation and validation layer to ensure compatibility
between the Skill and Core versions.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SearchResult:
    """Expected format of search results from core.factories.ContextManager.recursive_retrieve()"""
    uri: str
    content: str
    score: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """Convert dict to SearchResult with validation"""
        return cls(
            uri=data.get("uri", "Unknown"),
            content=data.get("content", ""),
            score=float(data.get("score", 0.0))
        )


@dataclass
class Config:
    """Expected configuration structure from core.config module"""
    mode: str  # 'embedded' or 'external'
    workspace_dir: str
    watch_dirs: List[str]
    qmd: Optional[Dict[str, Any]] = None
    openviking: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Convert dict to Config with validation"""
        if not isinstance(data, dict):
            raise ValueError(f"Config must be a dict, got {type(data)}")
        
        if "mode" not in data:
            raise ValueError("Config must have 'mode' field")
        
        if "workspace_dir" not in data:
            raise ValueError("Config must have 'workspace_dir' field")
        
        return cls(
            mode=data["mode"],
            workspace_dir=data["workspace_dir"],
            watch_dirs=data.get("watch_dirs", []),
            qmd=data.get("qmd"),
            openviking=data.get("openviking")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dict for saving"""
        result = {
            "mode": self.mode,
            "workspace_dir": self.workspace_dir,
            "watch_dirs": self.watch_dirs,
        }
        if self.qmd:
            result["qmd"] = self.qmd
        if self.openviking:
            result["openviking"] = self.openviking
        return result


class CoreAPIContract:
    """
    Defines the expected Core API that the Skill depends on.
    
    This serves as documentation and can be used for runtime validation.
    """

    # Expected Core module version
    MINIMUM_CORE_VERSION = "0.1.5"
    MAXIMUM_CORE_VERSION = "0.2.0"

    # Expected modules and functions
    REQUIRED_MODULES = {
        "core.factories": ["initialize_system"],
        "core.config": ["get_config", "save_config", "is_configured", "init_workspace"],
        "core.watcher": ["index_all"],
    }

    # Expected ContextManager interface
    CONTEXT_MANAGER_METHODS = {
        "recursive_retrieve": {
            "parameters": ["query", "top_k"],
            "return_type": "List[Dict[str, Any]]",
            "return_format": [
                {
                    "uri": "str",
                    "content": "str",
                    "score": "float"
                }
            ]
        }
    }

    # Expected configuration structure
    EXPECTED_CONFIG_STRUCTURE = {
        "mode": "str (required)",
        "workspace_dir": "str (required)",
        "watch_dirs": "List[str] (required)",
        "qmd": "Dict[str, Any] (optional)",
        "openviking": "Dict[str, Any] (optional)",
    }

    @staticmethod
    def validate_search_result(result: Dict[str, Any]) -> SearchResult:
        """Validate and convert search result dict to SearchResult"""
        try:
            return SearchResult.from_dict(result)
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid search result format: {e}")

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Config:
        """Validate and convert config dict to Config"""
        try:
            return Config.from_dict(config)
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid config format: {e}")

    @staticmethod
    def check_core_availability() -> bool:
        """Check if Core module is available"""
        try:
            import core
            return True
        except ImportError:
            return False

    @staticmethod
    def get_core_version() -> Optional[str]:
        """Get Core module version"""
        try:
            import core
            return getattr(core, '__version__', None)
        except ImportError:
            return None
