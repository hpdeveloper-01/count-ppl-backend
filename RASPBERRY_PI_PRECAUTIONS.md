# Raspberry Pi Python HTTP POST - Precautions & Common Pitfalls

## ⚠️ **Critical Precautions**

### **1. Network & Connectivity Issues**

**Pitfall:** Assuming Raspberry Pi is on same network as server
```
❌ Wrong: Server at 192.168.1.100, RPi tries localhost:8000
✅ Right: Use actual server IP/hostname, test with ping first
```

**Precaution:**
```bash
# Before running script, test connectivity
ping your-server-ip
curl http://your-server-ip:8000/health
```

**Common Issue:** Firewall blocking port 8000
```bash
# Server side: Ensure port is open
sudo ufw allow 8000
# OR check if using iptables
sudo iptables -L | grep 8000
```

---

### **2. API Key Management**

**Pitfall:** Hardcoding API key in script
```python
❌ api_key = "abcdef123456"  # Visible in git, logs, ps output
```

**Precaution:** Use environment variables
```python
✅ api_key = os.environ.get('API_KEY')
```

**Setup:**
```bash
# On RPi, set in ~/.bashrc or systemd service
export API_KEY="abcdef123456"

# Or pass at runtime
API_KEY=abcdef123456 python3 script.py
```

**Never do:**
- Commit API key to git
- Print API key in logs
- Store in config files with wrong permissions
- Use same key for multiple cameras (use different keys)

---

### **3. Room ID Format (Critical)**

**Pitfall:** Invalid room_id format causes persistent failures
```
❌ "living room" (space - invalid)
❌ "cam@01" (@ symbol - invalid)  
❌ "building/A/floor/2" (/ - invalid)
❌ "very-long-room-name-exceeding-64-character-limit-which-is-too-long" (too long)

✅ "living-room"
✅ "cam_01"
✅ "building-A-floor-2"
✅ "office-camera"
```

**Pattern:** `^[A-Za-z0-9_-]{1,64}$`

**Precaution:** Validate room_id before sending
```python
import re
ROOM_ID_PATTERN = r'^[A-Za-z0-9_-]{1,64}$'
assert re.match(ROOM_ID_PATTERN, ROOM_ID), f"Invalid room_id: {ROOM_ID}"
```

---

### **4. Image Capture Timing**

**Pitfall:** Capturing images too fast before camera warms up
```
❌ Immediate capture after opening camera = dark/blurry images
✅ 1-2 second delay after opening camera
```

**Precaution:**
```python
cap = cv2.VideoCapture(0)
time.sleep(2)  # ← Essential for good image quality
ret, frame = cap.read()
```

**Why:** Camera sensor needs time to adjust exposure/focus

---

### **5. Interval & Load Timing**

**Pitfall:** Script sends faster than server can process
```
❌ Interval 1 second (60/min) vs server can do 8/min = queue overflows
✅ Interval 7.5 seconds (8/min) matches server capacity
```

**Precaution:**
```python
# Your server: 8 photos/min requirement
# 1 minute = 60 seconds
# 60 / 8 = 7.5 seconds interval (MINIMUM)

INTERVAL = 7.5  # seconds
# Or safer: 10 seconds (6/min) to have buffer
```

**Monitor:** Check server doesn't accumulate backlog
```bash
# On server, watch for increasing response times
tail -f /tmp/server.log | grep "processing_ms"
```

---

### **6. File Handle Leaks**

**Pitfall:** Not closing files/camera handles properly
```python
❌ cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   # Never closed - resource leak over time

✅ cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   cap.release()  # Always close
```

**Precaution:** Always use context managers
```python
✅ with open(image_path, 'rb') as f:
       response = requests.post(..., files={'file': f})
       # File auto-closes after block
```

**Impact:** If not closed, after 10-20 iterations:
- Camera becomes unavailable
- Memory slowly leaks
- Script hangs or crashes

---

### **7. Disk Space Issues**

**Pitfall:** Disk fills up with temp images
```
❌ Creating new image files without cleanup
   After days: /tmp fills 100%, script fails
```

**Precaution:**
```python
# Reuse same filename to avoid multiple files
IMAGE_PATH = Path("/tmp") / "camera_capture.jpg"  # Overwrite same file

# Or periodically cleanup
import os
if os.path.exists(IMAGE_PATH):
    os.remove(IMAGE_PATH)
```

**Check disk space:**
```bash
# On RPi, monitor disk usage
df -h /tmp

# If getting full, increase interval or reduce image size
```

---

### **8. Timeout Handling**

**Pitfall:** Network issues cause script to hang indefinitely
```python
❌ response = requests.post(...)  # No timeout = hangs forever if network fails
✅ response = requests.post(..., timeout=30)  # Will raise exception after 30s
```

**Precaution:**
```python
try:
    response = requests.post(
        SERVER_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=30  # ← Essential
    )
except requests.exceptions.Timeout:
    print("Server not responding - will retry next cycle")
except requests.exceptions.ConnectionError:
    print("Cannot connect to server - check network")
```

**Why:** Without timeout, hung connection blocks forever, causing memory leak

---

### **9. Camera Not Detected**

**Pitfall:** Script runs but camera never initializes
```python
❌ cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   if ret:  # Silently fails if ret is False
       save_image()
```

**Precaution:**
```python
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera not found at /dev/video0")
    exit(1)

# Set explicit properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ret, frame = cap.read()
if not ret:
    print("ERROR: Cannot read from camera")
    cap.release()
    exit(1)
```

**Debug:** Check what cameras exist
```bash
ls /dev/video*
# Should show /dev/video0, /dev/video1, etc.
```

---

### **10. Server URL Typos**

