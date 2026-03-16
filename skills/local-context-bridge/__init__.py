"""Local ContextBridge Skill for OpenClaw."""

from .skill import LocalContextBridgeSkill
from .openclaw_adapter import OpenClawAdapter, get_adapter, initialize_adapter, call_capability
from .openclaw_protocol import OpenClawProtocolHandler, create_protocol_handler
from .openclaw_server import OpenClawServer, run_server

__version__ = "1.0.0"
__all__ = [
    "LocalContextBridgeSkill",
    "OpenClawAdapter",
    "get_adapter",
    "initialize_adapter",
    "call_capability",
    "OpenClawProtocolHandler",
    "create_protocol_handler",
    "OpenClawServer",
    "run_server"
]
