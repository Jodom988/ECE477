import argparse
import asyncio
import logging
import os
import select
import socket
import sys
import threading
import time
from enum import Enum

from picamera import PiCamera, PiCameraCircularIO

from nrf24 import *
import pigpio

from Screen import *

SEEK_SET = 0
MB_SIZE = 1000000

LOCAL_HOST = "127.0.0.1"
BUFFER_SIZE = 4096

LASER_ADDR = b'\xAA\x44\x33\x22\x11'
USB_ADDR = b'\x00\x00\x00\x00\x00'

class states(Enum):
	SETUP = 0
	LASER_OFF = 1
	GET_BASE_FRAME = 2
	LASER_ON = 3
	CAL_1 = 4
	CAL_2 = 5
	CAL_3 = 6
	CAL_4 = 7

class headers(Enum):
	EXIT = b'\x95'
	PROC_FRAME = b'\x96'
	XY_DATA = b'\x97'
	BASE_FRAME = b'\x98'

class rf_headers(Enum):
	MOUSE_XY = b'\x00'

	CAL_START = b'\x00'
	CAL_CORNER = b'\x00'
	CMD_LASER_OFF = b'\x00'
	CAL_RESULT = b'\x00'
	CAL_EXIT = b'\x00'

	LASER_ON = b'\x00'
	LASER_OFF = b'\x00'

	GET_BASE_FRAME = b'\x00'
	BASE_FRAME_RES = b'\x00'

def rec_from(s):
	# Receive all data from socket
	b = b''
	while True:
		data = s.recv(BUFFER_SIZE)
		b += data
		if not data or len(data) < BUFFER_SIZE:	# We assume the socket will Tx in chunks, if continuous stream is Rx this function will not work
			break
	return b

def setup_nrf():
	pi = pigpio.pi("127.0.0.1", 8888)

	if not pi.connected:
		return None, pi

	nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=52, data_rate=RF24_DATA_RATE.RATE_2MBPS, pa_level=RF24_PA.MAX)
	nrf.set_address_bytes(5)
	nrf.set_retransmission(15, 15)

	nrf.open_writing_pipe(LASER_ADDR)
	time.sleep(0.5)
	nrf.open_writing_pipe(USB_ADDR)
	time.sleep(0.5)

	nrf._nrf_write_reg(NRF24.DYNPD, 0x3F)
	nrf._nrf_write_reg(NRF24.FEATURE, 0x6)

	return nrf, pi

def send_nrf(nrf, addr, payload):
	nrf._nrf_write_reg(NRF24.TX_ADDR, addr)
	nrf.send(payload)


def setup_camera(res: int, framerate: int):
	camera = PiCamera()
	camera.resolution = res
	camera.framerate = framerate

	buff = PiCameraCircularIO(camera, size=2.5 * MB_SIZE)
	time.sleep(0.5)

	camera.start_recording(buff, format='mjpeg', quality=23)

	return camera, buff

def setup_socket(host, port):
	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		listen_socket.bind((host, port))
	except Exception as e:
		logging.ERROR("Could not bind to {}:{} in Overhead.py:serve_frames".format(LOCAL_HOST, REQ_PORT))
		raise e

	listen_socket.listen(0) #Only allow one at a time, (allow zero in backlog)

	return listen_socket

def gen_frames(stream, latest_frame_lock):
	global latest_frame
	global gen_frames_running
	
	while gen_frames_running:
		frames = list()
		read_size = 0
		last_read_size = 0
		latest_frame_lock.acquire()
		for frame in stream.frames:
			frames.append(frame)
			last_read_size = read_size
			read_size += frame.frame_size
		
		if read_size>0 and frames[-1].complete:
			stream.seek(SEEK_SET, whence=0)
			stream_bytes = stream.read(read_size)

			latest_frame_bytes = stream_bytes[last_read_size:]
		latest_frame_lock.release()

async def launch_proc_frame(port):
	cmd = "./ProcessFrame {}".format(port)

	proc = await asyncio.create_subprocess_shell(cmd)
	
	#os.system(cmd)

	# consumer_thread = threading.Thread(target=consume_frames, args=[REQ_PORT])
	# consumer_thread.start()

