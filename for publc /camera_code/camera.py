import cv2
from picamera2 import Picamera2

class KitchenCamera:
    def __init__(self):
        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(main={"size": (640, 480)})
        self.picam2.configure(config)
        self.picam2.start()

    def get_frame(self):
        try:
            frame = self.picam2.capture_array("main")
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            return True, frame
        except Exception:
            return False, None

    def release(self):
        self.picam2.stop()
        self.picam2.close()