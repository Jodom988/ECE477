import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Polygon
from Screen import *

def plot_full():
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

	laser_pt = [81, 33]

	x_percent, x_lines = scrn.get_x_percent(laser_pt)
	y_percent, y_lines = scrn.get_y_percent(laser_pt)

	fig, axs = plt.subplots(1, 2, figsize=(10,5))

	ax = axs[0]
	scrn_poly = scrn.get_poly()
	scrn_poly.set_ec((1, 0, 0))
	scrn_poly.set_fc((0, 0, 0, 0))
	ax.add_patch(scrn_poly)

	ax.plot(laser_pt[0], laser_pt[1], 'ro')

	line = y_lines[-1]
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'b:')
	line = x_lines[-1]
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'b:')

	ax.set_xticks([])
	ax.set_yticks([])
	ax.invert_yaxis()
	ax.set_title("Picture Taken by Camera")

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

	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)
	ax.axis('off')
	ax.set_xlim(-100, 1700)
	ax.set_ylim(-450, 1350)
	ax.invert_yaxis()
	ax.set_title("Laser Mapped to Screen")

	plt.savefig('imgs/mapping_complete.png')
	plt.show()

def plot_steps():
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

	laser_pt = [81, 33]

	x_percent, x_lines = scrn.get_x_percent(laser_pt)
	y_percent, y_lines = scrn.get_y_percent(laser_pt)

	fig, axs = plt.subplots(1, 3, figsize=(10,5))

	

	### 1st Subplot ###
	ax = axs[0]

	scrn_poly = scrn.get_poly()
	scrn_poly.set_ec((1, 0, 0))
	scrn_poly.set_fc((0, 0, 0, 0))
	ax.add_patch(scrn_poly)

	line = y_lines[0]
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'g:')
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'bo')

	ax.plot(laser_pt[0], laser_pt[1], 'ro')

	ax.set_xticks([])
	ax.set_yticks([])
	ax.invert_yaxis()
	ax.set_title("A")

	### 2nd Subplot ###
	ax = axs[1]

	scrn_poly = scrn.get_poly()
	scrn_poly.set_ec((1, 0, 0))
	scrn_poly.set_fc((0, 0, 0, 0))
	ax.add_patch(scrn_poly)

	line = y_lines[0]
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'g:')
	line = y_lines[1]
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'g:')
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'bo')

	ax.plot(laser_pt[0], laser_pt[1], 'ro')

	ax.set_xticks([])
	ax.set_yticks([])
	ax.invert_yaxis()
	ax.set_title("B")

	### 3rd subplot ###
	ax = axs[2]

	scrn_poly = scrn.get_poly()
	scrn_poly.set_ec((1, 0, 0))
	scrn_poly.set_fc((0, 0, 0, 0))
	ax.add_patch(scrn_poly)

	for i in range(len(y_lines) - 1):
		line = y_lines[i]
		ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'g:')

	aline = y_lines[-1]
	ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'r:')

	ax.plot(laser_pt[0], laser_pt[1], 'ro')

	ax.set_xticks([])
	ax.set_yticks([])
	ax.invert_yaxis()
	ax.set_title("C")
	
	plt.savefig('imgs/steps.png')
	plt.show()

def main():
	plot_full()
	#plot_steps()
	

if __name__ == '__main__':
	main()
