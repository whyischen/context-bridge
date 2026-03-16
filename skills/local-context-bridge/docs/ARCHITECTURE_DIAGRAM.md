# Architecture Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenClaw Platform                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  OpenClaw Agent                                          │   │
│  │  - Processes user requests                              │   │
│  │  - Calls skills via WebSocket                           │   │
│  │  - Receives results                                     │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                    WebSocket Connection
                              │
┌─────────────────────────────▼──────────────────────────────────┐
│              Local ContextBridge Skill                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  OpenClaw Server (openclaw_server.py)                  │    │
│  │  - WebSocket listener on ws://127.0.0.1:8765          │    │
│  │  - Handles incoming connections                       │    │
│  │  - Routes messages to protocol handler                │    │
│  └────────────────────┬─────────────────────────────────┘    │
│                       │                                        │
│  ┌────────────────────▼─────────────────────────────────┐    │
│  │  Protocol Handler (openclaw_protocol.py)             │    │
│  │  - Parses JSON-RPC requests                          │    │
│  │  - Validates request format                          │    │
│  │  - Routes to adapter methods                         │    │
│  │  - Formats responses                                 │    │
│  │  - Handles batch requests                            │    │
│  └────────────────────┬─────────────────────────────────┘    │
│                       │                                        │
│  ┌────────────────────▼─────────────────────────────────┐    │
│  │  OpenClaw Adapter (openclaw_adapter.py)              │    │
│  │  - Manages skill lifecycle                           │    │
│  │  - Implements capability interface                   │    │
│  │  - Transforms requests/responses                     │    │
│  │  - Handles errors                                    │    │
│  │  - Provides status info                              │    │
│  └────────────────────┬─────────────────────────────────┘    │
│                       │                                        │
│  ┌────────────────────▼─────────────────────────────────┐    │
│  │  LocalContextBridgeSkill (skill.py)                  │    │
│  │  - search_documents()                                │    │
│  │  - setup_environment()                               │    │
│  │  - detect_environment()                              │    │
│  │  - add_watch_directory()                             │    │
│  │  - remove_watch_directory()                          │    │
│  │  - get_watch_directories()                           │    │
│  │  - get_status()                                      │    │
│  └────────────────────┬─────────────────────────────────┘    │
│                       │                                        │
│  ┌────────────────────▼─────────────────────────────────┐    │
│  │  Supporting Modules                                  │    │
│  │  - Setup (setup.py)                                  │    │
│  │  - Environment Detection (environment.py)            │    │
│  │  - Config Manager (config_manager.py)                │    │
│  └────────────────────┬─────────────────────────────────┘    │
└─────────────────────────┼──────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│              ContextBridge Core (core/)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Factories (core/factories.py)                         │    │
│  │  - initialize_system()                                │    │
│  │  - Creates context manager                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Context Manager                                       │    │
│  │  - recursive_retrieve(query, top_k)                   │    │
│  │  - Searches vector database                           │    │
│  │  - Returns ranked results                             │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Vector Database                                       │    │
│  │  - Embedded: ChromaDB                                 │    │
│  │  - External: QMD + OpenViking                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  File Watcher (core/watcher.py)                        │    │
│  │  - Monitors watch directories                         │    │
│  │  - Detects file changes                               │    │
│  │  - Updates indexes                                    │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## Request/Response Flow

### Search Request

```
OpenClaw Agent
    │
    │ WebSocket Message (JSON-RPC)
    │ {
    │   "method": "skill.call",
    │   "params": {
    │     "capability": "search_documents",
    │     "parameters": {"query": "...", "top_k": 5}
    │   }
    │ }
    ▼
OpenClaw Server
    │ Receives message
    ▼
Protocol Handler
    │ Parses JSON-RPC
    │ Routes to adapter.call_capability()
    ▼
OpenClaw Adapter
    │ Validates parameters
    │ Calls skill.search_documents()
    ▼
LocalContextBridgeSkill
    │ Loads context manager
    │ Calls context_manager.recursive_retrieve()
    ▼
ContextBridge Core
    │ Searches vector database
    │ Returns ranked results
    ▼
LocalContextBridgeSkill
    │ Formats results
    │ Returns to adapter
    ▼
OpenClaw Adapter
    │ Transforms response
    │ Returns to protocol handler
    ▼
Protocol Handler
    │ Formats JSON-RPC response
    │ Sends to server
    ▼
OpenClaw Server
    │ Sends via WebSocket
    ▼
OpenClaw Agent
    │ Receives results
    │ Processes response
    ▼
User
```

