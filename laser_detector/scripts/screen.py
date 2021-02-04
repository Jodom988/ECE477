from matplotlib.patches import Polygon
from utility import *

class screen:

	RES_16_9 = 1
	RES_4_3 = 2
	RES_1_1 = 3 # Testing only

	def __init__(self, points):
		good_dims = True
		if len(points) == 4:
			for pt in points:
				if not len(pt) == 2:
					good_dims = False
					break
		else:
			good_dims = False

		if not good_dims:
			print("Need 4 2-dimensional points to define screen")
			print("Format for screen points should be [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]")
			print("Given: ", end='')
			print(points)
			raise Exception('Incorrect Point Dimensions')

		self.corners = points

	def get_ne(self):
		return self.corners[2]

	def get_se(self):
		return self.corners[3]

	def get_sw(self):
		return self.corners[0]

	def get_nw(self):
		return self.corners[1]

	def get_poly(self):
		return Polygon(self.corners)

	def get_y_percent(self, pt):
		top_slope = slope(self.corners[1], self.corners[2])
		bottom_slope = slope(self.corners[0], self.corners[3])

		top_y = self.corners[1][1] + (pt[0]-self.corners[1][0])*top_slope
		bottom_y = self.corners[0][1] + (pt[0]-self.corners[0][0])*bottom_slope

		percent = (pt[1] - top_y) / (bottom_y - top_y)

		return percent, [top_y, bottom_y]

	def get_x_percent(self, pt):
		left_slope = 1/slope(self.corners[0], self.corners[1])
		right_slope = 1/slope(self.corners[2], self.corners[3])

		left_x = self.corners[1][0] + (pt[1]-self.corners[1][1])*left_slope
		right_x = self.corners[2][0] + (pt[1]-self.corners[2][1])*right_slope

		percent = (pt[0] - left_x) / (right_x - left_x)

		return percent, [right_x, left_x]