def main():
	state = states.SETUP
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--port', action='store', type=int, default=9595, help="Port to communicate between two processes")
	parser.add_argument('-r', '--resolution', action='store', type=int, nargs=2, default=(640, 480), help="Video dimension")
	parser.add_argument('-f', '--framerate', action='store', type=int, default=15, help="Video framerate")
	
	parsed_args = parser.parse_args(sys.argv[1:])

	# Setup RF module
	print("Starting RF Module...", end="")
	nrf, pi = setup_nrf()
	if not pi.connected:
		print("\n Could not connect to Raspberry Pi GPIO Daemon, exiting...")
		return
	print("Done!")

	# Initialize the screen
	screen = Screen([[0,0],[0,0],[0,0],[0,0]])

	# Start the camera
	print("Starting camera... ", end="")
	camera, circ_buffer = setup_camera(parsed_args.resolution, parsed_args.framerate)
	print("Done!")

	# Start the thread to read from buffer
	print("Starting generate frame thread... ", end="")
	global latest_frame
	global gen_frames_running
	gen_frames_running = True
	latest_frame = b''

	latest_frame_lock = threading.Lock()
	gen_frames_thread = threading.Thread(target=gen_frames, args=[circ_buffer, latest_frame_lock])
	gen_frames_thread.start()
	print("Done!")

	# Do socket setup 
	print("Starting listen socket at {}:{}... ".format(LOCAL_HOST, parsed_args.port), end="")
	listen_socket = setup_socket(LOCAL_HOST, parsed_args.port)
	print("Done!")

	# Start process for frame proccessing
	print("Starting frame processing process...", end="")
	# asyncio.run(launch_proc_frame(parsed_args.port))
	print("Done!")

	# Listen for process frame process to connect
	print("Awaiting Connection...")
	to_socket, in_addrinfo = listen_socket.accept()
	print("Received Connection!")

	try:
		while True:
			# Get header from rf
			header = None
			header = rf_headers.GET_BASE_FRAME

			if header == rf_headers.GET_BASE_FRAME:
				state = states.GET_BASE_FRAME
				# Send most recent frame to proc thread
				latest_frame_lock.acquire()
				frame_len_bytes = len(latest_frame).to_bytes(4, byteorder='big')
				print(len(latest_frame))
				print(frame_len_bytes)
				print("=================")
				s.send(headers.BASE_FRAME + frame_len_bytes + latest_frame)
				latest_frame_lock.release()

				# Send base frame result to laser pointer
				payload = rf_headers.BASE_FRAME_RES + b'\x01'
				send_nrf(nrf, LASER_ADDR, payload)

				pass
			elif header == rf_headers.LASER_ON or state == states.LASER_ON:
				state = states.LASER_ON
				
				latest_frame_lock.acquire()				
				
				# Send most recent frame to processing thread
				to_socket.send(headers.PROC_FRAME + latest_frame)

				# Wait (use select) until process frame thread returns data
				read_socket, _, _ = select.select([to_socket], list(), list())	# Block process until socket in list has data (blocks until ready)
				read_socket = read_socket[0]
				data = rec_from(read_socket)
				x = int(data[1:5])
				y = int(data[5:9])

				# Release lock for most recent frame
				latest_frame_lock.release()

				# Map to the screen
				x,y = get_xy_percent([x,y])

				x /= 4096
				y /= 4096

				# Send data to the usb controller
				payload = MOUSE_XY + x.to_bytes(2) + y.to_bytes(2)
				send_nrf(nrf, USB_ADDR, payload)






	except KeyboardInterrupt as e:
		print("Exiting gracefully...")
	except Exception as e:
		print("WARNING: Unexpcted exception, performating cleanup...")
		print(e)
	finally:
		# Do cleanup
		listen_socket.send(b'\x95')
		gen_frames_running = False
		gen_frames_thread.join()
		camera.stop_recording()
		listen_socket.close()
		pi.stop()


if __name__ == '__main__':
	main()