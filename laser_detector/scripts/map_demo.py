import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Polygon
from Screen import *

def get_point_between(p1, p2, percent):
	new_x = (p1[0] * (1-percent)) + (p2[0] * percent)
	new_y = (p1[1] * (1-percent)) + (p2[1] * percent)

	return [new_x, new_y]

def main():

	points = [[6, 60],
				[5, 40],
				[90, 3],
				[95, 95]]

	scrn = Screen(points, Screen.RATIO_16_9)

	laser_pt = [50, 50]

	fig, ax = plt.subplots()

	scrn_poly = scrn.get_poly()
	scrn_poly.set_ec((1, 0, 0))
	scrn_poly.set_fc((0, 0, 0, 0))
	ax.add_patch(scrn_poly)

	ax.plot(laser_pt[0], laser_pt[1], 'ro')

	plt.xticks([])
	plt.yticks([])
	ax.invert_yaxis()

	#plt.plot()

if __name__ == '__main__':
	main()
