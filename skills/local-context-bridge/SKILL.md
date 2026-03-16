# Local Document Search (Privacy-First) Skill

## Overview

**Local Document Search** is an OpenClaw Skill that provides local document indexing and search capabilities for AI agents. It enables intelligent searching through Word, Excel, PDF, and Markdown files without uploading documents to external services.

**Important**: This Skill handles configuration and search operations only. File creation and workspace initialization are the responsibility of the ContextBridge Core, not the Skill.

**Skill ID**: `local-context-bridge`  
**Version**: 1.0.4  
**Author**: whyischen  
**License**: MIT

## Installation

### Prerequisites

- Python 3.8 or higher
- cbridge-agent 0.1.5

### Install from PyPI

```bash
pip install local-context-bridge
```

### Install from Source

```bash
git clone https://github.com/whyischen/local-context-bridge-skill.git
cd local-context-bridge-skill
pip install -r requirements.txt
```

## Quick Start

### 1. Install cbridge-agent

```bash
pip install cbridge-agent==0.1.5
```

### 2. Initialize the Skill (Configuration Only)

```bash
cbridge init
```

**Note**: This configures the Skill but does NOT create files. File creation is handled by Core.

### 3. Add Directories to Monitor

```bash
cbridge watch add ~/Documents/MyProjects
cbridge watch add ~/Downloads/Research
```

### 4. Build the Index

```bash
cbridge index
```

### 5. Start the Service

```bash
cbridge start
```

### 6. Use in OpenClaw

```
/enable local-context-bridge
/local-context-bridge search "your query"
```

## API Reference

### Core Methods

#### `initialize(auto_setup=False)`

Initialize the skill (configuration only).

**IMPORTANT**: This method only initializes the Skill. It does NOT create files or directories. File creation is the responsibility of Core, not the Skill.

**Parameters:**
- `auto_setup` (bool): Automatically configure if not configured (default: False)

**Returns:**
```json
{
  "status": "success",
  "message": "Skill initialized successfully",
  "metadata": {
    "name": "local-context-bridge",
    "displayName": "Local Document Search (Privacy-First)",
    "version": "1.0.4",
    "capabilities": [...]
  }
}
```

**Example:**
```python
from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)

if result["status"] == "not_configured":
    # Configure the environment (no files created)
    config_result = skill.setup_environment(mode='embedded')
    
    # If you want to create files, call Core's init_workspace() explicitly
    if config_result["status"] == "success":
        from core.config import init_workspace
        init_workspace()  # This creates files and directories
```

---

#### `search_documents(query, top_k=5)`

Search through indexed local documents.

**Parameters:**
- `query` (str): Search query string
- `top_k` (int): Maximum number of results to return (default: 5)

**Returns:**
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

**Example:**
```python
results = skill.search_documents("machine learning algorithms", top_k=10)
for result in results["results"]:
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']}")
    print(f"Content: {result['content']}\n")
```

---

#### `detect_environment()`

Detect user environment and available services.

**Returns:**
```json
{
  "status": "success",
  "environment": {
    "os_type": "darwin",
    "python_version": "3.9.0",
    "qmd_available": true,
    "openviking_available": true,
    "qmd_endpoint": "http://localhost:9090",
    "openviking_endpoint": "http://localhost:8080"
  },
  "summary": "External mode available"
}
```

---

#### `setup_environment(workspace_dir=None, mode='auto')`

Configure ContextBridge environment with specified mode (configuration only).

**IMPORTANT**: This method only configures settings. It does NOT create files or directories. File creation is the responsibility of Core, not the Skill.

**Parameters:**
- `workspace_dir` (str): Custom workspace directory (optional)
- `mode` (str): Setup mode - 'auto', 'embedded', or 'external' (default: 'auto')

**Returns:**
```json
{
  "status": "success",
  "mode": "external",
  "message": "Environment setup completed",
  "config": {...}
}
```

**Example:**
```python
# Configure the environment (no files created)
result = skill.setup_environment(mode='embedded')

# If you want to create files, call Core's init_workspace() explicitly
if result["status"] == "success":
    from core.config import init_workspace
    init_workspace()  # This creates files and directories
```

---

#### `add_watch_directory(path)`

Add a directory to the watch list for automatic indexing.

