# Security Guide for Local ContextBridge Skill

## Overview

This document provides detailed security information for the Local ContextBridge Skill, including threat analysis, mitigation strategies, and best practices.

## Executive Summary

The Local ContextBridge Skill is designed with security in mind:

- **Local-Only**: All documents and operations remain on your machine
- **Transparent**: All setup operations are logged and auditable
- **Controlled**: Users can disable auto-setup and review operations before enabling
- **Pinned Dependencies**: Uses exact version pinning for reproducibility
- **Minimal Permissions**: Only requests necessary permissions

## Dependency Management

### Version Pinning

The skill requires `cbridge-agent==0.1.5` (exact version):

```
cbridge-agent==0.1.5
```

This ensures:
- **Reproducibility**: Same version installed every time
- **Security**: No unexpected updates with potential vulnerabilities
- **Auditability**: Easy to verify which versions are in use
- **Transparency**: Version declared in manifest.json matches actual requirement

### Installation Process

**IMPORTANT**: The skill does NOT perform automatic pip install. Users must install manually:

```bash
pip install cbridge-agent==0.1.5
```

**Why manual installation?**
1. **Explicit User Control**: Users must consciously install the dependency
2. **Security**: No automatic code execution during skill initialization
3. **Transparency**: Users can review what they're installing
4. **Auditability**: Installation is user-initiated, not automatic

### Verifying Installation

To verify the installed version:

```bash
pip show cbridge-agent
# Should show: Version: 0.1.5
```

To verify the skill can find the dependency:

```python
from local_context_bridge import LocalContextBridgeSkill
skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)
# If cbridge-agent is not installed, you'll get an error message
# with instructions to install it manually
```

## File System Security

### Configuration Storage

Configuration is stored at `~/.cbridge/config.yaml`:

```yaml
mode: embedded
workspace_dir: ~/.cbridge/workspace
watch_directories:
  - ~/Documents/Projects
auto_setup: true
```

**Permissions**: Standard user permissions (typically 0644 for files, 0755 for directories)

### Audit Logging

All setup operations are logged to `~/.cbridge/setup.log`:

```
2024-01-15 10:30:45,123 - INFO - Starting auto_setup for ContextBridge
2024-01-15 10:30:45,456 - INFO - cbridge-agent is installed
2024-01-15 10:30:53,012 - INFO - Environment detection: QMD=False, OpenViking=False
2024-01-15 10:30:53,234 - INFO - No external services detected, using embedded mode
```

**Review this log** to verify all operations performed by the skill.

### Workspace Directory

The skill creates a workspace directory at `~/.cbridge/workspace/`:

```
~/.cbridge/workspace/
├── index/          # Document index
├── cache/          # Cached data
└── metadata/       # Metadata files
```

**Permissions**: User-only (0700 for directories, 0600 for files)

## Network Security

### Local-Only Network Access

The skill only accesses local network endpoints:

- `http://127.0.0.1:9090/health` - QMD service check
- `http://127.0.0.1:8080/health` - OpenViking service check

**No external network connections are made.**

### Network Probing

During environment detection, the skill probes these endpoints to determine if external services are available. This is a **read-only operation** that does not modify any services.

### Disabling Network Access

To use embedded mode without network probing:

```python
skill = LocalContextBridgeSkill()
result = skill.setup_environment(mode='embedded')
```

## Subprocess Execution

### No Automatic Pip Install

The skill does NOT execute pip install automatically. Users must install cbridge-agent manually:

```bash
pip install cbridge-agent==0.1.5
```

**Why this design?**
- No automatic code execution during skill initialization
- Users have explicit control over dependency installation
- Transparent and auditable process
- Aligns with security best practices

### Document Indexing

Document indexing is performed by cbridge-agent:

```python
from core.watcher import index_all
index_all()
```

**Security measures:**
- Operates on local files only
- Respects file permissions
- Logged to audit trail

## Network Security

### Server Binding

The OpenClaw server must only bind to localhost (127.0.0.1):

```python
# CORRECT
run_server(host="127.0.0.1", port=8765)

# INCORRECT - DO NOT USE
run_server(host="0.0.0.0", port=8765)
```

