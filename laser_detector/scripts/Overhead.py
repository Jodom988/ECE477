import argparse
import sys

REQ_PORT = 8989

def main():
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)

	group.add_argument('-g', '--generate_frames', action="store_true", help="Only call the program with this argument from the command line. With this option, the program will start the camera and listen for frame requests.")
	group.add_argument('-c', '--consume_frames', action="store", nargs=1, help="Never call the program with this argument from the command line. With this option, the program will request frames and process them.")
	print(sys.argv)
	parsed_args = parser.parse_args(sys.argv[1:])

if __name__ == '__main__':
	main()