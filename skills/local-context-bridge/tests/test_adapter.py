#!/usr/bin/env python3
"""Test script for OpenClaw Adapter."""

import json
import sys
from openclaw_adapter import get_adapter, initialize_adapter
from openclaw_protocol import create_protocol_handler


def test_adapter_direct():
    """Test adapter directly."""
    print("=" * 60)
    print("Testing Adapter Direct Usage")
    print("=" * 60)
    
    # Initialize
    print("\n1. Initializing adapter...")
    result = initialize_adapter()
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    
    # Get adapter
    adapter = get_adapter()
    
    # Get skill info
    print("\n2. Getting skill info...")
    info = adapter.get_skill_info()
    print(f"   Name: {info['name']}")
    print(f"   Version: {info['version']}")
    print(f"   Capabilities: {len(info['capabilities'])}")
    
    # Detect environment
    print("\n3. Detecting environment...")
    result = adapter.call_capability("detect_environment", {})
    if result["status"] == "success":
        env = result.get("environment", {})
        print(f"   OS: {env.get('os')}")
        print(f"   Python: {env.get('python_version')}")
        print(f"   ContextBridge Installed: {env.get('cbridge_installed')}")
        print(f"   QMD Running: {env.get('qmd_running')}")
        print(f"   OpenViking Running: {env.get('openviking_running')}")
    else:
        print(f"   Error: {result['message']}")
    
    # Get status
    print("\n4. Getting status...")
    result = adapter.call_capability("get_status", {})
    if result["status"] == "success":
        print(f"   Configured: {result.get('configured')}")
        print(f"   Watch Dirs: {result.get('watch_directories', [])}")
    else:
        print(f"   Error: {result['message']}")
    
    print("\n" + "=" * 60)


def test_protocol_handler():
    """Test protocol handler."""
    print("=" * 60)
    print("Testing Protocol Handler")
    print("=" * 60)
    
    handler = create_protocol_handler()
    
    # Test initialize request
    print("\n1. Testing skill.initialize request...")
    request = {
        "jsonrpc": "2.0",
        "method": "skill.initialize",
        "params": {},
        "id": "1"
    }
    response = handler.handle_request(request)
    print(f"   Response: {json.dumps(response, indent=2)}")
    
    # Test getInfo request
    print("\n2. Testing skill.getInfo request...")
    request = {
        "jsonrpc": "2.0",
        "method": "skill.getInfo",
        "params": {},
        "id": "2"
    }
    response = handler.handle_request(request)
    print(f"   Skill Name: {response['result']['name']}")
    print(f"   Capabilities: {len(response['result']['capabilities'])}")
    
    # Test capability call
    print("\n3. Testing skill.call request (detect_environment)...")
    request = {
        "jsonrpc": "2.0",
        "method": "skill.call",
        "params": {
            "capability": "detect_environment",
            "parameters": {}
        },
        "id": "3"
    }
    response = handler.handle_request(request)
    if response['result']['status'] == 'success':
        print(f"   OS: {response['result']['environment'].get('os')}")
        print(f"   Python: {response['result']['environment'].get('python_version')}")
    
    # Test batch request
    print("\n4. Testing batch request...")
    requests = [
        {
            "jsonrpc": "2.0",
            "method": "skill.getInfo",
            "params": {},
            "id": "4"
        },
        {
            "jsonrpc": "2.0",
            "method": "skill.getStatus",
            "params": {},
            "id": "5"
        }
    ]
    responses = handler.handle_batch_request(requests)
    print(f"   Batch responses: {len(responses)}")
    
    print("\n" + "=" * 60)


def main():
    """Run all tests."""
    try:
        test_adapter_direct()
        test_protocol_handler()
        print("\n✓ All tests completed successfully!")
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
