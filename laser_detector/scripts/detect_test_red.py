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

def count_frames(fname):
	# WARNING, Do not call this function if file is already opened.
	cap = cv.VideoCapture(fname)
	count = 0
	while cap.isOpened():
		ret, frame = cap.read()
		if not ret:
			break
		count += 1
	return count


def test_detect_in_frame_red(img):

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
			
def detect_in_frame_red(img):
	height, width, ch = img.shape
	
	largest = list()
	positions = list()
	N = 5

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

def test_time_detect_red(fname, max_frames=0):
	frame_count = count_frames(fname)
	cap = cv.VideoCapture(fname)

	fptr = open("data/times_proc_frame.txt", "w")


	if max_frames > 0 and frame_count > max_frames:
			bar = Bar('Processing', max=max_frames)
	else:
		bar = Bar('Processing', max=frame_count)


	count = 0
	while cap.isOpened():
		ret, frame = cap.read()
		# if frame is read correctly ret is True
		if not ret:
			#print("Can't receive frame (stream end?). Exiting ...")
			break
		
		start = current_time_millis()
		pos = detect_in_frame(frame)
		ellapsed = current_time_millis() - start

		fptr.write("{}\n".format(ellapsed))

		bar.next()
		count += 1
		if max_frames > 0 and count>=max_frames:
			break

	bar.finish()
	fptr.close()

def detect_in_video_red(infile, outfile):
	frame_count = count_frames(infile)
	cap = cv.VideoCapture(infile)

	fourcc = cv.VideoWriter_fourcc(*'XVID')
	width = 640
	height = 480
	out = cv.VideoWriter(outfile, fourcc, 30.0, (width,  height))

	times = list()

	bar = Bar('Processing', max=frame_count)
	count = 0
	while cap.isOpened():
		ret, frame = cap.read()
		# if frame is read correctly ret is True
		if not ret:
			#print("Can't receive frame (stream end?). Exiting ...")
			break
		
		start = current_time_millis()
		pos = detect_in_frame(frame)
		ellapsed = current_time_millis() - start
		times.append(ellapsed)

		cv.line(frame, (0, pos[1]), (width, pos[1]), (0,0,255), 1)
		cv.line(frame, (pos[0], 0), (pos[0], height), (0,0,255), 1)


		out.write(frame)
		if count == 25: break
		count += 1

		# cv.imshow('frame', frame)
		# if cv.waitKey(1) == ord('q'):
		# 	break

		bar.next()
	bar.finish()

	[print(time) for time in times]


def main():
	try:
		base = cv.imread("./imgs/base.jpg", cv.IMREAD_COLOR)
		img = cv.imread("./imgs/ir-laser-1mw-24ma.jpg", cv.IMREAD_COLOR)
		test_detect_in_frame_ir(img, base)
		# img = cv.imread("./imgs/test-detect.jpg")
		# test_detect_in_frame_red(img)
		# detect_in_video('imgs/test-detect.mjpeg', 'imgs/test-detected.avi')
		# test_time_detect('imgs/test-detect.mjpeg', max_frames=3)
	except KeyboardInterrupt:
		pass


if __name__ == '__main__':
	main()