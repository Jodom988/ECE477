import argparse
from picamera import PiCamera
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--resolution', action='store', type=int, nargs=2, default=[640, 480], help="Video dimension")
parser.add_argument('-f', '--framerate', action='store', type=int, default=30, help="Video framerate")

parsed_args = parser.parse_args(sys.argv[1:])

res = parsed_args.resolution
framerate = parsed_args.framerate

camera = PiCamera()
camera.resolution = res
camera.framerate = framerate
camera.start_preview()

print("Press enter to stop preview")
input()
camera.stop_preview()