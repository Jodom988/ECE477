from picamera import PiCamera

def main():
	cam = PiCamera()
	cam.resolution = (1064, 768)
	cam.start_preview()

	sleep(2)
	cam.capture("~/Desktop/tmp.jp")

if __name__ == '__main__':
	main()