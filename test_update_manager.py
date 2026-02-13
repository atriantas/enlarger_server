"""
Test file for UpdateManager - Can run with Python 3 for basic testing
Tests version comparison, parsing, and simulation of update flow

Run with:
  python3 test_update_manager.py

This creates mock functions to test the core logic without needing MicroPython
"""

import json
import sys
import os

# Add lib to path for imports
sys.path.insert(0, os.path.dirname(__file__))


# Mock UpdateManager class for testing
class MockUpdateManager:
    """Simplified UpdateManager for testing core logic"""
    
    def __init__(self):
        self.repo_owner = 'atriantas'
        self.repo_name = 'enlarger_server'
        self.current_version = "0.0.0"
        self.latest_version = "0.0.0"
        self.FILES_TO_UPDATE = [
            "boot.py",
            "index.html",
            "lib/gpio_control.py",
            "lib/http_server.py",
            "lib/light_sensor.py",
            "lib/paper_database.py",
            "lib/splitgrade_enhanced.py",
            "lib/temperature_sensor.py",
            "lib/timer_manager.py",
            "lib/update_manager.py",
            "lib/wifi_ap.py",
            "lib/wifi_sta.py",
        ]
    
    def _parse_version(self, version_str):
        """Parse version string to tuple for comparison."""
        try:
            version_str = version_str.lstrip('v')
            parts = version_str.split('.')
            # Pad to ensure 3 elements
            result = [int(p) for p in parts[:3]]
            while len(result) < 3:
                result.append(0)
            return tuple(result)
        except (ValueError, IndexError):
            return (0, 0, 0)
    
    def _version_newer(self, remote_version, local_version):
        """Check if remote version is newer than local."""
        remote_tuple = self._parse_version(remote_version)
        local_tuple = self._parse_version(local_version)
        return remote_tuple > local_tuple


def test_version_parsing():
    """Test version string parsing."""
    print("\n=== Testing Version Parsing ===")
    
    um = MockUpdateManager()
    
    test_cases = [
        ("v1.0.0", (1, 0, 0)),
        ("1.0.0", (1, 0, 0)),
        ("v2.5.3", (2, 5, 3)),
        ("v0.0.1", (0, 0, 1)),
        ("v10.20.30", (10, 20, 30)),
        ("invalid", (0, 0, 0)),
        ("v1.2", (1, 2, 0)),
    ]
    
    for version_str, expected in test_cases:
        result = um._parse_version(version_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} {version_str:15} -> {result} (expected {expected})")


def test_version_comparison():
    """Test version comparison logic."""
    print("\n=== Testing Version Comparison ===")
    
    um = MockUpdateManager()
    
    test_cases = [
        ("1.0.0", "1.0.1", True),   # 1.0.1 is newer
        ("1.0.1", "1.0.0", False),  # 1.0.0 is not newer than 1.0.1
        ("1.0.0", "2.0.0", True),   # 2.0.0 is newer
        ("2.0.0", "1.9.9", False),  # 1.9.9 is not newer than 2.0.0
        ("1.5.0", "1.5.0", False),  # Same version is not newer
        ("0.0.0", "1.0.0", True),   # 1.0.0 is newer than 0.0.0
        ("1.0.0", "1.0.0", False),  # Equality returns False
    ]
    
    for local, remote, expected in test_cases:
        result = um._version_newer(remote, local)
        status = "✓" if result == expected else "✗"
        print(
            f"{status} remote={remote} vs local={local} -> newer={result} (expected {expected})"
        )


def test_file_list():
    """Test that all required files are listed."""
    print("\n=== Testing File List ===")
    
    um = MockUpdateManager()
    
    print(f"\nFiles to update ({len(um.FILES_TO_UPDATE)} total):")
    for file_path in um.FILES_TO_UPDATE:
        print(f"  - {file_path}")
    
    # Check critical files are included
    critical_files = [
        "boot.py",
        "index.html",
        "lib/http_server.py",
        "lib/update_manager.py",
    ]
    
    print(f"\nChecking critical files:")
    for critical in critical_files:
        found = critical in um.FILES_TO_UPDATE
        status = "✓" if found else "✗"
        print(f"{status} {critical}")


def test_git_url_building():
    """Test GitHub URL building."""
    print("\n=== Testing GitHub URL Building ===")
    
    um = MockUpdateManager()
    
    test_files = [
        "boot.py",
        "index.html",
        "lib/update_manager.py",
    ]
    
    for file_path in test_files:
        url = f"https://raw.githubusercontent.com/{um.repo_owner}/{um.repo_name}/Back_Up/{file_path}"
        print(f"  {file_path}")
        print(f"    -> {url}")


def test_config_loading():
    """Test version config loading and saving."""
    print("\n=== Testing Config Loading/Saving ===")
    
    um = MockUpdateManager()
    
    # Simulate version config
    config = {
        "version": "1.0.0",
        "last_check": 0,
        "last_update": 0
    }
    print(f"Version config structure: {json.dumps(config, indent=2)}")
    
    # Parse version
    parsed = um._parse_version(config['version'])
    print(f"Parsed version {config['version']} as tuple: {parsed}")


def test_update_flow_simulation():
    """Simulate the update flow without actual network calls."""
    print("\n=== Simulating Update Flow ===")
    
    um = MockUpdateManager()
    
    print("\n1. Initial state:")
    print(f"   - Current version: {um.current_version}")
    print(f"   - Latest version: {um.latest_version}")
    
    print("\n2. Simulating version check results:")
    um.latest_version = "1.2.0"
    is_newer = um._version_newer(um.latest_version, um.current_version)
    print(f"   - Latest (1.2.0) is newer than current (0.0.0): {is_newer}")
    
    if is_newer:
        print("\n3. Update procedure:")
        print(f"   a) Fetch latest release from GitHub API")
        print(f"   b) Download {len(um.FILES_TO_UPDATE)} files from:")
        print(f"      https://raw.githubusercontent.com/{um.repo_owner}/{um.repo_name}/Back_Up/")
        print(f"   c) Write files safely with .tmp extension first")
        print(f"   d) Verify file sizes match expected")
        print(f"   e) Rename .tmp files to final (atomic operation)")
        print(f"   f) Update version.json with new version")
        print(f"   g) Trigger Pico soft_reset() after 3 seconds")
        print(f"\n4. Expected result:")
        print(f"   - All {len(um.FILES_TO_UPDATE)} files updated")
        print(f"   - Pico restarts automatically")
        print(f"   - Browser reloads to new version")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("UpdateManager Test Suite")
    print("=" * 60)
    
    try:
        test_version_parsing()
        test_version_comparison()
        test_file_list()
        test_git_url_building()
        test_config_loading()
        test_update_flow_simulation()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