## Initialization Flow

```
OpenClaw Agent
    │
    │ skill.initialize()
    ▼
Protocol Handler
    │ Routes to adapter.initialize()
    ▼
OpenClaw Adapter
    │ Status: INITIALIZING
    │ Calls skill.initialize(auto_setup=True)
    ▼
LocalContextBridgeSkill
    │ Calls setup.auto_setup()
    ▼
ContextBridgeSetup
    │
    ├─ Check if already configured
    │  └─ If yes, return existing config
    │
    ├─ Install cbridge-agent (if needed)
    │
    ├─ Detect environment
    │  ├─ Check OS
    │  ├─ Check Python version
    │  ├─ Check if QMD running
    │  └─ Check if OpenViking running
    │
    ├─ Choose mode
    │  ├─ If QMD + OpenViking running
    │  │  └─ External mode with namespace isolation
    │  └─ Else
    │     └─ Embedded mode
    │
    ├─ Create configuration
    │
    ├─ Save to ~/.cbridge/config.yaml
    │
    └─ Initialize workspace
       ├─ Create directories
       └─ Load context manager
    ▼
LocalContextBridgeSkill
    │ Status: READY
    │ Return success
    ▼
OpenClaw Adapter
    │ Status: READY
    │ Return success response
    ▼
Protocol Handler
    │ Format JSON-RPC response
    ▼
OpenClaw Server
    │ Send to OpenClaw Agent
    ▼
OpenClaw Agent
    │ Skill ready to use
```

## Capability Routing

```
Protocol Handler receives request
    │
    ├─ method: "skill.initialize"
    │  └─ adapter.initialize()
    │
    ├─ method: "skill.getInfo"
    │  └─ adapter.get_skill_info()
    │
    ├─ method: "skill.getStatus"
    │  └─ adapter.get_status_info()
    │
    ├─ method: "skill.call"
    │  │
    │  └─ capability: ?
    │     │
    │     ├─ "search_documents"
    │     │  └─ adapter._handle_search_documents()
    │     │     └─ skill.search_documents()
    │     │
    │     ├─ "setup_environment"
    │     │  └─ adapter._handle_setup_environment()
    │     │     └─ skill.setup_environment()
    │     │
    │     ├─ "detect_environment"
    │     │  └─ adapter._handle_detect_environment()
    │     │     └─ skill.detect_environment()
    │     │
    │     ├─ "add_watch_directory"
    │     │  └─ adapter._handle_add_watch_directory()
    │     │     └─ skill.add_watch_directory()
    │     │
    │     ├─ "remove_watch_directory"
    │     │  └─ adapter._handle_remove_watch_directory()
    │     │     └─ skill.remove_watch_directory()
    │     │
    │     ├─ "get_watch_directories"
    │     │  └─ adapter._handle_get_watch_directories()
    │     │     └─ skill.get_watch_directories()
    │     │
    │     └─ "get_status"
    │        └─ adapter._handle_get_status()
    │           └─ skill.get_status()
    │
    └─ method: "skill.shutdown"
       └─ adapter.shutdown()
```

## Lifecycle State Machine

```
                    ┌─────────────────────┐
                    │  UNINITIALIZED      │
                    │  (Initial state)    │
                    └──────────┬──────────┘
                               │
                    initialize() called
                               │
                               ▼
                    ┌─────────────────────┐
                    │  INITIALIZING       │
                    │  (In progress)      │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
         Success                         Error
                │                             │
                ▼                             ▼
    ┌─────────────────────┐    ┌─────────────────────┐
    │  READY              │    │  ERROR              │
    │  (Ready to handle   │    │  (Error occurred)   │
    │   requests)         │    └─────────────────────┘
    └──────────┬──────────┘
               │
        shutdown() called
               │
               ▼
    ┌─────────────────────┐
    │  DISABLED           │
    │  (Shut down)        │
    └─────────────────────┘
```