**Pitfall:** URL typo causes all requests to fail silently
```python
❌ "http://192.168.1.100:8000/api/v1/process-image-bytes"
   vs actual server
   "http://192.168.1.101:8000/..."  # Wrong IP

❌ "http://localhost:8000"  # Localhost doesn't exist on RPi network
```

**Precaution:**
```bash
# Test URL before using in script
curl -X POST http://your-server:8000/api/v1/process-image-bytes \
  -H "X-API-KEY: abcdef123456" \
  -F "room_id=test-room" \
  -F "file=@test.jpg"

# Should return 200 OK
```

---

### **11. Permissions Issues**

**Pitfall:** Script runs as different user with no access to camera
```bash
❌ Script runs as 'root' or different user
   /dev/video0 only readable by 'pi' user

✅ Run as 'pi' user, or add user to video group
```

**Precaution:**
```bash
# Check current user
whoami

# Add user to video group
sudo usermod -a -G video $USER

# Log out and back in for changes to take effect
```

---

### **12. Logging & Debugging**

**Pitfall:** No visibility into what script is doing - problems invisible until disk fills
```python
❌ print("Error")  # Lost in background
✅ logging to file + stdout
```

**Precaution:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/camera.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info(f"Sending {people_count} people detected")
logger.error(f"Connection failed: {e}")
```

**Monitor logs:**
```bash
# Real-time
tail -f /home/pi/camera.log

# Search for errors
grep ERROR /home/pi/camera.log
```

---

### **13. Memory Leaks Over Time**

**Pitfall:** Script works fine for hours, then crashes
```
Common causes:
- Open camera handles never released
- Open file handles never closed
- Uncaught exceptions filling memory
- Responses never read/discarded
```

**Precaution:**
```python
# Always use context managers
with open(image_path, 'rb') as f:
    response = requests.post(...)

# Always release camera
cap.release()

# Always read response content
response = requests.post(...)
data = response.json()  # Must read it

# Monitor with systemd auto-restart
Restart=always
RestartSec=30  # Restart if crashed
```

---

### **14. Timestamp Issues**

**Pitfall:** Timestamp in future causes server rejection
```python
❌ timestamp = datetime.utcnow().isoformat() + 'Z'
   Sends: "2025-12-04T10:30:45.123456Z"
   Server says: "Timestamp is in the future"
```

**Precaution:**
```python
# Use timezone-aware datetime
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).isoformat()

# Or just omit timestamp - server uses current time
# data = {'room_id': ROOM_ID}  # No timestamp key
```

---

### **15. Systemd Service Gotchas**

**Pitfall:** Service works manually but fails when set to auto-start
```
Common issue: Working directory not set, relative paths fail
            Environment variables not inherited
            User permissions different
```

**Precaution:**
```ini
[Service]
# Specify absolute paths, not relative
ExecStart=/usr/bin/python3 /home/pi/camera_uploader.py

# Set working directory
WorkingDirectory=/home/pi

# Set environment variables
Environment="API_KEY=abcdef123456"
Environment="TZ=UTC"

# Run as specific user
User=pi
Group=pi

# Restart on failure
Restart=always
RestartSec=30

# Redirect logs
StandardOutput=journal
StandardError=journal
```

**Debug:**
```bash
# Check if service started
sudo systemctl status camera-uploader

# View logs
sudo journalctl -u camera-uploader -n 50

# Test service file
sudo systemd-analyze verify /etc/systemd/system/camera-uploader.service
```

---

## ✅ **Minimal Safe Script Template**

```python
#!/usr/bin/env python3
import os
import sys
import time
import logging
import requests
import cv2
from pathlib import Path

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config from environment
SERVER_URL = os.environ.get('SERVER_URL', 'http://192.168.1.100:8000/api/v1/process-image-bytes')
API_KEY = os.environ.get('API_KEY')
ROOM_ID = os.environ.get('ROOM_ID', 'camera-01')

if not API_KEY:
    logger.error("API_KEY environment variable not set")
    sys.exit(1)

logger.info(f"Starting for room: {ROOM_ID}")

try:
    while True:
        # Capture
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("Cannot open camera")
            time.sleep(5)
            continue
        
        time.sleep(1)  # Warm up
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logger.error("Cannot read frame")
            time.sleep(5)
            continue
        
        # Save
        img_path = Path("/tmp/capture.jpg")
        cv2.imwrite(str(img_path), frame)
        
        # Send
        try:
            with open(img_path, 'rb') as f:
                response = requests.post(
                    SERVER_URL,
                    headers={'X-API-KEY': API_KEY},
                    files={'file': f},
                    data={'room_id': ROOM_ID},
                    timeout=30
                )
            
            if response.status_code == 200:
                people = response.json().get('people_count', 0)
                logger.info(f"✅ {people} people")
            else:
                logger.error(f"Server error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Send failed: {e}")
        
        # Wait
        time.sleep(7.5)

except KeyboardInterrupt:
    logger.info("Stopped")
```

---

## 🎯 **Pre-Deployment Checklist**

- [ ] Test connectivity: `curl http://server:8000/health`
- [ ] API key set: `echo $API_KEY`
- [ ] Room ID valid: only alphanumeric, `-`, `_`, max 64 chars
- [ ] Camera detected: `ls /dev/video*`
- [ ] Image captures: run script manually, check /tmp/capture.jpg
- [ ] Server receives: check server logs
- [ ] Timeout set: `timeout=30` in requests.post()
- [ ] File handles closed: use `with open()`
- [ ] Camera released: `cap.release()`
- [ ] Logs configured: output to file
- [ ] Interval correct: 7.5s minimum for 8/min requirement
- [ ] Environment variables set properly
- [ ] Systemd service has absolute paths

