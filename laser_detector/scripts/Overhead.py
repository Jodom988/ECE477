import argparse
import sys
import socket
import asyncio
import select
import threading
import logging

from picamera import PiCamera

from io import BytesIO

REQ_PORT = 8989
LOCAL_HOST = "127.0.0.1"
BUFFER_SIZE = 4096

CODE_EXIT = b'\x00'
CODE_REQ_FRAME = b'\x01'
CODE_POS_DATA = b'\x02'


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

	while True:
		s.send(CODE_REQ_FRAME)
		read_socket, _, _ = select.select([s], list(), list())	# Wait until socket in list has data (blocks until ready)
		read_socket = read_socket[0] # only one socket so we know its the first

		frame = b''
		while True:
			data = rec_from(read_socket)

			if data == CODE_EXIT:
				logging.info("Received CODE_EXIT, exiting...")
				return
			frame += data
			# TODO check to make sure full frame
			if frame:
				break

		# Process Frame Here
		logging.info(frame)




def serve_frames():
	# Do camera setup
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 20

	stream = BytesIO()
	camera.start_recording(stream, format='mjpeg', quality=23)

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
	
	running = True
	while running:
		try:
			
			read_socket, _, _ = select.select([to_socket], list(), list())	# Wait until socket in list has data (blocks until ready)
			read_socket = read_socket[0] # only one socket so we know its the first

			i = 0
			while running:
				msg = rec_from(read_socket)
				if msg == CODE_REQ_FRAME:
					# Get latest frame here
					logging.info("Received request for new frame")
					to_socket.send(str.encode('Frame number {}'.format(i)))
					i += 1
				elif msg == CODE_POS_DATA:
					## TODO 
					logging.error("Need to implement rx position data")
			try:
				logging.info("Consumer program disconnected, relaunching program")
				asyncio.run(launch_consumer())

				logging.info("Awaiting Connection...")
				to_socket, in_addrinfo = listen_socket.accept()
				logging.info("Received Connection!")
			
			except Exception as e:
				logging.ERROR("FATAL ERROR IN MAIN LOOP OF serve_frames()")
				print("FATAL ERROR IN MAIN LOOP OF serve_frames()")

		except KeyboardInterrupt as e:
			
			logging.info("Received KeyboardInterrupt, exiting gracefully...")
			try:
				to_socket.send(CODE_EXIT)
				to_socket.close()
				listen_socket.close()
			except Exception as e:
				# Socket already closed
				pass

			return

		except Exception as e:
			## TODO: Do error handling for full buffer
			logging.error("BUFFER FULL")
			print("Buffer full")
			pass

async def launch_consumer():


	logging.info("Launching consumer program...")
	proc = await asyncio.create_subprocess_shell(
		"python3 Overhead.py -c {}".format(REQ_PORT))
		# stdout=asyncio.subprocess.PIPE,
		# stderr=asyncio.subprocess.PIPE)
	
	# stdout, stderr = await proc.communicate()
	# if stdout:
	# 	print("[stdout]\n{}".format(stdout.decode()))
	# if stderr:
	# 	print("[stderr]\n{}".format(stderr.decode()))
	logging.info("Launched consumer program")

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