## Environment Detection Flow

```
EnvironmentDetector.detect_all()
    │
    ├─ get_os_type()
    │  └─ platform.system()
    │
    ├─ get_python_version()
    │  └─ sys.version_info
    │
    ├─ is_cbridge_installed()
    │  └─ Try import cbridge
    │
    ├─ check_qmd_running()
    │  └─ GET http://localhost:9090/health
    │
    ├─ check_openviking_running()
    │  └─ GET http://localhost:8080/health
    │
    ├─ get_qmd_endpoint()
    │  ├─ Check QMD_ENDPOINT env var
    │  └─ Default: http://localhost:9090
    │
    ├─ get_openviking_endpoint()
    │  ├─ Check OPENVIKING_ENDPOINT env var
    │  └─ Default: http://localhost:8080
    │
    └─ get_workspace_dir()
       ├─ Check CBRIDGE_WORKSPACE env var
       ├─ Check ~/.cbridge/config.yaml
       └─ Default: ~/ContextBridge_Workspace
```

## Configuration Decision Tree

```
Auto Setup
    │
    ├─ Already configured?
    │  ├─ Yes → Return existing config
    │  └─ No → Continue
    │
    ├─ Install cbridge-agent
    │
    ├─ Detect environment
    │
    └─ Choose mode
       │
       ├─ QMD running AND OpenViking running?
       │  │
       │  ├─ Yes → External Mode
       │  │  ├─ Collection: contextbridge_docs
       │  │  ├─ Mount: viking://contextbridge/
       │  │  └─ Reuse existing services
       │  │
       │  └─ No → Embedded Mode
       │     ├─ Use built-in ChromaDB
       │     └─ No external dependencies
       │
       └─ Save configuration
          └─ ~/.cbridge/config.yaml
```

## Error Handling Flow

```
Any Operation
    │
    ├─ Try
    │  │
    │  └─ Execute operation
    │
    └─ Except
       │
       ├─ Log error
       │
       ├─ Format error response
       │  │
       │  ├─ If protocol error
       │  │  └─ JSON-RPC error format
       │  │
       │  └─ If operation error
       │     └─ Standard error format
       │
       └─ Return error response
          │
          ├─ To adapter
          ├─ To protocol handler
          ├─ To server
          └─ To OpenClaw Agent
```

## File Organization

```
skills/local-context-bridge/
│
├─ __init__.py
│  └─ Exports all public APIs
│
├─ manifest.json
│  └─ Skill metadata for OpenClaw
│
├─ skill.py
│  └─ Core business logic
│
├─ openclaw_adapter.py ✨
│  └─ Integration layer
│
├─ openclaw_protocol.py ✨
│  └─ RPC protocol handler
│
├─ openclaw_server.py ✨
│  └─ WebSocket server
│
├─ setup.py
│  └─ Setup & initialization
│
├─ environment.py
│  └─ Environment detection
│
├─ config_manager.py
│  └─ Configuration management
│
├─ test_adapter.py
│  └─ Test script
│
├─ README.md
│  └─ Full documentation
│
├─ OPENCLAW_INTEGRATION.md
│  └─ Integration guide
│
├─ QUICK_REFERENCE.md
│  └─ Quick reference
│
└─ ARCHITECTURE_DIAGRAM.md
   └─ This file
```

## Data Structures

### Skill Info Response

```json
{
  "id": "local-context-bridge",
  "name": "Local ContextBridge",
  "version": "1.0.0",
  "description": "...",
  "capabilities": [
    {
      "name": "search_documents",
      "description": "...",
      "parameters": {
        "query": {"type": "string", "required": true},
        "top_k": {"type": "integer", "default": 5}
      }
    }
  ],
  "status": "ready",
  "initialized": true
}
```

### Search Result

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

### Environment Info

```json
{
  "os": "Darwin",
  "python_version": "3.9.0",
  "cbridge_installed": true,
  "qmd_running": true,
  "openviking_running": true,
  "qmd_endpoint": "http://localhost:9090",
  "openviking_endpoint": "http://localhost:8080",
  "workspace_dir": "/Users/user/ContextBridge_Workspace"
}
```
