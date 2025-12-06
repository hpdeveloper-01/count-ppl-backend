# ESP Camera HTTP POST Configuration Guide

## 🔧 Room ID Format Requirements (FIXED & UNIFIED)

### ✅ Valid Format
- **Pattern**: `^[A-Za-z0-9_-]{1,64}$`
- **Length**: 1-64 characters
- **Allowed Characters**:
  - Letters: A-Z, a-z
  - Numbers: 0-9
  - Hyphens: `-`
  - Underscores: `_`

### ❌ Invalid Format (Will Be Rejected)
- Empty string
- Whitespace or spaces
- Special characters: `@`, `#`, `$`, `%`, `&`, `*`, `(`, `)`, `[`, `]`, `.`, `/`, etc.
- Strings longer than 64 characters
- Strings starting/ending with special chars

---

## 📱 Example ESP Camera Configurations

### ✅ Good Room IDs
```
cam-01
camera_01
FRONT_DOOR_CAMERA
lobby-main-entrance
building_A_floor_3
office-conference-room
entrance_01_hd
lab_2b
conf-room-north-wall
```

### ❌ Bad Room IDs (Will Fail)
```
cam@01              ❌ @ is not allowed
camera.01           ❌ . is not allowed
building/A/floor/3  ❌ / is not allowed
office (main)       ❌ ( ) and spaces not allowed
room#101            ❌ # is not allowed
very_long_room_name_that_exceeds_sixty_four_characters_maximum_limit
                    ❌ Too long (> 64 chars)
```

---

## 🚀 HTTP POST Request Format

### Endpoint: `/api/v1/process-image` (JSON)
```bash
curl -X POST http://your-server:8000/api/v1/process-image \
  -H "X-API-KEY: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "cam-01",
    "image": "base64_encoded_image_string_here...",
    "timestamp": "2025-12-02T10:30:45Z"
  }'
```

### Endpoint: `/api/v1/process-image-bytes` (Multipart/Form-Data)
```bash
curl -X POST http://your-server:8000/api/v1/process-image-bytes \
  -H "X-API-KEY: your_api_key_here" \
  -F "room_id=cam-01" \
  -F "file=@image.jpg" \
  -F "timestamp=2025-12-02T10:30:45Z"
```

---

## ✅ Response Examples

### Success Response (200 OK)
```json
{
  "status": "ok",
  "room_id": "cam-01",
  "people_count": 5,
  "processing_ms": 1234,
  "timestamp": "2025-12-02T10:30:45Z"
}
```

### Invalid room_id Response (400 Bad Request)
```json
{
  "error": "Invalid room_id",
  "message": "room_id must match pattern: ^[A-Za-z0-9_-]{1,64}$"
}
```

---

## 🔍 Troubleshooting

### Error: "Invalid room_id"
**Cause**: room_id contains forbidden characters or doesn't match the pattern

**Solution**:
1. Check that room_id only contains: `A-Z`, `a-z`, `0-9`, `-`, `_`
2. Ensure room_id is 1-64 characters long
3. Remove any spaces or special characters
4. Verify the format matches: `^[A-Za-z0-9_-]{1,64}$`

**Examples of fixes**:
```
❌ "office-room-1 (main)" → ✅ "office-room-1-main"
❌ "cam@101" → ✅ "cam-101"
❌ "building/A/floor/3" → ✅ "building-A-floor-3"
❌ "" → ✅ "cam-01"
```

### Error: "Missing API key"
**Solution**: Add header `X-API-KEY: your_api_key_here` to request

### Error: "Image too large"
**Solution**: Image exceeds 10MB limit, compress or reduce image size

---

## 📋 Validation Summary

| Check | Status | Details |
|-------|--------|---------|
| **Pattern Unified** | ✅ FIXED | Server & Backend use identical pattern |
| **Length Validation** | ✅ FIXED | Enforces 1-64 character limit |
| **Special Chars** | ✅ FIXED | Only alphanumeric, hyphens, underscores allowed |
| **ESP Camera Format** | ✅ TESTED | Supports common naming conventions |
| **Double Validation** | ✅ FIXED | Consistent validation throughout pipeline |

---

## 🎯 Quick Reference for ESP Camera Firmware

Set your room_id like this in your ESP camera code:

```cpp
// Example Arduino/ESP32 code
const char* ROOM_ID = "cam-01";  // ✅ Valid format

// Make POST request
WiFiClient client;
HTTPClient http;
http.begin(client, "http://your-server:8000/api/v1/process-image-bytes");
http.addHeader("X-API-KEY", "your_api_key_here");

// Attach room_id in multipart form
http.addHeader("Content-Type", "multipart/form-data; boundary=----Boundary");
// Add room_id and image file...
http.POST(payload);
```

---

**Last Updated**: December 2, 2025  
**Status**: ✅ Fully Fixed & Tested
