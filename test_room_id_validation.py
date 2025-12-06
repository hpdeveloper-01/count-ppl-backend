#!/usr/bin/env python3
"""
Test room_id validation with unified pattern.
Verifies that both server and backend use consistent validation.
"""

import re
import os
import sys

# Add paths
sys.path.insert(0, '/workspaces/count-ppl-backend')

# Set dummy environment variables before importing configs
os.environ.setdefault('INGESTION_API_KEY', 'test_key_for_validation')
os.environ.setdefault('SUPABASE_URL', 'https://test.supabase.co')
os.environ.setdefault('SUPABASE_SERVICE_KEY', 'test_service_key')

from server.config import ROOM_ID_PATTERN as SERVER_PATTERN
from backend.config import VALID_ROOM_ID_PATTERN as BACKEND_PATTERN

def test_patterns_match():
    """Verify both patterns are identical."""
    print("=" * 60)
    print("PATTERN VALIDATION TEST")
    print("=" * 60)
    
    print(f"\nServer pattern:  {SERVER_PATTERN}")
    print(f"Backend pattern: {BACKEND_PATTERN}")
    
    if SERVER_PATTERN == BACKEND_PATTERN:
        print("✅ PASS: Patterns are identical")
        return True
    else:
        print("❌ FAIL: Patterns differ!")
        return False

def validate_room_id(room_id, pattern):
    """Test if room_id matches pattern."""
    return bool(re.match(pattern, room_id))

def test_valid_room_ids():
    """Test room IDs that should be valid."""
    print("\n" + "=" * 60)
    print("VALID ROOM IDs TEST")
    print("=" * 60)
    
    valid_ids = [
        "room-101",
        "room_101",
        "ROOM101",
        "room101",
        "R",
        "1",
        "-",
        "_",
        "conference-room-A",
        "Lab_2B",
        "Office-1-North",
        "A" * 64,  # Max length (64 chars)
        "test_room-with-mix_123-456",
    ]
    
    all_pass = True
    for room_id in valid_ids:
        server_valid = validate_room_id(room_id, SERVER_PATTERN)
        backend_valid = validate_room_id(room_id, BACKEND_PATTERN)
        
        if server_valid and backend_valid:
            print(f"✅ '{room_id}' - VALID")
        else:
            print(f"❌ '{room_id}' - INVALID (server: {server_valid}, backend: {backend_valid})")
            all_pass = False
    
    return all_pass

def test_invalid_room_ids():
    """Test room IDs that should be invalid."""
    print("\n" + "=" * 60)
    print("INVALID ROOM IDs TEST")
    print("=" * 60)
    
    invalid_ids = [
        "",  # Empty
        " ",  # Whitespace
        "room@101",  # Special char @
        "room#101",  # Special char #
        "room$101",  # Special char $
        "room%101",  # Special char %
        "room&101",  # Special char &
        "room*101",  # Special char *
        "room(101)",  # Parentheses
        "room[101]",  # Brackets
        "room.101",  # Dot
        "room/101",  # Slash
        "room 101",  # Space
        "A" * 65,  # Too long (65 chars, max is 64)
        "A" * 100,  # Way too long
    ]
    
    all_pass = True
    for room_id in invalid_ids:
        server_valid = validate_room_id(room_id, SERVER_PATTERN)
        backend_valid = validate_room_id(room_id, BACKEND_PATTERN)
        
        if not server_valid and not backend_valid:
            print(f"✅ '{room_id}' - Correctly rejected")
        else:
            print(f"❌ '{room_id}' - Incorrectly accepted (server: {server_valid}, backend: {backend_valid})")
            all_pass = False
    
    return all_pass

def test_esp_camera_examples():
    """Test typical ESP camera room IDs."""
    print("\n" + "=" * 60)
    print("ESP CAMERA EXAMPLES TEST")
    print("=" * 60)
    
    esp_ids = [
        "cam-01",
        "camera_front_door",
        "building-A-floor-3",
        "office-conference-room",
        "lobby-main",
        "entrance_north",
        "cam_0001",
        "entrance-01-hd",
    ]
    
    all_pass = True
    for room_id in esp_ids:
        server_valid = validate_room_id(room_id, SERVER_PATTERN)
        backend_valid = validate_room_id(room_id, BACKEND_PATTERN)
        
        if server_valid and backend_valid:
            print(f"✅ '{room_id}' - VALID")
        else:
            print(f"❌ '{room_id}' - INVALID")
            all_pass = False
    
    return all_pass

def main():
    """Run all tests."""
    results = []
    
    # Test 1: Patterns match
    results.append(("Pattern Match", test_patterns_match()))
    
    # Test 2: Valid IDs
    results.append(("Valid Room IDs", test_valid_room_ids()))
    
    # Test 3: Invalid IDs
    results.append(("Invalid Room IDs", test_invalid_room_ids()))
    
    # Test 4: ESP Camera examples
    results.append(("ESP Camera Examples", test_esp_camera_examples()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} test groups passed")
    print("=" * 60)
    
    return all(result for _, result in results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
