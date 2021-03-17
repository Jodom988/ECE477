from io import BytesIO
from picamera import PiCamera

import time


stream = BytesIO()
camera = PiCamera()

camera.resolution = (640, 480)
camera.start_recording(stream, format='h264', quality=23)

time.sleep(2)


print("Done!")