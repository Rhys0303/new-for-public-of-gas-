import time
import cv2
import requests
from camera import KitchenCamera

print("[VISION SENDER] Waking up camera...")
cam = KitchenCamera()
SERVER_URL = 'http://localhost:5000/upload'

try:
    while True:
        success, frame = cam.get_frame()
        if success:
            ret, img_encoded = cv2.imencode('.jpg', frame)
            if ret:
                try:
                    requests.post(SERVER_URL, files={'image': img_encoded.tobytes()}, timeout=2)
                    print("[+] Frame sent to Docker")
                except requests.exceptions.RequestException:
                    print("[-] Docker AI is not responding.")
        
        # Take a picture every 2 seconds
        time.sleep(2)

except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    cam.release()