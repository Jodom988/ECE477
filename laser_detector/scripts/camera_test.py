from picamera import PiCamera
import time
import cv2 as cv




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
	get_video("./imgs/tmp.mjpeg", (640, 480))

if __name__ == '__main__':
	main()