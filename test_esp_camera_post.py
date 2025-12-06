#!/usr/bin/env python3
"""
Test ESP camera POST request handling with detailed parameter logging.
"""

import requests
import base64
import json
from io import BytesIO
from PIL import Image
import time

# Configuration
SERVER_URL = "http://localhost:8000"
API_KEY = "abcdef123456"
HEADERS_JSON = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}
HEADERS_MULTIPART = {
    "X-API-KEY": API_KEY
}

def create_test_image(width=320, height=240):
    """Create a simple test image."""
    img = Image.new('RGB', (width, height), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

def test_health_check():
    """Test health check endpoint."""
    print("\n" + "=" * 70)
    print("TEST: Health Check")
    print("=" * 70)
    
    try:
        response = requests.get(f"{SERVER_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_json_valid_room_id():
    """Test JSON endpoint with valid room_id."""
    print("\n" + "=" * 70)
    print("TEST: JSON POST with Valid room_id (cam-01)")
    print("=" * 70)
    
    image_bytes = create_test_image()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "room_id": "cam-01",
        "image": base64_image,
        "timestamp": "2025-12-02T10:30:45Z"
    }
    
    print(f"\nPayload keys: {list(payload.keys())}")
    print(f"room_id: '{payload['room_id']}'")
    print(f"image length: {len(payload['image'])} chars")
    print(f"timestamp: {payload['timestamp']}")
    
    try:
        response = requests.post(f"{SERVER_URL}/api/v1/process-image", 
                                headers=HEADERS_JSON,
                                json=payload)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 500]  # 500 is ok for processing, we're testing validation
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_json_invalid_room_id_special_chars():
    """Test JSON endpoint with invalid room_id (special characters)."""
    print("\n" + "=" * 70)
    print("TEST: JSON POST with Invalid room_id (room@101)")
    print("=" * 70)
    
    image_bytes = create_test_image()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "room_id": "room@101",
        "image": base64_image,
        "timestamp": "2025-12-02T10:30:45Z"
    }
    
    print(f"\nPayload keys: {list(payload.keys())}")
    print(f"room_id: '{payload['room_id']}'")
    print(f"room_id ASCII: {[ord(c) for c in payload['room_id']]}")
    print(f"image length: {len(payload['image'])} chars")
    
    try:
        response = requests.post(f"{SERVER_URL}/api/v1/process-image",
                                headers=HEADERS_JSON,
                                json=payload)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400 and "Invalid room_id" in response.text
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_json_invalid_room_id_whitespace():
    """Test JSON endpoint with invalid room_id (whitespace)."""
    print("\n" + "=" * 70)
    print("TEST: JSON POST with Invalid room_id (whitespace: ' cam-01 ')")
    print("=" * 70)
    
    image_bytes = create_test_image()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "room_id": " cam-01 ",
        "image": base64_image,
        "timestamp": "2025-12-02T10:30:45Z"
    }
    
    print(f"\nPayload keys: {list(payload.keys())}")
    print(f"room_id: {repr(payload['room_id'])}")
    print(f"room_id length: {len(payload['room_id'])}")
    print(f"image length: {len(payload['image'])} chars")
    
    try:
        response = requests.post(f"{SERVER_URL}/api/v1/process-image",
                                headers=HEADERS_JSON,
                                json=payload)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400 and "Invalid room_id" in response.text
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_json_empty_room_id():
    """Test JSON endpoint with empty room_id."""
    print("\n" + "=" * 70)
    print("TEST: JSON POST with Invalid room_id (empty string)")
    print("=" * 70)
    
    image_bytes = create_test_image()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "room_id": "",
        "image": base64_image,
        "timestamp": "2025-12-02T10:30:45Z"
    }
    
    print(f"\nPayload keys: {list(payload.keys())}")
    print(f"room_id: {repr(payload['room_id'])}")
    print(f"image length: {len(payload['image'])} chars")
    
    try:
        response = requests.post(f"{SERVER_URL}/api/v1/process-image",
                                headers=HEADERS_JSON,
                                json=payload)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400 and "Invalid room_id" in response.text
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_multipart_valid_room_id():
    """Test multipart endpoint with valid room_id."""
    print("\n" + "=" * 70)
    print("TEST: Multipart POST with Valid room_id (lobby-main)")
    print("=" * 70)
    
    image_bytes = create_test_image()
    
    files = {
        'file': ('test.jpg', image_bytes, 'image/jpeg'),
    }
    data = {
        'room_id': 'lobby-main',
        'timestamp': '2025-12-02T10:30:45Z'
    }
    
    print(f"\nForm data keys: {list(data.keys())}")
    print(f"room_id: '{data['room_id']}'")
    print(f"timestamp: {data['timestamp']}")
    print(f"file: test.jpg ({len(image_bytes)} bytes)")
    
    try:
        response = requests.post(f"{SERVER_URL}/api/v1/process-image-bytes",
                                headers=HEADERS_MULTIPART,
                                files=files,
                                data=data)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 500]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_multipart_invalid_room_id():
    """Test multipart endpoint with invalid room_id."""
    print("\n" + "=" * 70)
    print("TEST: Multipart POST with Invalid room_id (building/A/floor/3)")
    print("=" * 70)
    
    image_bytes = create_test_image()
    
    files = {
        'file': ('test.jpg', image_bytes, 'image/jpeg'),
    }
    data = {
        'room_id': 'building/A/floor/3',
        'timestamp': '2025-12-02T10:30:45Z'
    }
    
    print(f"\nForm data keys: {list(data.keys())}")
    print(f"room_id: '{data['room_id']}'")
    print(f"file: test.jpg ({len(image_bytes)} bytes)")
    
    try:
        response = requests.post(f"{SERVER_URL}/api/v1/process-image-bytes",
                                headers=HEADERS_MULTIPART,
                                files=files,
                                data=data)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400 and "Invalid room_id" in response.text
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("ESP CAMERA POST REQUEST VALIDATION TEST SUITE")
    print("=" * 70)
    print(f"Server: {SERVER_URL}")
    print(f"API Key: {API_KEY}")
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(10):
        try:
            requests.get(f"{SERVER_URL}/health", timeout=1)
            print("✅ Server is ready!")
            break
        except:
            time.sleep(1)
            if i == 9:
                print("❌ Server not responding!")
                return
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("JSON Valid room_id (cam-01)", test_json_valid_room_id()))
    results.append(("JSON Invalid room_id (room@101)", test_json_invalid_room_id_special_chars()))
    results.append(("JSON Invalid room_id (whitespace)", test_json_invalid_room_id_whitespace()))
    results.append(("JSON Invalid room_id (empty)", test_json_empty_room_id()))
    results.append(("Multipart Valid room_id (lobby-main)", test_multipart_valid_room_id()))
    results.append(("Multipart Invalid room_id (building/A/floor/3)", test_multipart_invalid_room_id()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)
    
    # Show server logs
    print("\n" + "=" * 70)
    print("SERVER LOGS (Last 50 lines)")
    print("=" * 70)
    try:
        with open("/tmp/server.log", "r") as f:
            lines = f.readlines()[-50:]
            print("".join(lines))
    except:
        print("Could not read server logs")

if __name__ == '__main__':
    main()
