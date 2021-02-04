from matplotlib.patches import Polygon
import numpy as np
import utility

RATIO_16_9 = 1
RATIO_4_3 = 2

class Screen:

	RATIO_16_9 = 1
	RATIO_4_3 = 2

	def __init__(self, points, ratio):


		if ratio == Screen.RATIO_4_3:
			pass
		elif ratio == Screen.RATIO_16_9:
			pass
		else:
			raise Exception('Unrecognized Ratio')

		self.ratio = ratio
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
		curr_step = .5
		percentage = 1
		
		top_left = self.get_nw()
		bottom_left = self.get_sw()

		top_right = self.get_ne()
		bottom_right = self.get_se()

		lines = list()

		for i in range(10):
			# Get the line end points
			left_pt = utility.get_point_between(top_left, bottom_left, percentage)
			right_pt = utility.get_point_between(top_right, bottom_right, percentage)

			lines.append([left_pt, right_pt])

			# Find line between two endpoints
			slope = (right_pt[1]-left_pt[1]) / (right_pt[0]-left_pt[0])

			# Find line value at pt
			line_value = slope*(pt[0] - left_pt[0]) + left_pt[1]
			
			if line_value > pt[1]:
				percentage -= curr_step
			elif line_value < pt[1]:
				percentage += curr_step
			else:
				break

			curr_step /= 2

		return percentage, lines

	def get_x_percent(self, pt):
		curr_step = .5
		percentage = 1
		
		top_left = self.get_nw()
		bottom_left = self.get_sw()
		top_right = self.get_ne()
		bottom_right = self.get_se()

		lines = list()

		for i in range(10):
			# Get the line end points
			top_pt = utility.get_point_between(top_left, top_right, percentage)
			bottom_pt = utility.get_point_between(bottom_left, bottom_right, percentage)

			lines.append([top_pt, bottom_pt])

			# Find line between two endpoints
			slope = (bottom_pt[0]-top_pt[0]) / (bottom_pt[1]-top_pt[1])

			# Find line value at pt
			line_value = slope*(pt[1]-top_pt[1])+top_pt[0]
			
			if line_value > pt[0]:
				percentage -= curr_step
			elif line_value < pt[0]:
				percentage += curr_step
			else:
				break

			curr_step /= 2

		return percentage, lines