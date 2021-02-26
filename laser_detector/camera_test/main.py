from picamera import PiCamera

def main():
	cam = PiCameracamera()
	cam.resolution = (1064, 768)
	cam.start_preview()

	sleep(2)
	cam.capture("~/Desktop/tmp.jpg")

if __name__ == '__main__':
	main()