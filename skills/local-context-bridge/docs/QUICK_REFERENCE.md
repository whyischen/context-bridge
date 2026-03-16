# Quick Reference Guide

## Installation

```bash
# Install ContextBridge
pip install cbridge-agent

# Initialize
cbridge init

# Add directories
cbridge watch add ~/Documents

# Build index
cbridge index

# Start service
cbridge start
```

## Direct Python Usage

```python
from skills.local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()
skill.initialize()

# Search
results = skill.search_documents("query", top_k=5)

# Add directory
skill.add_watch_directory("/path/to/docs")

# Get status
status = skill.get_status()
```

## OpenClaw Adapter Usage

```python
from skills.local_context_bridge import (
    initialize_adapter,
    call_capability,
    get_adapter
)

# Initialize
initialize_adapter()

# Call capability
result = call_capability("search_documents", {
    "query": "architecture",
    "top_k": 5
})

# Get adapter
adapter = get_adapter()
status = adapter.get_status_info()
```

## OpenClaw Protocol (JSON-RPC)

### Initialize Skill
```json
{
  "jsonrpc": "2.0",
  "method": "skill.initialize",
  "params": {},
  "id": "1"
}
```

### Get Skill Info
```json
{
  "jsonrpc": "2.0",
  "method": "skill.getInfo",
  "params": {},
  "id": "2"
}
```

### Search Documents
```json
{
  "jsonrpc": "2.0",
  "method": "skill.call",
  "params": {
    "capability": "search_documents",
    "parameters": {
      "query": "architecture",
      "top_k": 5
    }
  },
  "id": "3"
}
```

### Setup Environment
```json
{
  "jsonrpc": "2.0",
  "method": "skill.call",
  "params": {
    "capability": "setup_environment",
    "parameters": {
      "mode": "auto"
    }
  },
  "id": "4"
}
```

### Detect Environment
```json
{
  "jsonrpc": "2.0",
  "method": "skill.call",
  "params": {
    "capability": "detect_environment",
    "parameters": {}
  },
  "id": "5"
}
```

### Add Watch Directory
```json
{
  "jsonrpc": "2.0",
  "method": "skill.call",
  "params": {
    "capability": "add_watch_directory",
    "parameters": {
      "path": "/path/to/documents"
    }
  },
  "id": "6"
}
```

### Get Status
```json
{
  "jsonrpc": "2.0",
  "method": "skill.call",
  "params": {
    "capability": "get_status",
    "parameters": {}
  },
  "id": "7"
}
```

## Running the Server

```python
from skills.local_context_bridge import run_server

# Default: ws://127.0.0.1:8765
run_server()

# Custom host/port
run_server(host="0.0.0.0", port=9000)
```

## Testing

```bash
cd skills/local-context-bridge
python test_adapter.py
```

## Response Format

### Success
```json
{
  "status": "success",
  "message": "Operation completed",
  "data": {}
}
```

### Error
```json
{
  "status": "error",
  "message": "Error description"
}
```

### Search Results
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

## Configuration File

Location: `~/.cbridge/config.yaml`

### Embedded Mode
```yaml
mode: embedded
workspace_dir: ~/ContextBridge_Workspace
watch_dirs:
  - ~/Documents
  - ~/Projects
mcp:
  port: 4733
```

### External Mode
```yaml
mode: external
workspace_dir: ~/ContextBridge_Workspace
watch_dirs:
  - ~/Documents
qmd:
  endpoint: http://localhost:9090
  collection: contextbridge_docs
openviking:
  endpoint: http://localhost:8080
  mount_path: viking://contextbridge/
mcp:
  port: 4733
```

## Troubleshooting

### Skill not initializing
```bash
# Check ContextBridge installation
pip list | grep cbridge

# Check configuration
cbridge status

# Enable debug logging
export LOGLEVEL=DEBUG
```

### No search results
```bash
# Check monitored directories
cbridge watch list

# Rebuild index
cbridge index

# Check file formats (Word, Excel, PDF, Markdown)
```

### Connection refused
```bash
# Check if ContextBridge is running
cbridge status

# Check if services are running
curl http://localhost:9090/health  # QMD
curl http://localhost:8080/health  # OpenViking
```

## Environment Variables

```bash
# Custom workspace
export CBRIDGE_WORKSPACE=/custom/path

# QMD endpoint
export QMD_ENDPOINT=http://localhost:9090

# OpenViking endpoint
export OPENVIKING_ENDPOINT=http://localhost:8080
```

## Capabilities Summary

| Capability | Purpose | Parameters |
|-----------|---------|-----------|
| `search_documents` | Search documents | query, top_k |
| `setup_environment` | Setup ContextBridge | workspace_dir, mode |
| `detect_environment` | Detect environment | - |
| `add_watch_directory` | Add directory | path |
| `remove_watch_directory` | Remove directory | path |
| `get_watch_directories` | List directories | - |
| `get_status` | Get status | - |

## Lifecycle States

- **UNINITIALIZED** - Not initialized
- **INITIALIZING** - Initialization in progress
- **READY** - Ready to handle requests
- **ERROR** - Error occurred
- **DISABLED** - Shut down

## Files

- `skill.py` - Core skill logic
- `openclaw_adapter.py` - OpenClaw integration
- `openclaw_protocol.py` - RPC protocol handler
- `openclaw_server.py` - WebSocket server
- `setup.py` - Setup & initialization
- `environment.py` - Environment detection
- `config_manager.py` - Configuration management
- `test_adapter.py` - Test script
- `manifest.json` - Skill metadata
- `README.md` - Full documentation
- `OPENCLAW_INTEGRATION.md` - Integration guide
- `QUICK_REFERENCE.md` - This file

## Links

- [Full Documentation](./README.md)
- [Integration Guide](./OPENCLAW_INTEGRATION.md)
- [Architecture](../../SKILL_ARCHITECTURE.md)
- [ContextBridge Docs](../../docs/)