### Threat: Network Exposure

**Risk**: Server bound to 0.0.0.0 or other network interfaces exposes local documents to the network

**Mitigation**:
- Default binding is localhost only (127.0.0.1)
- Code validates binding address and rejects non-localhost
- Documentation clearly warns against network exposure
- Examples only show localhost binding

**Residual Risk**: Very Low (with validation in place)

### Best Practices

1. **Always use localhost**: Bind to 127.0.0.1 only
2. **Never use 0.0.0.0**: This exposes to all network interfaces
3. **Verify binding**: Check that server is listening on localhost only
4. **Monitor access**: Review logs for unexpected connections
5. **Use firewall**: Add firewall rules to restrict access

## Auto-Setup Behavior

### Default: Explicit User Approval Required

By default, `initialize(auto_setup=False)` requires explicit user approval:

```python
skill = LocalContextBridgeSkill()
result = skill.initialize()  # auto_setup=False by default

# No automatic operations performed
# User must explicitly call setup_environment()
```

### Why Explicit Approval?

1. **Security**: Users know exactly what operations will be performed
2. **Transparency**: No hidden automatic operations
3. **Control**: Users can review environment before setup
4. **Auditability**: All operations are intentional and logged

### Automatic Setup (Optional)

Users can enable automatic setup if desired:

```python
skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=True)

# Automatically detects environment and configures
# Only use after reviewing what will happen
```

### Best Practice

For security-critical environments:

```python
# Step 1: Initialize without auto-setup
skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)

# Step 2: Review environment
env = skill.detect_environment()
print(env)

# Step 3: Explicitly setup after review
result = skill.setup_environment(mode='embedded')
```

### Threat: Unexpected Automatic Operations

**Risk**: Automatic operations performed without user knowledge

**Mitigation**:
- Default is `auto_setup=False` (no automatic operations)
- User must explicitly enable auto-setup
- All operations logged to `~/.cbridge/setup.log`
- User can review operations before enabling

**Residual Risk**: Very Low (with explicit approval required)

## Threat Model

### Threat: Malicious Dependency

**Risk**: Installed package contains malicious code

**Mitigation**:
- Manual installation gives users explicit control
- Version pinning ensures reproducible builds
- Audit logging records all operations
- Users can review source code before installing
- Can use `auto_setup=False` for manual review

**Residual Risk**: Very Low (users have full control over installation)

### Threat: Unauthorized File Access

**Risk**: Skill reads files outside watched directories

**Mitigation**:
- Only reads files in configured watch directories
- Respects file system permissions
- No elevated privileges required
- Audit logging records all file operations

**Residual Risk**: Very Low

### Threat: Network Exfiltration

**Risk**: Skill sends data to external services

**Mitigation**:
- All documents remain local
- Only local network endpoints are accessed
- No external API calls
- Network access can be disabled

**Residual Risk**: Very Low

### Threat: Configuration Tampering

**Risk**: Configuration file is modified by unauthorized process

**Mitigation**:
- Configuration stored in user home directory
- Standard file permissions
- Audit logging records all modifications
- Configuration validation on load

**Residual Risk**: Low (depends on system security)

### Threat: Privilege Escalation

**Risk**: Skill attempts to gain elevated privileges

**Mitigation**:
- No elevated privileges required
- No sudo/admin calls
- Runs with user permissions only

**Residual Risk**: Very Low

## Security Best Practices

### 1. Install Dependency Manually

Before using the skill, install cbridge-agent:

```bash
pip install cbridge-agent==0.1.5
```

### 2. Review Setup Operations

Before enabling the skill, review what operations will be performed:

```python
from local_context_bridge import LocalContextBridgeSkill

skill = LocalContextBridgeSkill()

# Detect environment without making changes
env = skill.detect_environment()
print(f"Environment: {env}")

# Review setup operations
status = skill.get_status()
print(f"Current status: {status}")

# Explicitly setup after review
result = skill.setup_environment(mode='embedded')
```

### 3. Monitor Audit Logs

Regularly review the setup log:

```bash
cat ~/.cbridge/setup.log
```

Look for:
- Unexpected operations
- Failed operations
- Unusual timestamps

