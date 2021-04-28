#!/home/pi/Repos/ECE477/laser_detector/rel/env/bin/python3

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
import traceback

from picamera import PiCamera, PiCameraCircularIO

from nrf24 import *
import pigpio

from Screen import *

SEEK_SET = 0
MB_SIZE = 1000000

LOCAL_HOST = "127.0.0.1"
BUFFER_SIZE = 4096

USB_ADDR = b'\xAA\x44\x33\x22\x11'
LASER_ADDR = b'\x44\x44\x44\x44\x44'
SELF_ADDR = b'\x99\x88\x77\x66\x55'

NOT_FOUND = 0xFFFFFFFF

class states(Enum):
	SETUP = 0
	LASER_OFF = 1
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
	MOUSE_XY = b'\x05'

	CAL_START = b'\x10'
	CAL_CORNER = b'\x11'
	CMD_LASER_ON = b'\x12'
	CAL_CORNER_RESULT = b'\x13'
	CAL_EXIT = b'\x14'
	CAL_RESULT = b'\x15'

	LASER_ON = b'\x20'
	LASER_OFF = b'\x21'

	GET_BASE_FRAME = b'\x30'
	BASE_FRAME_RES = b'\x31'

def current_time_millis():
	return round(time.time() * 1000)

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

	nrf = NRF24(pi, ce=25, payload_size=5, channel=120, data_rate=RF24_DATA_RATE.RATE_2MBPS, pa_level=RF24_PA.MAX)

	nrf.set_address_bytes(len(LASER_ADDR))
	nrf.set_retransmission(15, 15)

	nrf.open_reading_pipe(RF24_RX_ADDR.P1,SELF_ADDR)
	time.sleep(0.25)

	nrf.show_registers()

	return nrf, pi

def send_nrf(nrf, addr, payload):
	nrf.open_writing_pipe(addr)

	nrf.reset_packages_lost()
	print("Sent RF message, ADDR: " + str(addr) + ", PACKET: " + str(payload))
	nrf.send(payload)

	nrf.reset_reading_pipes()
	nrf.open_reading_pipe(RF24_RX_ADDR.P1,SELF_ADDR)
	nrf._nrf_write_reg(NRF24.CONFIG, 0x0F)

	if not (nrf.get_packages_lost() == 0):
		return 0
	else:
		return 1


def setup_camera(res: int, framerate: int):
	camera = PiCamera()
	camera.resolution = res
	camera.framerate = framerate

	buff = PiCameraCircularIO(camera, size=50 * MB_SIZE)
	time.sleep(0.5)

	#camera.start_preview()
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
	global running
	i = 0
	try:
		while running:
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
				stream.clear()
				latest_frame = stream_bytes[last_read_size:]
			if latest_frame_lock.locked():
				latest_frame_lock.release()

			time.sleep(0.05)

	except KeyboardInterrupt as e:
		print("KeyboardInterrupt, exting gracefully...")
	finally:
		running = False
		if latest_frame_lock.locked():
			latest_frame_lock.release()



def get_latest_frame(stream):
	while True:
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
			stream.clear()
			return stream_bytes[last_read_size:]


async def launch_proc_frame(port):
	cmd = "/home/pi/Repos/ECE477/laser_detector/rel/build/ProcessFrame {}".format(port)
	proc = await asyncio.create_subprocess_shell(cmd,
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.PIPE)

	#stdout, stderr = await proc.communicate()


def is_cal_state(state):
	return (state == states.CAL_1) or (state == states.CAL_2) or (state == states.CAL_3) or (state == states.CAL_4) 

