# Local ContextBridge Skill - Complete Guide

## Overview

**Local ContextBridge** is an OpenClaw Skill that provides local document search and context management capabilities for AI agents. It enables intelligent searching through Word, Excel, PDF, and Markdown files without uploading documents to external services.

**Skill ID**: `local-context-bridge`  
**Version**: 1.0.0  
**Author**: whyischen  
**License**: MIT

## Key Features

- **Automatic Environment Detection**: Intelligently detects your system setup and chooses optimal configuration
- **Privacy-First**: All documents remain local - no uploading or external processing
- **Smart Service Integration**: Automatically detects and reuses existing QMD and OpenViking instances
- **Namespace Isolation**: Prevents document conflicts with other applications
- **Multi-Format Support**: Indexes Word, Excel, PDF, and Markdown files
- **Watch Directory Management**: Monitor specific directories for automatic indexing
- **Flexible Deployment**: Choose between embedded (built-in) or external (service-based) modes

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Install cbridge-agent (Required)

```bash
pip install cbridge-agent==0.1.5
```

**Important:** You must install `cbridge-agent` manually before using this skill. The skill will not perform automatic installation. This is a deliberate design choice for security and transparency.

### Step 2: Initialize the Skill

```bash
cbridge init
```

### Step 3: Install from PyPI

```bash
pip install local-context-bridge
```

### Step 4: Install from Source (Alternative)

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

### 2. Initialize the Skill

```bash
cbridge init
```

This command:
- Detects your system environment
- Checks for existing QMD and OpenViking services
- Configures based on available services
- Sets up the workspace

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

Initialize the skill with optional automatic setup.

**IMPORTANT:** cbridge-agent must be installed before calling this method.
```bash
pip install cbridge-agent==0.1.5
```

**Parameters:**
- `auto_setup` (bool): Automatically setup if not configured (default: **False**)
  - `False` (recommended): Requires explicit setup call after reviewing operations
    - User must call `setup_environment()` explicitly
    - No automatic operations are performed
    - Recommended for security-conscious deployments
  - `True`: Automatically detects environment and configures
    - Automatically calls `setup_environment(mode='auto')`
    - Creates configuration files
    - Probes local network endpoints
    - Only use after ensuring cbridge-agent is installed

**Default Behavior (auto_setup=False):**

When `auto_setup=False` (the default), the skill will NOT automatically setup:

```python
skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)  # Default

# Result: "not_configured" status
# No automatic operations performed
# User must explicitly call setup_environment()
```

**Automatic Setup (auto_setup=True):**

When `auto_setup=True`, the skill will automatically setup:

```python
skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=True)

# Result: Automatically detects environment and configures
# Creates ~/.cbridge/config.yaml
# Probes localhost:9090 and localhost:8080
# Chooses embedded or external mode
```

**Security Recommendation:**

For security-conscious deployments, use explicit setup:

```python
skill = LocalContextBridgeSkill()

# Step 1: Initialize without auto-setup
result = skill.initialize(auto_setup=False)

# Step 2: Review environment
env = skill.detect_environment()
print(env)

# Step 3: Explicitly setup after review
setup_result = skill.setup_environment(mode='embedded')
```

**Returns:**
```json
{
  "status": "success",
  "message": "Skill initialized successfully",
  "metadata": {
    "name": "local-context-bridge",
    "displayName": "Local ContextBridge",
    "version": "1.0.0",
    "capabilities": [...]
  }
}
```

Or if not configured:
```json
{
  "status": "not_configured",
  "message": "Skill not configured. Call setup_environment() to configure.",
  "hint": "First ensure cbridge-agent is installed: pip install cbridge-agent==0.1.5",
  "next_steps": [
    "1. Install cbridge-agent: pip install cbridge-agent==0.1.5",
    "2. Call detect_environment() to review available services",
    "3. Call setup_environment(mode='embedded' or 'external') to configure"
  ]
}
```

