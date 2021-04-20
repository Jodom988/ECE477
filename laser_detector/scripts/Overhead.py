import argparse
import asyncio
import logging
import os
import select
import socket
import sys
import threading
import time

from picamera import PiCamera, PiCameraCircularIO
import cv2 as cv
import numpy as np

from utility import *

SEEK_SET = 0
MB_SIZE = 1000000

REQ_PORT = 8989
LOCAL_HOST = "127.0.0.1"
BUFFER_SIZE = 4096

CODE_EXIT = b'\x00'
CODE_REQ_FRAME = b'\x01'
CODE_POS_DATA = b'\x02'
CODE_FRAME_DATA = b'\x03'

latest_frame_bytes = b''
update_latest_frame_running = False


def rec_from(s):
	# Receive all data from socket
	b = b''
	while True:
		data = s.recv(BUFFER_SIZE)
		b += data
		if not data or len(data) < BUFFER_SIZE:	# We assume the socket will Tx in chunks, if continuous stream is Rx this function will not work
			break
	return b

def consume_frames(req_port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	s.connect((LOCAL_HOST, req_port))

	times = list()
	last_time = current_time_millis()

	time.sleep(1)
	i = 0

	time_fptr = open("data/times_rx_interpret_frame.txt", "w")

	try:
		while True:
			logging.info("requesting frame...")
			s.send(CODE_REQ_FRAME)
			read_socket, _, _ = select.select([s], list(), list())	# Wait until socket in list has data (blocks until ready)
			read_socket = read_socket[0] # only one socket so we know its the first

			data = rec_from(read_socket)
			header = data[0:1]
			logging.info(str(header))
			if header == CODE_EXIT:
				logging.info("Received CODE_EXIT, exiting...")
				break
			elif header == CODE_FRAME_DATA:
				frame_bytes = data
				logging.info("Frame size in bytes: {}".format(len(frame_bytes)));
				img = cv.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv.IMREAD_COLOR)
				logging.info("Received frame %d" % i)
				i+=1
				times.append(current_time_millis() - last_time)
				last_time = current_time_millis()
				time_fptr.write(str(times[-1])+"\n")
				# TODO do frame processing
	except KeyboardInterrupt as e:
		pass
	finally:
		# Do cleanup here
		
		s.close()

def update_latest_frame(stream):
	global latest_frame_bytes
	global update_latest_frame_running

	stream_bytes = b''
	
	update_latest_frame_running = True
	while update_latest_frame_running:

		frames = list()
		read_size = 0
		last_read_size = 0
		for frame in stream.frames:
			frames.append(frame)
			last_read_size = read_size
			read_size += frame.frame_size
		
		if read_size>0 and frames[-1].complete:
			stream.seek(SEEK_SET, whence=0)
			stream_bytes = stream.read(read_size)
			latest_frame_bytes = stream_bytes[last_read_size:]

def get_latest_frame():
	return latest_frame_bytes

def serve_frames():
	global update_latest_frame_running

	# Do camera setup
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 60

	stream = PiCameraCircularIO(camera, size=2.5 * MB_SIZE)
	time.sleep(2)
	camera.start_recording(stream, format='mjpeg', quality=23)

	# Start thread refreshing frame
	update_latest_frame_thread = threading.Thread(target=update_latest_frame, args=[stream])
	update_latest_frame_thread.start()

	# Do socket setup
	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		listen_socket.bind((LOCAL_HOST, REQ_PORT))
	except Exception as e:
		logging.ERROR("Could not bind to {}:{} in Overhead.py:serve_frames".format(LOCAL_HOST, REQ_PORT))
		raise e

	listen_socket.listen(0) #Only allow one at a time, (allow zero in backlog)
	
	asyncio.run(launch_consumer())

	logging.info("Awaiting Connection...")
	to_socket, in_addrinfo = listen_socket.accept()
	logging.info("Received Connection!")

	try:
		running = True
		i = 0
		while running:
			read_socket, _, _ = select.select([to_socket], list(), list())	# Block process until socket in list has data (blocks until ready)
			read_socket = read_socket[0] # only one socket so we know its the first

			msg = rec_from(read_socket)

			if len(msg) > 0:
				header = msg[0:1]		# 0:1 instead of 0 to keep as bytes like object
				if header == CODE_REQ_FRAME:
					# Get latest frame here
					logging.info("Received request for new frame")
					frame_bytes = get_latest_frame()
					to_socket.send(CODE_FRAME_DATA + frame_bytes)
					i += 1
				elif header == CODE_POS_DATA:
					## TODO 
					logging.error("Need to implement rx position data")
			elif len(msg) == 0:

				logging.info("Lost connection to consumer")
				asyncio.run(launch_consumer())

				logging.info("Awaiting Connection...")
				to_socket, in_addrinfo = listen_socket.accept()
				logging.info("Received Connection!")

	except KeyboardInterrupt as e:
		update_latest_frame_running = False
		logging.info("Received KeyboardInterrupt, exiting gracefully...")
		try:
			listen_socket.close()
			to_socket.send(CODE_EXIT)
			to_socket.close()
		except Exception as e:
			# Socket already closed
			pass
		camera.stop_recording()
		update_latest_frame_thread.join()
		logging.info("Success!")
		return

			

async def launch_consumer():
	logging.info("Launching consumer process...")
	cmd = "python3 Overhead.py -c {}".format(REQ_PORT)

	proc = await asyncio.create_subprocess_shell(cmd)
	
	#os.system(cmd)

	# consumer_thread = threading.Thread(target=consume_frames, args=[REQ_PORT])
	# consumer_thread.start()

	logging.info("Launched consumer process")

def main():
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)

	group.add_argument('-g', '--generate_frames', action="store_true", help="Only call the program with this argument from the command line. With this option, the program will start the camera and listen for frame requests.")
	group.add_argument('-c', '--consume_frames', action="store", nargs=1, help="Never call the program with this argument from the command line. With this option, the program will request frames and process them.")
	parsed_args = parser.parse_args(sys.argv[1:])

	if parsed_args.generate_frames:
		logging.basicConfig(filename='producer.log', filemode='w', level=logging.DEBUG)
		logging.info("Created producer log file")
		serve_frames()
	else:
		logging.basicConfig(filename='consumer.log', filemode='w', level=logging.DEBUG)
		logging.info("Created consumer log file")
		req_port = int(parsed_args.consume_frames[0])
		consume_frames(req_port)
		logging.info("Exited")

if __name__ == '__main__':
	main()