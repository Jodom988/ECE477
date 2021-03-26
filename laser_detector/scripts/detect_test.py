import cv2 as cv
import numpy as np
from utility import *

from progress.bar import Bar

def insert_sorted(l, elem):
	if len(l) == 0:
		return 0
	if elem <= l[-1]:
		return None
	for i in range(len(l)):
		if elem > l[i]:
			return i
	return None
			
def detect_in_frame(img):
	height, width, ch = img.shape
	
	largest = list()
	positions = list()
	N = 50

	for row_i in range(len(img)):
		for col_i in range(len(img[row_i])):
			val = int(img[row_i][col_i][2])-int(img[row_i][col_i][1])
			if val > 255:
				val = 255
			if val < 0:
				val = 0
			
			i = insert_sorted(largest, val)
			if not i == None:
				largest.insert(i, val)
				positions.insert(i, (row_i, col_i))
				if len(largest) > N:
					largest.pop()
					positions.pop()

	y_avg = round(np.average([pos[0] for pos in positions]))
	x_avg = round(np.average([pos[1] for pos in positions]))

	return (x_avg,y_avg)

def detect_in_video(infile, outfile):
	cap = cv.VideoCapture(infile)

	fourcc = cv.VideoWriter_fourcc(*'XVID')
	width = 640
	height = 480
	out = cv.VideoWriter(outfile, fourcc, 30.0, (width,  height))

	times = list()

	bar = Bar('Processing', max=144)

	while cap.isOpened():
		ret, frame = cap.read()
		# if frame is read correctly ret is True
		if not ret:
			print("Can't receive frame (stream end?). Exiting ...")
			break
		
		pos = detect_in_frame(frame)

		start = current_time_micros()
		cv.line(frame, (0, pos[1]), (width, pos[1]), (0,0,255), 1)
		cv.line(frame, (pos[0], 0), (pos[0], height), (0,0,255), 1)
		ellapsed = current_time_micros() - start

		times.append(ellapsed)

		out.write(frame)


		# cv.imshow('frame', frame)
		# if cv.waitKey(1) == ord('q'):
		# 	break

		#frame

		bar.next()
	bar.finish()

	[print(time) for time in times]

	print(len(times))


def test_detect_in_frame(img):

	height, width, ch = img.shape

	new_img = np.zeros((height,width*ch,ch),np.uint8)

	largest = list()
	positions = list()
	N = 50

	for row_i in range(len(img)):
		for col_i in range(len(img[row_i])):
			new_img[row_i][col_i+(width*2)][2] = img[row_i][col_i][2]
			new_img[row_i][col_i+width][1] = img[row_i][col_i][1]
			val = int(img[row_i][col_i][2])-int(img[row_i][col_i][1])
			if val > 255:
				val = 255
			if val < 0:
				val = 0

			new_img[row_i][col_i][0] = val
			new_img[row_i][col_i][1] = val
			new_img[row_i][col_i][2] = val
			
			i = insert_sorted(largest, val)
			if not i == None:
				largest.insert(i, val)
				positions.insert(i, (row_i, col_i))
				if len(largest) > N:
					largest.pop()
					positions.pop()

	row_avg = round(np.average([pos[0] for pos in positions]))
	col_avg = round(np.average([pos[1] for pos in positions]))

	cv.line(new_img, (0, row_avg), (width, row_avg), (0,0,255), 1)
	cv.line(new_img, (col_avg, 0), (col_avg, height), (0,0,255), 1)

	print((row_avg,col_avg))
	cv.imshow("preview", new_img)
	cv.waitKey(0)
	cv.destroyAllWindows()
	pass


def main():
	try:
		# img = cv.imread("./imgs/test-detect.jpg")
		# test_detect_in_frame(img)
		detect_in_video('imgs/test-detect.mjpeg', 'imgs/test-detected.avi')
	except KeyboardInterrupt:
		pass


if __name__ == '__main__':
	main()