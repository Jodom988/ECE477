from picamera import PiCamera, CircularIO, PiCameraCircularIO
import time
import cv2 as cv
from io import BytesIO
import numpy as np

SEEK_SET = 0



def find_last(b, search):
	search_len = len(search)
	for i in range(len(b) - search_len + 1, 0, -1):
		if b[i:i+search_len] == search:
			return i

def detect_in_frame(img):
	cv.imshow("preview", img)
	cv.waitKey(0)
	cv.destroyAllWindows()
	pass

def test_detect_stream():
	pass

def test_recent_frame(res, framerate=20):
	print("Initializing Camera...")
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = framerate

	mb = 1000000
	stream = PiCameraCircularIO(camera, size=(50 * mb))
	time.sleep(2)
	camera.start_recording(stream, format='mjpeg', quality=23)
	print("Done!")

	## Wait some time then get the last frame in buffer
	## ================================== ##

	for i in range(1, 4):
		print("Timer: %d" % i)
		time.sleep(.1)

	frames = list()
	read_size = 0
	last_read_size = 0
	for frame in stream.frames:
		frames.append(frame)
		last_read_size = read_size
		read_size += frame.frame_size


	stream.seek(SEEK_SET, whence=0)
	stream_bytes = stream.read(read_size)

	frame_bytes = stream_bytes[last_read_size:]

	i = cv.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv.IMREAD_COLOR)
	cv.imwrite("imgs/buffer_read-1.jpg", i)

	## Wait some time then get the last frame in buffer
	## ================================== ##
	for i in range(1, 4):
		print("Timer: %d" % i)
		time.sleep(1)

	frames = list()
	read_size = 0
	last_read_size = 0
	for frame in stream.frames:
		frames.append(frame)
		last_read_size = read_size
		read_size += frame.frame_size

	stream.seek(SEEK_SET, whence=0)
	stream_bytes = stream.read(read_size)

	frame_bytes = stream_bytes[last_read_size:]

	i = cv.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), 0)
	cv.imwrite("imgs/buffer_read-2.jpg", i)

	camera.stop_recording()

def test_recent_frame_manual(res, framerate=20):
	print("Initializing Camera...")
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = framerate

	mb = 1000000
	stream = CircularIO(50 * mb)
	time.sleep(2)
	camera.start_recording(stream, format='mjpeg', quality=23)
	print("Done!") 

	for i in range(1, 3):
		print(i)
		time.sleep(1)

	camera.stop_recording()
	stream_bytes = b''

	stream.seek(SEEK_SET, whence=0)
	stream_bytes = stream.readall()
	print("Length read: %.2f" % (len(stream_bytes) / mb))
	
	a = None
	b = None

	search = b'\xff\xd9'
	search_len = len(search)
	for i in range(len(stream_bytes) - search_len, 0, -1):
		if stream_bytes[i:i+search_len] == search:
			b = i
			break
	
	search = b'\xff\xd8'
	search_len = len(search)
	for i in range(len(stream_bytes) - search_len, 0, -1):
		if stream_bytes[i:i+search_len] == search:
			if i > b:
				continue
			else:
				a = i
				break

	print((a, b))

	if a != None and b != None:
		jpg = stream_bytes[a:b+2]
		i = cv.imdecode(np.fromstring(jpg, dtype=np.uint8), 0)
		cv.imwrite("imgs/buffer_read.jpg", i)
	else:
		print("No frame found")
		with open("imgs/tmp.mjpg", 'wb') as f:
			f.write(stream_bytes)

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

	os.system("rm {}".format(tmp_fname))

def infinte_preview(res=(640, 480), framerate=30):
	camera = PiCamera()
	camera.resolution = res
	camera.framerate = framerate
	camera.start_preview()

	print("Press ctrl+c to stop preview")

	try:
		time.sleep(1000000)
	except KeyboardInterrupt:
		camera.stop_preview()
		print("\n")

def take_picture(fname, res):
	cam = PiCamera()
	cam.resolution = res
	cam.start_preview()
	time.sleep(2)
	cam.capture(fname)

def main():
	#take_picture("./imgs/test-detect.jpg", (640, 480))
	#get_video("./imgs/test-detect.mjpeg", (640, 480))
	#test_recent_frame((640, 480))
	#infinte_preview()

	img = cv.imread("./imgs/test-detect.jpg")
	detect_in_frame(img)

if __name__ == '__main__':
	main()