**Example:**
```python
from local_context_bridge import LocalContextBridgeSkill

# First ensure cbridge-agent is installed
# pip install cbridge-agent==0.1.5

skill = LocalContextBridgeSkill()

# Option 1: Manual setup (recommended for security)
result = skill.initialize(auto_setup=False)
if result["status"] == "not_configured":
    # Review environment
    env = skill.detect_environment()
    print(env)
    
    # Then setup explicitly
    setup_result = skill.setup_environment(mode='embedded')

# Option 2: Automatic setup (only after reviewing operations)
result = skill.initialize(auto_setup=True)
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

**Example:**
```python
env = skill.detect_environment()
if env["status"] == "success":
    print(f"OS: {env['environment']['os_type']}")
    print(f"Python: {env['environment']['python_version']}")
```

---

#### `setup_environment(workspace_dir=None, mode='auto')`

Setup ContextBridge environment with specified mode.

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
# Auto-detect and setup
result = skill.setup_environment()

# Force embedded mode
result = skill.setup_environment(mode='embedded')

# Use external services with custom workspace
result = skill.setup_environment(
    workspace_dir='/custom/path',
    mode='external'
)
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

**Example:**
```python
result = skill.add_watch_directory('~/Documents/Projects')
if result["status"] == "success":
    print(result["message"])
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

**Example:**
```python
result = skill.remove_watch_directory('~/Documents/OldProjects')
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

**Example:**
```python
dirs = skill.get_watch_directories()
for directory in dirs["directories"]:
    print(f"Monitoring: {directory}")
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

**Example:**
```python
status = skill.get_status()
print(f"Configured: {status['configured']}")
print(f"Mode: {status['config_summary']}")
print(f"Watched directories: {len(status['watch_directories'])}")
```

---

#### `get_metadata()`

Get skill metadata and capabilities.

**Returns:**
```json
{
  "name": "local-context-bridge",
  "displayName": "Local ContextBridge",
  "version": "1.0.0",
  "description": "Local document search and context management for AI agents",
  "capabilities": [
    "search_documents",
    "setup_environment",
    "detect_environment",
    "manage_watch_dirs"
  ]
}
```

## Network Security

### Server Binding

The OpenClaw server must only bind to localhost:

```python
# CORRECT: Localhost only
run_server(host="127.0.0.1", port=8765)

# INCORRECT: Exposes to network
run_server(host="0.0.0.0", port=8765)  # DO NOT USE

# INCORRECT: Exposes to specific interface
run_server(host="192.168.1.100", port=8765)  # DO NOT USE
```

### Why Localhost Only?

- **Security**: Prevents unauthorized network access to local documents
- **Privacy**: Keeps all data local and private
- **Compliance**: Aligns with data protection requirements
- **Best Practice**: Standard for local development tools

### If You Need Network Access

If you need to expose the service to a network:

1. **Implement Authentication**: Add proper authentication layer
2. **Use VPN**: Tunnel through encrypted connection
3. **Use Firewall**: Restrict access to trusted IPs
4. **Use Reverse Proxy**: Add security layer (nginx, Apache)
5. **Encrypt Data**: Use TLS/SSL for all connections

Example with authentication:

```python
from local_context_bridge import run_server
from some_auth_library import require_auth

# Add authentication middleware
@require_auth
def secure_run_server():
    run_server(host="127.0.0.1", port=8765)
```

## Deployment Modes

### Embedded Mode (Default)

Uses built-in ChromaDB for document indexing and retrieval.

**Advantages:**
- No external dependencies
- Standalone operation
- Minimal setup
- Lower resource overhead

**Best for:**
- Single-user setups
- Development and testing
- Standalone applications

**Configuration:**
```python
skill.setup_environment(mode='embedded')
```

### External Mode (Auto-detected)

Connects to existing QMD (Quantum Metadata Database) and OpenViking services.