**Parameters:**
- `path` (str): Directory path to monitor

**Returns:**
```json
{
  "status": "success",
  "message": "Directory added to watch list: /path/to/dir"
}
```

---

#### `remove_watch_directory(path)`

Remove a directory from the watch list.

**Parameters:**
- `path` (str): Directory path to remove

**Returns:**
```json
{
  "status": "success",
  "message": "Directory removed from watch list: /path/to/dir"
}
```

---

#### `get_watch_directories()`

Get the list of all monitored directories.

**Returns:**
```json
{
  "status": "success",
  "directories": [
    "~/Documents/Projects",
    "~/Downloads/Research"
  ],
  "count": 2
}
```

---

#### `get_status()`

Get comprehensive skill status and configuration information.

**Returns:**
```json
{
  "status": "success",
  "configured": true,
  "environment": {...},
  "config": {...},
  "watch_directories": [...],
  "environment_summary": "External mode available",
  "config_summary": "Using external services"
}
```

---

#### `get_metadata()`

Get skill metadata and capabilities.

**Returns:**
```json
{
  "name": "local-context-bridge",
  "displayName": "Local Document Search (Privacy-First)",
  "version": "1.0.4",
  "description": "Local document search, privacy-first. Index and search Word, Excel, PDF, Markdown files without uploading to external services.",
  "capabilities": [
    "search_documents",
    "setup_environment",
    "detect_environment",
    "manage_watch_dirs"
  ]
}
```

## Supported File Formats

| Format | Extension | Support |
|--------|-----------|---------|
| Microsoft Word | .docx, .doc | ✓ Full |
| Microsoft Excel | .xlsx, .xls | ✓ Full |
| PDF | .pdf | ✓ Full |
| Markdown | .md | ✓ Full |
| Plain Text | .txt | ✓ Full |

## Deployment Modes

### Embedded Mode (Default)

Uses built-in ChromaDB for document indexing and retrieval.

**Configuration:**
```python
skill.setup_environment(mode='embedded')
```

### External Mode (Auto-detected)

Connects to existing QMD and OpenViking services.

**Configuration:**
```python
skill.setup_environment(mode='external')
```

## Responsibility Separation: Skill vs Core

### What the Skill Does

- ✅ Configuration management (reading/writing config)
- ✅ Environment detection (checking for available services)
- ✅ Document search operations
- ✅ Watch directory management
- ✅ Status and metadata queries

### What the Skill Does NOT Do

- ❌ Create files or directories
- ❌ Initialize workspace
- ❌ Write logs
- ❌ Manage file permissions

### What Core Does

- ✅ File and directory creation
- ✅ Workspace initialization
- ✅ Audit logging
- ✅ Permission management
- ✅ Document parsing and indexing

**Important**: If you want to create files and initialize the workspace, you must explicitly call Core's `init_workspace()` function after configuring the Skill.

## Environment Variables (Optional)

| Variable | Purpose | Default |
|----------|---------|---------|
| `CBRIDGE_WORKSPACE` | Custom workspace directory | `~/.cbridge/` |
| `CBRIDGE_MODE` | Deployment mode | Auto-detect |
| `QMD_ENDPOINT` | QMD service endpoint | `http://localhost:9090` |
| `OPENVIKING_ENDPOINT` | OpenViking service endpoint | `http://localhost:8080` |

## Usage Examples

### Example 1: Basic Document Search

```python
from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)

if result["status"] == "not_configured":
    # Configure the environment (no files created)
    config_result = skill.setup_environment(mode='embedded')
    
    # If you want to create files, call Core's init_workspace() explicitly
    if config_result["status"] == "success":
        from core.config import init_workspace
        init_workspace()  # This creates files and directories

# Search documents
results = skill.search_documents("Python best practices", top_k=5)

# Process results
for result in results["results"]:
    print(f"File: {result['source']}")
    print(f"Relevance: {result['score']:.2%}")
    print(f"Content: {result['content'][:200]}...\n")
```

### Example 2: Setup and Monitor Directories