def main():
	state = states.SETUP
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--port', action='store', type=int, default=9595, help="Port to communicate between two processes")
	parser.add_argument('-r', '--resolution', action='store', type=int, nargs=2, default=[640, 480], help="Video dimension")
	parser.add_argument('-f', '--framerate', action='store', type=int, default=15, help="Video framerate")
	
	parsed_args = parser.parse_args(sys.argv[1:])

	# Setup RF module
	print("Starting RF Module...", end="")
	nrf, pi = setup_nrf()
	if not pi.connected:
		print("\n Could not connect to Raspberry Pi GPIO Daemon, exiting...")
		return
	print("Done!")

	global running
	running = True

	# Initialize the screen mapper
	res = parsed_args.resolution
	scrn = Screen([[0,res[1]],[0,0],[res[0],0],[res[0],res[1]]])
	# scrn.set_ne([495,175])
	# scrn.set_nw([147,179])
	# scrn.set_se([519,402])
	# scrn.set_sw([129,400])
	default_scrn = Screen([[0,res[1]],[0,0],[res[0],0],[res[0],res[1]]])

	# Start the camera
	print("Starting camera... ", end="")
	camera, circ_buffer = setup_camera(parsed_args.resolution, parsed_args.framerate)
	print("Done!")

	# Do socket setup 
	print("Starting listen socket at {}:{}... ".format(LOCAL_HOST, parsed_args.port), end="")
	listen_socket = setup_socket(LOCAL_HOST, parsed_args.port)
	print("Done!")

	# Start update latest frame thread
	print("Starting update latest frame thread...", end="")
	global latest_frame
	latest_frame_lock = threading.Lock()
	update_latest_frame_thread = threading.Thread(target=gen_frames, args=[circ_buffer, latest_frame_lock])
	update_latest_frame_thread.start()
	print("Done!")

	# Start process for frame proccessing
	print("Starting frame processing process...")
	asyncio.run(launch_proc_frame(parsed_args.port))
	print("Done!")

	# Listen for process frame process to connect
	print("Awaiting Connection...")
	to_socket, in_addrinfo = listen_socket.accept()
	print("Received Connection!")

	latest_frame_lock.acquire()
	print("Setting base frame...", end="")
	latest_frame = get_latest_frame(circ_buffer)
	frame_len_bytes = len(latest_frame).to_bytes(4, byteorder='little')
	to_socket.send(headers.BASE_FRAME.value + frame_len_bytes + latest_frame)
	print("Done!")
	latest_frame_lock.release()

	print("Entering main loop. Press ctrl+c to exit.")

	times = list()
	start_time = current_time_millis()

	state = states.LASER_OFF

	try:
		while running:
			# Get header from rf
			if nrf.data_ready():
				payload = nrf.get_payload()
				header = payload[0]
				print("Command recieved: 0x%02x" % header)
				header = payload[0].to_bytes(1, 'big')
				print("Current state: {}".format(state))
			else:
				header = None


			if header == rf_headers.GET_BASE_FRAME.value:
				print("Acquiring base frame")
				# Send most recent frame to proc thread
				latest_frame_lock.acquire()
				frame_len_bytes = len(latest_frame).to_bytes(4, byteorder='little')
				to_socket.send(headers.BASE_FRAME.value + frame_len_bytes + latest_frame)
				latest_frame_lock.release()
				print("acquired base frame")

			elif (header == rf_headers.LASER_OFF.value and state == states.LASER_ON):
				print("Setting to state laser off")
				state = states.LASER_OFF
			elif (header == rf_headers.LASER_ON.value and state == states.LASER_OFF) or state == states.LASER_ON:
				print("Setting to state laser on")
				state = states.LASER_ON

				latest_frame_lock.acquire()
				frame_len_bytes = len(latest_frame).to_bytes(4, byteorder='little')
				to_socket.send(headers.PROC_FRAME.value + frame_len_bytes + latest_frame)

				# Wait (use select) until process frame thread returns data
				read_socket, _, _ = select.select([to_socket], list(), list())	# Block process until socket in list has data (blocks until ready)
				read_socket = read_socket[0]
				data = rec_from(read_socket)
				x = int.from_bytes(data[1:5], byteorder='little')
				y = int.from_bytes(data[5:9], byteorder='little')

				latest_frame_lock.release()

				if not (x == NOT_FOUND and y == NOT_FOUND):
					# Map to the screen

					x,y = scrn.get_xy_percent([x,y])
					#print("(%.2f, %.2f)" % (x, y))
					print("After mapping: %.2f, %.2f" % (x, y))

					x = int(x*4096)
					y = int(y*4096)

					if (x >= 0 and x <= 4095 and y >= 0 and y <= 4095):
						# Send data to the usb controller
						payload = rf_headers.MOUSE_XY.value + x.to_bytes(2, byteorder='big') + y.to_bytes(2, byteorder='big')
						send_nrf(nrf, USB_ADDR, payload)
				else:
					print("Not found")
					pass


			elif header == rf_headers.CAL_START.value:
				print("Entering CAL1")
				state = states.CAL_1
			elif header == rf_headers.CAL_CORNER.value and is_cal_state(state):

				# process latest frame for position
				latest_frame_lock.acquire()
				
				frame_len_bytes = len(latest_frame).to_bytes(4, byteorder='little')
				to_socket.send(headers.PROC_FRAME.value + frame_len_bytes + latest_frame)

				# Wait (use select) until process frame thread returns data
				read_socket, _, _ = select.select([to_socket], list(), list())	# Block process until socket in list has data (blocks until ready)
				read_socket = read_socket[0]
				data = rec_from(read_socket)
				x = int.from_bytes(data[1:5], byteorder='big')
				y = int.from_bytes(data[5:9], byteorder='big')

				latest_frame_lock.release()

				print("Updating state, currently: " + state)

				# Update state and screen value
				if (x == NOT_FOUND and y == NOT_FOUND):
					if state == states.CAL_1:
						state = states.CAL_2
						screen.set_nw(default_scrn.get_nw())

					elif state == states.CAL_2:
						state = states.CAL_3
						screen.set_ne(default_scrn.get_ne())

					elif state == states.CAL_3:
						state = states.CAL_4
						screen.set_sw(default_scrn.get_sw())

					elif state == states.CAL_4:
						state = states.LASER_OFF
						screen.set_se(default_scrn.get_se())

				else:
					if state == states.CAL_1:
						state = states.CAL_2
						screen.set_nw([x, y])

					elif state == states.CAL_2:
						state = states.CAL_3
						screen.set_ne([x, y])

					elif state == states.CAL_3:
						state = states.CAL_4
						screen.set_sw([x, y])

					elif state == states.CAL_4:
						state = states.LASER_OFF
						screen.set_se([x, y])

				print("State updated, currently: " + state)

			elif header == rf_headers.CAL_CORNER.value and not is_cal_state(state):
				print("Error! Received RF message to calibrate corner when not in calibration state!")
			elif header == rf_headers.CAL_EXIT.value:
				state = states.LASER_OFF

	except KeyboardInterrupt as e:
		print("\nExiting gracefully...")
	except Exception as e:
		traceback.print_exc()
		print("===================================================")
		print("WARNING: Unexpcted exception, performing cleanup...")
	finally:
		running = False
		if latest_frame_lock.locked():
			latest_frame_lock.release()
		# Do cleanup
		try:
			listen_socket.sendall(headers.EXIT.value)
		except Exception as e:
			print("Unable to send exit code to process frame process")
		
		try:
			#camera.stop_preview()
			camera.close()
		except Exception as e:
			print("Unable to stop camera in shutdown")
		
		try:
			listen_socket.close()
		except Exception as e:
			print("Unable to close socket in shutdown")

		try:
			pi.stop()
		except Exception as e:
			print("Unable to close connection to pigpio daemon")

		update_latest_frame_thread.join()

		# with open("../scripts/data/times_laser_on_all.txt", "w") as f:
		# 	[f.write(str(curr_time) + "\n") for curr_time in times]


if __name__ == '__main__':
	main()