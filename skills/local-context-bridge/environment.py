"""Environment detection for ContextBridge Skill."""

import subprocess
import sys
import platform
from typing import Dict, Optional, Any
from pathlib import Path


class EnvironmentDetector:
    """Detect and analyze user environment."""

    def __init__(self):
        self.os_type = platform.system()
        self.python_version = sys.version_info
        self.platform = platform.platform()

    def detect_all(self) -> Dict[str, Any]:
        """Detect complete environment."""
        return {
            "os": self.get_os_type(),
            "python_version": self.get_python_version(),
            "platform": self.platform,
            "cbridge_installed": self.is_cbridge_installed(),
            "qmd_running": self.check_qmd_running(),
            "openviking_running": self.check_openviking_running(),
            "qmd_endpoint": self.get_qmd_endpoint(),
            "openviking_endpoint": self.get_openviking_endpoint(),
            "workspace_dir": self.get_workspace_dir(),
        }

    def get_os_type(self) -> str:
        """Get OS type."""
        return self.os_type

    def get_python_version(self) -> str:
        """Get Python version."""
        return f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}"

    def is_cbridge_installed(self) -> bool:
        """Check if cbridge-agent is installed."""
        try:
            import cbridge
            return True
        except ImportError:
            return False

    def check_qmd_running(self) -> bool:
        """Check if QMD service is running."""
        endpoint = self.get_qmd_endpoint()
        if not endpoint:
            return False
        
        try:
            import requests
            response = requests.get(f"{endpoint}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def check_openviking_running(self) -> bool:
        """Check if OpenViking service is running."""
        endpoint = self.get_openviking_endpoint()
        if not endpoint:
            return False
        
        try:
            import requests
            response = requests.get(f"{endpoint}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def get_qmd_endpoint(self) -> Optional[str]:
        """Get QMD endpoint from environment or config."""
        # Check environment variable
        import os
        if "QMD_ENDPOINT" in os.environ:
            return os.environ["QMD_ENDPOINT"]
        
        # Default endpoint
        return "http://localhost:9090"

    def get_openviking_endpoint(self) -> Optional[str]:
        """Get OpenViking endpoint from environment or config."""
        import os
        if "OPENVIKING_ENDPOINT" in os.environ:
            return os.environ["OPENVIKING_ENDPOINT"]
        
        # Default endpoint
        return "http://localhost:8080"

    def get_workspace_dir(self) -> Optional[str]:
        """Get ContextBridge workspace directory."""
        import os
        from pathlib import Path
        
        # Check environment variable
        if "CBRIDGE_WORKSPACE" in os.environ:
            return os.environ["CBRIDGE_WORKSPACE"]
        
        # Default workspace
        return str(Path.home() / "ContextBridge_Workspace")

    def get_summary(self) -> str:
        """Get human-readable environment summary."""
        env = self.detect_all()
        summary = f"""
Environment Summary:
- OS: {env['os']}
- Python: {env['python_version']}
- ContextBridge Installed: {env['cbridge_installed']}
- QMD Running: {env['qmd_running']} ({env['qmd_endpoint']})
- OpenViking Running: {env['openviking_running']} ({env['openviking_endpoint']})
- Workspace: {env['workspace_dir']}
        """
        return summary.strip()