**Advantages:**
- Shared infrastructure
- Namespace isolation
- Scalable architecture
- Service reuse

**Best for:**
- Multi-application environments
- Enterprise deployments
- Shared infrastructure

**Namespace Isolation:**
- QMD Collection: `contextbridge_docs`
- OpenViking Mount: `viking://contextbridge/`

**Configuration:**
```python
skill.setup_environment(mode='external')
```

## Configuration

### Configuration Management

Configuration is managed by the ContextBridge Core module (`core.config`). The skill delegates all configuration operations to the core:

- **Configuration Storage**: Handled by `core.config`
- **Configuration Format**: Defined by ContextBridge Core
- **Configuration Location**: Determined by ContextBridge Core (typically `~/.cbridge/config.yaml`)

### Environment Variables (Optional)

The skill reads these optional environment variables if set:

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `CBRIDGE_WORKSPACE` | Custom workspace directory | `~/ContextBridge_Workspace` | `/custom/path/to/workspace` |
| `CBRIDGE_MODE` | Deployment mode | Auto-detect | `embedded` or `external` |
| `QMD_ENDPOINT` | QMD service endpoint | `http://localhost:9090` | `http://qmd.example.com:9090` |
| `OPENVIKING_ENDPOINT` | OpenViking service endpoint | `http://localhost:8080` | `http://viking.example.com:8080` |

**Important:** All environment variables are optional. The skill works without them and will auto-detect the best configuration.

### Configuration File Format

The configuration file (managed by `core.config`) contains:

```yaml
mode: external                    # 'embedded' or 'external'
workspace_dir: ~/ContextBridge_Workspace
watch_dirs:
  - ~/Documents/Projects
  - ~/Downloads/Research
qmd:
  endpoint: http://localhost:9090
  collection: contextbridge_docs
openviking:
  endpoint: http://localhost:8080
  mount_path: viking://contextbridge/
```

### Setting Environment Variables

**Linux/macOS:**
```bash
export CBRIDGE_WORKSPACE=/custom/path
export CBRIDGE_MODE=embedded
```

**Windows (PowerShell):**
```powershell
$env:CBRIDGE_WORKSPACE = "C:\custom\path"
$env:CBRIDGE_MODE = "embedded"
```

**Windows (CMD):**
```cmd
set CBRIDGE_WORKSPACE=C:\custom\path
set CBRIDGE_MODE=embedded
```

## Usage Examples

### Example 1: Basic Document Search

```python
from local_context_bridge import LocalContextBridgeSkill

# First ensure cbridge-agent is installed
# pip install cbridge-agent==0.1.5

# Initialize skill
skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)

if result["status"] == "not_configured":
    # Setup explicitly
    skill.setup_environment(mode='embedded')

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
# First ensure cbridge-agent is installed
# pip install cbridge-agent==0.1.5

from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()

# Initialize without auto-setup
result = skill.initialize(auto_setup=False)

if result["status"] == "not_configured":
    # Setup explicitly
    skill.setup_environment(mode='auto')

# Add directories to monitor
skill.add_watch_directory('~/Documents/Projects')
skill.add_watch_directory('~/Downloads/Research')

# View monitored directories
dirs = skill.get_watch_directories()
print(f"Monitoring {dirs['count']} directories")

# Get current status
status = skill.get_status()
print(f"Configuration: {status['config_summary']}")
```

### Example 3: Environment Detection

```python
# First ensure cbridge-agent is installed
# pip install cbridge-agent==0.1.5

from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()

# Initialize without auto-setup
skill.initialize(auto_setup=False)

# Detect environment
env = skill.detect_environment()

if env["status"] == "success":
    env_info = env["environment"]
    
    if env_info["qmd_available"] and env_info["openviking_available"]:
        print("External services available - using external mode")
        skill.setup_environment(mode='external')
    else:
        print("Using embedded mode")
        skill.setup_environment(mode='embedded')
```

