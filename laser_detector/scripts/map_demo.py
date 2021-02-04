import matplotlib.pyplot as plt

from matplotlib.patches import Polygon
from screen import *
from utility import *

def get_point_between(p1, p2, percent):
	new_x = (p1[0] * (1-percent)) + (p2[0] * percent)
	new_y = (p1[1] * (1-percent)) + (p2[1] * percent)

	return [new_x, new_y]

def main():

	points = [[6, 88],
				[5, 8],
				[90, 3],
				[95, 95]]

	scrn = screen(points)

	laser_pt = [50, 50]

	x_percent, [x_right_map, x_left_map] = scrn.get_x_percent(laser_pt)
	y_percent, [y_top_map, y_bottom_map] = scrn.get_y_percent(laser_pt)

	points_x = [laser_pt[0], laser_pt[0], laser_pt[0], x_right_map, x_left_map]
	points_y = [laser_pt[1], y_top_map, y_bottom_map, laser_pt[1], laser_pt[1]]

	x_line = [[x_right_map, x_left_map],
				[laser_pt[1], laser_pt[1]]]

	y_line = [[laser_pt[0], laser_pt[0]],
				[y_top_map, y_bottom_map]]

	temp_pt1 = get_point_between(scrn.get_nw(), scrn.get_sw(), y_percent)
	temp_pt2 = get_point_between(scrn.get_ne(), scrn.get_se(), y_percent)

	x_line_parallax = [[temp_pt1[0], temp_pt2[0]],
						[temp_pt1[1], temp_pt2[1]]]

	temp_pt1 = get_point_between(scrn.get_nw(), scrn.get_ne(), x_percent)
	temp_pt2 = get_point_between(scrn.get_sw(), scrn.get_se(), x_percent)

	y_line_parallax = [[temp_pt1[0], temp_pt2[0]],
						[temp_pt1[1], temp_pt2[1]]]


	fig, ax = plt.subplots()

	ax.invert_yaxis()

	scrn_poly = scrn.get_poly()
	scrn_poly.set_ec((1, 0, 0))
	scrn_poly.set_fc((0, 0, 0, 0))
	ax.add_patch(scrn_poly)

	ax.plot(x_line[0], x_line[1], 'bo:')
	ax.plot(y_line[0], y_line[1], 'bo:')
	# ax.plot(x_line_parallax[0], x_line_parallax[1], 'go:')
	# ax.plot(y_line_parallax[0], y_line_parallax[1], 'go:')

	ax.plot(laser_pt[0], laser_pt[1], 'ro')

	plt.xticks([])
	plt.yticks([])
	plt.show()


	plt.plot()

if __name__ == '__main__':
	main()
