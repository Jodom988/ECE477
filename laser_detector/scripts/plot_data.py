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


def main():
	time_rx_frame()
if __name__ == '__main__':
	main()