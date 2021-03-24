from picamera import PiCamera
import time
import cv2 as cv
from io import BytesIO


def test_recent_frame(res, framerate=30):
	print("Initializing Camera...")
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 20
	camera.start_preview()

	stream = BytesIO()
	time.sleep(2)
	camera.start_recording(stream, format='mjpeg', quality=23)
	print("Done!")

	for i in range(1, 2):
		print(i)
		time.sleep(1)

	camera.stop_recording()
	img_bytes = b''
	while True:
		read = stream.read(1024)
		img_bytes += read
		a = img_bytes.find(b'\xff\xd8')
		b = img_bytes.find(b'\xff\xd9')
		if a != -1 and b != -1:
			jpg = img_bytes[a:b+2]
			img_bytes = img_bytes[b+2:]
			i = cv.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
			cv.imwrite("imgs/buffer_read.jpg")
		elif len(read) == 0:
			print("No frame found")
			return
		


def get_video(fname, res, framerate=30, durration=5.0):

	f_ext = fname.split(".")[-1]
	tmp_fname = fname[:-(len(f_ext)+1)] + '-tmp.' + f_ext

	camera = PiCamera()
	camera.resolution = res
	camera.framerate = framerate
	camera.start_recording(tmp_fname)
	print("recording")
	camera.wait_recording(durration)
	print("done")
	camera.stop_recording()

	vid = cv.VideoCapture(tmp_fname)

	fourcc = cv.VideoWriter_fourcc(*'MPEG')
	writer = cv.VideoWriter(fname, fourcc, framerate, res)

	while vid.isOpened():
		ret, frame = vid.read()

		if not ret:
			break

		writer.write(frame)

	writer.release()
	vid.release()

def take_picture(fname, res):
	cam = PiCamera()
	cam.resolution = res
	cam.start_preview()
	time.sleep(2)
	cam.capture(fname)

def main():
	#take_picture("./imgs/tmp.jpg", (1064, 768))
	#get_video("./imgs/tmp.mjpeg", (640, 480))
	test_recent_frame((640, 480))

if __name__ == '__main__':
	main()