```python
from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)

if result["status"] == "not_configured":
    # Configure the environment (no files created)
    config_result = skill.setup_environment(mode='auto')
    
    # If you want to create files, call Core's init_workspace() explicitly
    if config_result["status"] == "success":
        from core.config import init_workspace
        init_workspace()  # This creates files and directories

# Add directories to monitor
skill.add_watch_directory('~/Documents/Projects')
skill.add_watch_directory('~/Downloads/Research')

# View monitored directories
dirs = skill.get_watch_directories()
print(f"Monitoring {dirs['count']} directories")
```

### Example 3: Environment Detection

```python
from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()
skill.initialize(auto_setup=False)

# Detect environment
env = skill.detect_environment()

if env["status"] == "success":
    env_info = env["environment"]
    
    if env_info["qmd_available"] and env_info["openviking_available"]:
        print("External services available - using external mode")
        config_result = skill.setup_environment(mode='external')
    else:
        print("Using embedded mode")
        config_result = skill.setup_environment(mode='embedded')
    
    # If you want to create files, call Core's init_workspace() explicitly
    if config_result["status"] == "success":
        from core.config import init_workspace
        init_workspace()  # This creates files and directories
```

### Example 4: OpenClaw Integration

```python
from local_context_bridge import initialize_adapter, call_capability

# Initialize adapter
initialize_adapter(auto_setup=False)

# Call capability through adapter
result = call_capability(
    "search_documents",
    {
        "query": "machine learning",
        "top_k": 10
    }
)

print(f"Found {result['count']} results")
```

## Testing

### Run Test Suite

```bash
cd local-context-bridge
python test_adapter.py
```

### Manual Testing

```python
from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()

# Test initialization
print("Testing initialization...")
result = skill.initialize(auto_setup=False)
assert result["status"] in ["success", "not_configured"]

# Test environment detection
print("Testing environment detection...")
env = skill.detect_environment()
assert env["status"] == "success"

# Setup if needed
if result["status"] == "not_configured":
    print("Setting up environment...")
    setup_result = skill.setup_environment(mode='embedded')
    assert setup_result["status"] == "success"

# Test directory management
print("Testing directory management...")
skill.add_watch_directory("~/test")
dirs = skill.get_watch_directories()
assert "~/test" in dirs["directories"]

print("All tests passed!")
```

## Capabilities Summary

| Capability | Description | Parameters | Returns |
|------------|-------------|-----------|---------|
| `search_documents` | Search indexed documents | query, top_k | Results with scores |
| `setup_environment` | Configure deployment mode | workspace_dir, mode | Setup status |
| `detect_environment` | Detect available services | - | Environment info |
| `add_watch_directory` | Monitor directory | path | Operation status |
| `remove_watch_directory` | Stop monitoring directory | path | Operation status |
| `get_watch_directories` | List monitored directories | - | Directory list |
| `get_status` | Get skill status | - | Status info |
| `get_metadata` | Get skill metadata | - | Metadata |

## Related Documentation

- **[README](./README.md)** - Project overview
- **[Quick Reference](./QUICK_REFERENCE.md)** - Quick command reference
- **[OpenClaw Integration](./OPENCLAW_INTEGRATION.md)** - Integration details

## Support & Community

- **Documentation**: See related docs in this repository
- **Issues**: Report bugs on GitHub
- **Discussions**: Join community discussions

## License

MIT License - See LICENSE file for details

## Changelog

### Version 1.0.4 (Current)
- **BREAKING CHANGE**: Skill no longer creates files automatically
  - `setup_environment()` now only configures settings
  - File creation is the responsibility of Core, not the Skill
  - Users must explicitly call `core.config.init_workspace()` to create files
- Centralized version management: all version numbers now read from `version.py`
- Simplified documentation: removed architecture and security docs (handled by ContextBridge core)
- Updated all examples to show responsibility separation
- Future version updates only require changing one file

### Version 1.0.3
- Updated skill name and description for clarity: "Local Document Search (Privacy-First)"
- Unified version numbers across all files (manifest, code, documentation)
- Improved metadata consistency
- Enhanced privacy-first messaging

### Version 1.0.0
- Initial release
- OpenClaw integration
- Auto environment detection
- Namespace isolation
- Complete documentation
- Test suite

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Authors

- **whyischen** - Original author and maintainer

## Acknowledgments

- OpenClaw framework team
- ContextBridge project contributors
- Community feedback and contributions