### Example 4: OpenClaw Integration

```python
# First ensure cbridge-agent is installed
# pip install cbridge-agent==0.1.5

from local_context_bridge import initialize_adapter, call_capability

# Initialize adapter (requires manual setup first)
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

## Supported File Formats

| Format | Extension | Support |
|--------|-----------|---------|
| Microsoft Word | .docx, .doc | ✓ Full |
| Microsoft Excel | .xlsx, .xls | ✓ Full |
| PDF | .pdf | ✓ Full |
| Markdown | .md | ✓ Full |
| Plain Text | .txt | ✓ Full |

## Architecture

```
┌─────────────────────────────────────────┐
│         OpenClaw Framework              │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│    OpenClaw Protocol Handler            │
│    (JSON-RPC over WebSocket)            │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      OpenClaw Adapter                   │
│  (Skill Interface & Capability Routing) │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│   LocalContextBridgeSkill               │
│  (Core Skill Implementation)            │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌────────▼────────┐
│  Embedded Mode │   │ External Mode   │
│  (ChromaDB)    │   │ (QMD + Viking)  │
└────────────────┘   └─────────────────┘
```

## Troubleshooting

### Issue: Skill fails to initialize

**Solution:**
```bash
# Ensure cbridge-agent is installed
pip install cbridge-agent==0.1.5

# Verify installation
pip list | grep cbridge

# Check status
cbridge status
```

If you see "cbridge-agent is not installed" error:
1. Install manually: `pip install cbridge-agent==0.1.5`
2. Then initialize the skill again

### Issue: No search results found

**Solution:**
```bash
# List watched directories
cbridge watch list

# Rebuild index
cbridge index --force

# Verify file formats are supported
ls -la ~/Documents/Projects
```

### Issue: Connection refused (External mode)

**Solution:**
```bash
# Check QMD service
curl http://localhost:9090/health

# Check OpenViking service
curl http://localhost:8080/health

# Fall back to embedded mode
cbridge config set mode embedded
cbridge restart
```

### Issue: High memory usage

**Solution:**
- Reduce number of watched directories
- Use external mode for better resource management
- Limit index size with configuration

## Performance Considerations

### Search Performance

- **Embedded Mode**: ~100-500ms for typical queries
- **External Mode**: ~50-200ms (with service overhead)

### Indexing Performance

- **Initial Index**: ~1-5 minutes per 1000 documents
- **Incremental Updates**: ~100-500ms per document

### Memory Usage

- **Embedded Mode**: ~200-500MB base + document size
- **External Mode**: ~50-100MB (delegated to services)

## Security

### Privacy

- All documents remain on local machine
- No data sent to external services (except QMD/OpenViking if used)
- Namespace isolation prevents cross-application access

### Permissions

The skill requires:
- `file_read`: Read document files from user-specified watch directories
- `file_write`: Write configuration and cache to `~/.cbridge/` directory only
- `local_storage`: Store configuration, cache, and document index in `~/.cbridge/`
- `network_access`: Probe local network endpoints (127.0.0.1:9090, 127.0.0.1:8080) only

**Note:** `process_execution` permission is NOT required. The skill does not execute pip install automatically.

### Security Considerations

#### Dependency Installation

This skill requires `cbridge-agent==0.1.5` to be installed manually before use. This is a **deliberate design choice** for security:

1. **Explicit User Control**: Users must explicitly install the dependency
2. **Version Transparency**: Exact version `0.1.5` is pinned and declared in manifest
3. **No Automatic Execution**: The skill does not execute pip install automatically
4. **Audit Trail**: All setup operations are logged to `~/.cbridge/setup.log`

**Installation:**
```bash
pip install cbridge-agent==0.1.5
```

**For security-conscious deployments:**
```python
# Step 1: Install dependency manually
# pip install cbridge-agent==0.1.5

# Step 2: Initialize without auto-setup
skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)

