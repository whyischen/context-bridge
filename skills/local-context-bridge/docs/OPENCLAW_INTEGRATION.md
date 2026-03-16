# OpenClaw Integration Guide

This document explains how the Local ContextBridge Skill integrates with OpenClaw.

## Architecture

```
OpenClaw
    ↓
OpenClaw Protocol Handler
    ↓
OpenClaw Adapter
    ↓
LocalContextBridgeSkill
    ↓
ContextBridge Core (core/)
```

## Components

### 1. OpenClaw Adapter (`openclaw_adapter.py`)

The main integration layer that:
- Manages skill lifecycle (initialize, ready, error, disabled)
- Implements OpenClaw capability interface
- Transforms requests/responses
- Handles error cases

**Key Classes:**
- `OpenClawAdapter` - Main adapter class
- `SkillStatus` - Skill lifecycle states

**Key Methods:**
- `initialize()` - Initialize the skill
- `call_capability()` - Execute a capability
- `get_skill_info()` - Get skill metadata
- `get_status_info()` - Get current status

### 2. Protocol Handler (`openclaw_protocol.py`)

Handles OpenClaw RPC protocol:
- Parses OpenClaw requests
- Routes to appropriate handlers
- Formats responses according to OpenClaw spec
- Supports batch requests

**Key Classes:**
- `OpenClawProtocolHandler` - Protocol handler

**Supported Methods:**
- `skill.initialize` - Initialize skill
- `skill.getInfo` - Get skill information
- `skill.getStatus` - Get skill status
- `skill.call` - Call a capability
- `skill.shutdown` - Shutdown skill

### 3. Server (`openclaw_server.py`)

WebSocket server for OpenClaw communication:
- Listens for OpenClaw connections
- Handles incoming messages
- Sends responses back

**Key Classes:**
- `OpenClawServer` - WebSocket server

## Usage

### Direct Python Usage

```python
from skills.local_context_bridge import (
    get_adapter,
    initialize_adapter,
    call_capability
)

# Initialize
result = initialize_adapter()

# Call capability
result = call_capability("search_documents", {
    "query": "project architecture",
    "top_k": 5
})

# Get status
adapter = get_adapter()
status = adapter.get_status_info()
```

### OpenClaw Protocol Usage

```json
{
  "jsonrpc": "2.0",
  "method": "skill.initialize",
  "params": {},
  "id": "1"
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "message": "Skill initialized successfully",
    "skill_status": "ready",
    "initialized": true
  },
  "id": "1"
}
```

### Running the Server

```python
from skills.local_context_bridge import run_server

# Run on default host/port (127.0.0.1:8765)
run_server()

# Or with custom host/port
run_server(host="0.0.0.0", port=9000)
```

## Capabilities

### search_documents

Search through local documents.

**Request:**
```json
{
  "method": "skill.call",
  "params": {
    "capability": "search_documents",
    "parameters": {
      "query": "project architecture",
      "top_k": 5
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "source": "file_path",
      "content": "relevant excerpt",
      "score": 0.95
    }
  ],
  "count": 1
}
```

### setup_environment

Setup ContextBridge environment.

**Request:**
```json
{
  "method": "skill.call",
  "params": {
    "capability": "setup_environment",
    "parameters": {
      "mode": "auto"
    }
  }
}
```

### detect_environment

Detect user environment.

**Request:**
```json
{
  "method": "skill.call",
  "params": {
    "capability": "detect_environment",
    "parameters": {}
  }
}
```

### add_watch_directory

Add directory to watch list.

**Request:**
```json
{
  "method": "skill.call",
  "params": {
    "capability": "add_watch_directory",
    "parameters": {
      "path": "/path/to/documents"
    }
  }
}
```

### get_status

Get current skill status.

**Request:**
```json
{
  "method": "skill.call",
  "params": {
    "capability": "get_status",
    "parameters": {}
  }
}
```

## Error Handling

All responses follow this format:

**Success:**
```json
{
  "status": "success",
  "message": "Operation completed",
  "data": {}
}
```

**Error:**
```json
{
  "status": "error",
  "message": "Error description"
}
```

**Protocol Error:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error"
  }
}
```

## Lifecycle

1. **Uninitialized** - Skill created but not initialized
2. **Initializing** - Initialization in progress
3. **Ready** - Skill ready to handle requests
4. **Error** - Error occurred during initialization
5. **Disabled** - Skill has been shut down

## Configuration

The adapter automatically:
- Detects environment (QMD, OpenViking)
- Chooses appropriate mode (embedded/external)
- Manages configuration persistence
- Handles service discovery

## Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

Test the adapter directly:

```python
from skills.local_context_bridge import get_adapter, initialize_adapter

# Initialize
init_result = initialize_adapter()
print(init_result)

# Get adapter
adapter = get_adapter()

# Call capability
result = adapter.call_capability("detect_environment", {})
print(result)

# Get status
status = adapter.get_status_info()
print(status)
```

## Integration Checklist

- [ ] Install ContextBridge: `pip install cbridge-agent`
- [ ] Initialize ContextBridge: `cbridge init`
- [ ] Add watch directories: `cbridge watch add /path`
- [ ] Build index: `cbridge index`
- [ ] Start ContextBridge: `cbridge start`
- [ ] Test adapter: Run test script
- [ ] Deploy to OpenClaw

## Troubleshooting

### Adapter not initializing

1. Check ContextBridge is installed: `pip list | grep cbridge`
2. Check configuration: `cbridge status`
3. Check logs: Enable debug logging

### Connection refused

1. Verify server is running
2. Check host/port configuration
3. Check firewall settings

### Capability not found

1. Check capability name spelling
2. Verify skill is initialized
3. Check OpenClaw version compatibility

## Next Steps

- See [README.md](./README.md) for skill usage
- See [../README.md](../README.md) for skills overview
- See main [ContextBridge documentation](../../docs/)
