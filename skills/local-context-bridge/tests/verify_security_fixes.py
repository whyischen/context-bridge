"""
Verify security fixes without pytest.

This script verifies that the security fixes are actually working.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from local_context_bridge.openclaw_server import OpenClawServer


def test_localhost_binding():
    """Test that localhost binding works."""
    print("Test 1: Localhost binding (127.0.0.1)...")
    try:
        server = OpenClawServer(host="127.0.0.1", port=8765)
        print("  ✓ PASS: Localhost binding allowed")
        return True
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False


def test_localhost_name_binding():
    """Test that 'localhost' binding works."""
    print("Test 2: Localhost name binding...")
    try:
        server = OpenClawServer(host="localhost", port=8765)
        print("  ✓ PASS: 'localhost' binding allowed")
        return True
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False


def test_ipv6_localhost_binding():
    """Test that IPv6 localhost binding works."""
    print("Test 3: IPv6 localhost binding (::1)...")
    try:
        server = OpenClawServer(host="::1", port=8765)
        print("  ✓ PASS: IPv6 localhost binding allowed")
        return True
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False


def test_all_interfaces_binding_rejected():
    """Test that 0.0.0.0 binding is rejected."""
    print("Test 4: All interfaces binding (0.0.0.0) - should be REJECTED...")
    try:
        server = OpenClawServer(host="0.0.0.0", port=8765)
        print("  ✗ FAIL: 0.0.0.0 binding was allowed (should be rejected)")
        return False
    except ValueError as e:
        if "SECURITY ERROR" in str(e):
            print(f"  ✓ PASS: 0.0.0.0 binding rejected with security error")
            print(f"    Error message: {e}")
            return True
        else:
            print(f"  ✗ FAIL: Wrong error: {e}")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: Unexpected error: {e}")
        return False


def test_specific_interface_binding_rejected():
    """Test that specific interface binding is rejected."""
    print("Test 5: Specific interface binding (192.168.1.100) - should be REJECTED...")
    try:
        server = OpenClawServer(host="192.168.1.100", port=8765)
        print("  ✗ FAIL: 192.168.1.100 binding was allowed (should be rejected)")
        return False
    except ValueError as e:
        if "SECURITY ERROR" in str(e):
            print(f"  ✓ PASS: 192.168.1.100 binding rejected with security error")
            return True
        else:
            print(f"  ✗ FAIL: Wrong error: {e}")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: Unexpected error: {e}")
        return False


def test_external_ip_binding_rejected():
    """Test that external IP binding is rejected."""
    print("Test 6: External IP binding (8.8.8.8) - should be REJECTED...")
    try:
        server = OpenClawServer(host="8.8.8.8", port=8765)
        print("  ✗ FAIL: 8.8.8.8 binding was allowed (should be rejected)")
        return False
    except ValueError as e:
        if "SECURITY ERROR" in str(e):
            print(f"  ✓ PASS: 8.8.8.8 binding rejected with security error")
            return True
        else:
            print(f"  ✗ FAIL: Wrong error: {e}")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: Unexpected error: {e}")
        return False


def test_auto_setup_default():
    """Test that auto_setup defaults to False."""
    print("Test 7: auto_setup default value...")
    try:
        from local_context_bridge.skill import LocalContextBridgeSkill
        import inspect
        
        skill = LocalContextBridgeSkill()
        sig = inspect.signature(skill.initialize)
        auto_setup_default = sig.parameters['auto_setup'].default
        
        if auto_setup_default is False:
            print(f"  ✓ PASS: auto_setup defaults to False")
            return True
        else:
            print(f"  ✗ FAIL: auto_setup defaults to {auto_setup_default} (should be False)")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False


def test_environment_detector():
    """Test that EnvironmentDetector checks cbridge-agent."""
    print("Test 8: EnvironmentDetector checks cbridge-agent...")
    try:
        from local_context_bridge.environment import EnvironmentDetector
        
        detector = EnvironmentDetector()
        is_installed = detector.is_cbridge_installed()
        
        print(f"  ✓ PASS: cbridge-agent installed: {is_installed}")
        return True
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False


def test_endpoint_defaults():
    """Test that endpoints default to localhost."""
    print("Test 9: Network endpoints default to localhost...")
    try:
        from local_context_bridge.environment import EnvironmentDetector
        
        detector = EnvironmentDetector()
        qmd_endpoint = detector.get_qmd_endpoint()
        openviking_endpoint = detector.get_openviking_endpoint()
        
        if qmd_endpoint == "http://localhost:9090" and openviking_endpoint == "http://localhost:8080":
            print(f"  ✓ PASS: Endpoints default to localhost")
            print(f"    QMD: {qmd_endpoint}")
            print(f"    OpenViking: {openviking_endpoint}")
            return True
        else:
            print(f"  ✗ FAIL: Endpoints not localhost")
            print(f"    QMD: {qmd_endpoint}")
            print(f"    OpenViking: {openviking_endpoint}")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False


def main():
    """Run all security verification tests."""
    print("=" * 70)
    print("SECURITY FIXES VERIFICATION")
    print("=" * 70)
    print()
    
    tests = [
        test_localhost_binding,
        test_localhost_name_binding,
        test_ipv6_localhost_binding,
        test_all_interfaces_binding_rejected,
        test_specific_interface_binding_rejected,
        test_external_ip_binding_rejected,
        test_auto_setup_default,
        test_environment_detector,
        test_endpoint_defaults,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ FAIL: Unexpected error: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ ALL SECURITY FIXES VERIFIED")
        return 0
    else:
        print(f"✗ {total - passed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
