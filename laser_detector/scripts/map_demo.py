import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Polygon
from Screen import *



def main():

	points = [[6, 60],
				[18, 5],
				[90, 3],
				[95, 95]]

	points_sq = [[0, 900],
				[0, 0],
				[1600, 0],
				[1600, 900]]

	scrn = Screen(points, Screen.RATIO_16_9)
	scrn_sq = Screen(points_sq, Screen.RATIO_16_9)

	laser_pt = [79, 21]

	x_percent, x_lines = scrn.get_x_percent(laser_pt)
	y_percent, y_lines = scrn.get_y_percent(laser_pt)

	fig, axs = plt.subplots(1, 2, figsize=(10,5))

	ax = axs[0]
	scrn_poly = scrn.get_poly()
	scrn_poly.set_ec((1, 0, 0))
	scrn_poly.set_fc((0, 0, 0, 0))
	ax.add_patch(scrn_poly)

	# for line in x_lines:
	# 	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'g:')

	# for line in y_lines:
	# 	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'g:')

	ax.plot(laser_pt[0], laser_pt[1], 'ro')

	line = y_lines[-1]
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'b:')
	line = x_lines[-1]
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'b:')

	ax.set_xticks([])
	ax.set_yticks([])
	ax.invert_yaxis()

	ax = axs[1]
	scrn_poly = scrn_sq.get_poly()
	scrn_poly.set_ec((1, 0, 0))
	scrn_poly.set_fc((0, 0, 0, 0))
	ax.add_patch(scrn_poly)

	left_pt = utility.get_point_between(scrn_sq.get_nw(), scrn_sq.get_sw(), y_percent)
	top_pt = utility.get_point_between(scrn_sq.get_nw(), scrn_sq.get_ne(), x_percent)
	right_pt = utility.get_point_between(scrn_sq.get_ne(), scrn_sq.get_se(), y_percent)
	bottom_pt = utility.get_point_between(scrn_sq.get_sw(), scrn_sq.get_se(), x_percent)

	new_laser_pt = utility.get_point_between(left_pt, right_pt, x_percent)

	ax.plot(new_laser_pt[0], new_laser_pt[1], 'ro')
	ax.plot([left_pt[0], right_pt[0]], [left_pt[1], right_pt[1]], 'b:')
	ax.plot([top_pt[0], bottom_pt[0]], [top_pt[1], bottom_pt[1]], 'b:')

	ax.set_xticks([])
	ax.set_yticks([])
	ax.set_xlim(-100, 1700)
	ax.set_ylim(-450, 1350)
	ax.invert_yaxis()

	plt.show()

if __name__ == '__main__':
	main()
