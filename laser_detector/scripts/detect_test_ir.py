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

def diff_frame(img, base_img):
	height, width, ch = img.shape
	new_img = np.zeros((height,width,ch),np.uint8)

	for row_i in range(len(img)):
		for col_i in range(len(img[row_i])):
			val = (int(img[row_i][col_i][1])-int(base_img[row_i][col_i][1]))
			if val > 255:
				val = 255
			elif val < 0:
				val = 0
			new_img[row_i][col_i][0] = val
			new_img[row_i][col_i][1] = val
			new_img[row_i][col_i][2] = val

	return new_img

def detect_in_frame_ir(img, base_img):
	height, width, ch = img.shape

	largest_vals = list()
	positions = list()
	N = 4

	for row_i in range(len(img)):
		for col_i in range(len(img[row_i])):

			val = (int(img[row_i][col_i][1])-int(base_img[row_i][col_i][1]))
			if val > 255:
				val = 255
			elif val < 50:
				continue

			idx = insert_sorted(largest_vals, val)

			if not idx == None:
				largest_vals.insert(idx, val)
				positions.insert(idx, (row_i, col_i))
				if len(largest_vals) > N:
					largest_vals.pop()
					positions.pop()

	if len(positions) < (N // 2):
		return None

	row_avg = round(np.average([pos[0] for pos in positions]))
	col_avg = round(np.average([pos[1] for pos in positions]))

	return (col_avg,row_avg)

def test_detect_in_frame_ir(img, base_img):

	height, width, ch = img.shape


	new_img = np.zeros((height*2,width*3,ch),np.uint8)

	largest_vals = list()
	positions = list()
	N = 4

	for row_i in range(len(img)):
		for col_i in range(len(img[row_i])):
			new_img[row_i+height][col_i+(width*0)][0] = img[row_i][col_i][0]
			new_img[row_i+height][col_i+(width*0)][1] = img[row_i][col_i][0]
			new_img[row_i+height][col_i+(width*0)][2] = img[row_i][col_i][0]

			new_img[row_i+height][col_i+(width*1)][0] = img[row_i][col_i][1]
			new_img[row_i+height][col_i+(width*1)][1] = img[row_i][col_i][1]
			new_img[row_i+height][col_i+(width*1)][2] = img[row_i][col_i][1]
			
			new_img[row_i+height][col_i+(width*2)][0] = img[row_i][col_i][2]
			new_img[row_i+height][col_i+(width*2)][1] = img[row_i][col_i][2]
			new_img[row_i+height][col_i+(width*2)][2] = img[row_i][col_i][2]


			new_img[row_i][col_i+(width*2)][1] = img[row_i][col_i][1]

			val = (int(img[row_i][col_i][1])-int(base_img[row_i][col_i][1]))
			if val > 255:
				print("over")
				val = 255
			elif val < 0:
				val = 0
			new_img[row_i][col_i+(width*1)][0] = val
			new_img[row_i][col_i+(width*1)][1] = val
			new_img[row_i][col_i+(width*1)][2] = val

			new_img[row_i][col_i+(width*0)][0] = img[row_i][col_i][0]
			new_img[row_i][col_i+(width*0)][1] = img[row_i][col_i][1]
			new_img[row_i][col_i+(width*0)][2] = img[row_i][col_i][2]

			idx = insert_sorted(largest_vals, val)

			if not idx == None:
				largest_vals.insert(idx, val)
				positions.insert(idx, (row_i, col_i))
				if len(largest_vals) > N:
					largest_vals.pop()
					positions.pop()


	row_avg = round(np.average([pos[0] for pos in positions]))
	col_avg = round(np.average([pos[1] for pos in positions]))

	cv.line(new_img, (0, row_avg), (width, row_avg), (0,0,255), 1)
	cv.line(new_img, (col_avg, 0), (col_avg, height), (0,0,255), 1)

	print((col_avg,row_avg))
	cv.imshow("preview", new_img)
	cv.waitKey(0)
	cv.destroyAllWindows()


def show_in_video(infile, timesfname, maxframes=0, vidout=None, lines=True):
	frame_count = count_frames(infile)

	if maxframes > 0 and maxframes < frame_count:
		frame_count = maxframes


	cap = cv.VideoCapture(infile)

	if not vidout == None:
		fourcc = cv.VideoWriter_fourcc(*'XVID')
		width = 640
		height = 480
		out = cv.VideoWriter(vidout, fourcc, 30.0, (width,  height))

	time_file = open(timesfname, "w")

	bar = Bar('Processing', max=frame_count)
	count = 0
	base_frame = None
	while cap.isOpened():
		ret, frame = cap.read()
		# if frame is read correctly ret is True
		if not ret:
			#print("Can't receive frame (stream end?). Exiting ...")
			break

		if count == 0:
			base_frame = frame
		
		start = current_time_millis()
		pos = detect_in_frame_ir(frame, base_frame)
		ellapsed = current_time_millis() - start
		time_file.write("{}\n".format(ellapsed))

		# frame = diff_frame(frame, base_frame)

		if not vidout == None:
			if not pos == None and lines:
				cv.line(frame, (0, pos[1]), (width, pos[1]), (0,0,255), 1)
				cv.line(frame, (pos[0], 0), (pos[0], height), (0,0,255), 1)

			out.write(frame)

		if count >= frame_count: break
		count += 1

		bar.next()

	bar.finish()

def main():
	try:
		# base = cv.imread("./imgs/base.jpg", cv.IMREAD_COLOR)
		# img = cv.imread("./imgs/ir-laser-1mw-24ma.jpg", cv.IMREAD_COLOR)
		# test_detect_in_frame_ir(img, base)
		# img = cv.imread("./imgs/test-detect.jpg")
		show_in_video('videos/ir-laser-test-1mw-24ma-2.mjpeg', 'data/times_proc_frame.txt', vidout='videos/detected/diff-lines-n4.avi', lines=True)
	except KeyboardInterrupt:
		pass


if __name__ == '__main__':
	main()