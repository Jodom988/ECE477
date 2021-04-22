import matplotlib.pyplot as plt
import numpy as np


def time_rx_frame():
	fname = 'data/times_rx_interpret_frame.txt'
	times = list()

	with open(fname, 'r') as f:
		[times.append(int(line)) for line in f.readlines()]

	plt.hist(times)
	plt.xlabel("Time (ms)")
	plt.ylabel("Frequency")
	plt.title("Time to Read Frame from Buffer and\nInterpret as openCV Image Object")
	plt.savefig('plots/time_rx_frame.png')

def time_proc_frame():
	fname = 'data/times_proc_frame_skips.txt'
	times = list()

	with open(fname, 'r') as f:
		[times.append(int(line)) for line in f.readlines()]

	plt.hist(times)
	plt.xlabel("Time (ms)")
	plt.ylabel("Frequency")
	plt.title("Time to Process One Frame")
	plt.savefig('plots/time_proc_frame_skips.png')

def time_laser_on_all():
	fname = 'data/times_laser_on_all.txt'
	times = list()

	with open(fname, 'r') as f:
		[times.append(int(line)) for line in f.readlines()]

	plt.hist(times)
	plt.xlabel("Time (ms)")
	plt.ylabel("Frequency")
	plt.title("Time to Process Frame and Send Update")
	plt.savefig('plots/time_proc_laser_on_all.png')

def main():
	#time_rx_frame()
	#time_proc_frame()
	time_laser_on_all()
if __name__ == '__main__':
	main()