# Step 3: Review environment
env = skill.detect_environment()
print(env)

# Step 4: Explicitly call setup after review
result = skill.setup_environment(mode='embedded')
```

#### File System Access

The skill creates and manages:
- `~/.cbridge/config.yaml` - Configuration file
- `~/.cbridge/setup.log` - Audit log of setup operations
- `~/.cbridge/workspace/` - Document index and cache

These are created in the user's home directory with standard permissions. The skill only writes to `~/.cbridge/` directory.

#### Network Access

The skill probes local network endpoints during environment detection:
- `http://127.0.0.1:9090/health` - QMD service check
- `http://127.0.0.1:8080/health` - OpenViking service check

These are **local-only** probes and do not connect to external services.

#### Environment Variables

The skill reads (but does not require) these environment variables:
- `CBRIDGE_WORKSPACE` - Custom workspace directory
- `CBRIDGE_MODE` - Deployment mode ('embedded' or 'external')
- `QMD_ENDPOINT` - QMD service endpoint
- `OPENVIKING_ENDPOINT` - OpenViking service endpoint

These are optional and only used if explicitly set by the user.

### Audit Trail

All setup operations are logged to `~/.cbridge/setup.log`:

```
2024-01-15 10:30:45,123 - INFO - Starting auto_setup for ContextBridge
2024-01-15 10:30:45,456 - INFO - cbridge-agent is installed
2024-01-15 10:30:53,012 - INFO - Environment detection: QMD=False, OpenViking=False
2024-01-15 10:30:53,234 - INFO - No external services detected, using embedded mode
```

Review this log to verify all operations performed by the skill.

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| Malicious dependency | Manual installation, version pinning, audit logging |
| Unauthorized file access | Standard Unix permissions, local-only, scoped to `~/.cbridge/` |
| Network exfiltration | Local-only network access, no external connections |
| Privilege escalation | No elevated privileges required |
| Configuration tampering | File permissions, audit logging |
| Automatic code execution | No automatic pip install, explicit user control |

### Recommendations

1. **Install Manually**: Install cbridge-agent manually before using the skill
2. **Review Setup Log**: Check `~/.cbridge/setup.log` after initialization
3. **Use Explicit Setup**: For security-critical environments, use `auto_setup=False`
4. **Monitor Permissions**: Verify `~/.cbridge/` directory permissions
5. **Audit Regularly**: Review setup logs periodically
6. **Bind to Localhost**: When running WebSocket server, bind to `127.0.0.1` only

## Advanced Configuration

### Custom Workspace Directory

```python
skill.setup_environment(
    workspace_dir='/custom/path/to/workspace',
    mode='embedded'
)
```

### Batch Operations

```python
# Add multiple directories
directories = [
    '~/Documents/Projects',
    '~/Downloads/Research',
    '~/Desktop/Notes'
]

for directory in directories:
    skill.add_watch_directory(directory)

# Rebuild index
import subprocess
subprocess.run(['cbridge', 'index', '--force'])
```

## Integration with Other Tools

### With OpenClaw Commands

```
/enable local-context-bridge
/local-context-bridge search "query"
/local-context-bridge status
/local-context-bridge add-watch-dir ~/path
```

### With Python Applications

```python
from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()
skill.initialize()

# Use in your application
def find_relevant_docs(query):
    results = skill.search_documents(query, top_k=10)
    return results["results"]
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

# First ensure cbridge-agent is installed
# pip install cbridge-agent==0.1.5

skill = LocalContextBridgeSkill()

# Test initialization without auto-setup
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
- **[Architecture Diagrams](./ARCHITECTURE_DIAGRAM.md)** - System architecture

## Support & Community

- **Documentation**: See related docs in this repository
- **Issues**: Report bugs on GitHub
- **Discussions**: Join community discussions

## License

MIT License - See LICENSE file for details

## Changelog

### Version 1.0.0 (Current)
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