### 4. Verify Permissions

Check file permissions:

```bash
ls -la ~/.cbridge/
# Should show user-only permissions
```

### 5. Keep Dependencies Updated

Monitor for security updates:

```bash
pip list --outdated
```

When updates are available, update and re-test:

```bash
pip install --upgrade cbridge-agent==0.1.5
```

### 6. Use Explicit Setup for Security-Critical Environments

For production or security-critical deployments:

```python
# Disable auto-setup
skill = LocalContextBridgeSkill()
result = skill.initialize(auto_setup=False)

# Manually review and setup
result = skill.setup_environment(mode='embedded')
```

### 7. Limit Watch Directories

Only monitor directories that contain relevant documents:

```python
# Good: Specific project directories
skill.add_watch_directory('~/Documents/Projects/MyProject')

# Avoid: Entire home directory
skill.add_watch_directory('~')
```

### 8. Regular Audits

Periodically audit the skill's operations:

```bash
# Check setup log
tail -20 ~/.cbridge/setup.log

# Verify configuration
cat ~/.cbridge/config.yaml

# Check disk usage
du -sh ~/.cbridge/
```

## Incident Response

### If You Suspect Unauthorized Access

1. **Stop the skill**: Disable or uninstall the skill
2. **Review logs**: Check `~/.cbridge/setup.log` for suspicious activity
3. **Check permissions**: Verify file permissions on `~/.cbridge/`
4. **Audit documents**: Review which directories are being monitored
5. **Report**: If you find evidence of compromise, report to the project

### If Installation Fails

1. **Check logs**: Review `~/.cbridge/setup.log`
2. **Verify pip**: Ensure pip is working correctly
3. **Check network**: Verify internet connection for package download
4. **Manual install**: Try manual installation:
   ```bash
   pip install cbridge-agent==0.1.5
   ```

### If You Find a Security Issue

1. **Do not publicly disclose** the vulnerability
2. **Report privately** to the project maintainers
3. **Include details**: Version, reproduction steps, impact
4. **Allow time** for a fix before public disclosure

## Compliance

### Data Privacy

- **GDPR**: All data remains local, no external processing
- **CCPA**: User has full control over data location
- **HIPAA**: Can be deployed in compliant environments (with proper infrastructure)

### Audit Requirements

The skill provides:
- Audit logging to `~/.cbridge/setup.log`
- Configuration tracking
- Operation logging
- Timestamp recording

### Permissions Model

The skill operates with user permissions only:
- No elevated privileges
- No system-wide modifications
- No shared resources

## FAQ

### Q: Does the skill send data to external services?

**A**: No. All documents remain on your local machine. The skill only probes local network endpoints (127.0.0.1:9090, 127.0.0.1:8080) to detect if external services are available.

### Q: Does the skill automatically install dependencies?

**A**: No. Users must install cbridge-agent manually: `pip install cbridge-agent==0.1.5`. This gives you explicit control over what gets installed.

### Q: Can I disable auto-setup?

**A**: Yes. Use `initialize(auto_setup=False)` to disable automatic setup and review operations before enabling.

### Q: How do I verify the installed version?

**A**: Run `pip show cbridge-agent` to verify the version is 0.1.5.

### Q: What if I don't trust the dependency?

**A**: You can:
1. Review the cbridge-agent source code on GitHub
2. Use `auto_setup=False` and manually review before enabling
3. Use embedded mode to avoid external service connections
4. Monitor the audit log for all operations
5. Choose not to install it and use alternative tools

### Q: Can I use this in a production environment?

**A**: Yes, with proper security review:
1. Review the source code
2. Test in a staging environment
3. Monitor audit logs
4. Use explicit setup (`auto_setup=False`)
5. Implement regular audits
6. Install dependencies manually with explicit version pinning

### Q: How do I report a security issue?

**A**: Contact the project maintainers privately with:
- Version number
- Reproduction steps
- Impact assessment
- Suggested fix (if available)

## References

- [OWASP Security Guidelines](https://owasp.org/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [PyPI Security](https://pypi.org/help/#security)

## Version History

- **1.0.0** (2024-01-15): Initial security documentation
