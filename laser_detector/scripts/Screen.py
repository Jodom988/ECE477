from matplotlib.patches import Polygon
import numpy as np

RATIO_16_9 = 1
RATIO_4_3 = 2

class Screen:

	RATIO_16_9 = 1
	RATIO_4_3 = 2

	# calibration_mat_16_9 = np.array([[0, 0],
	# 							[16, 0],
	# 							[16, 9],
	# 							[0, 9]])

	calibration_mat_16_9 = np.array([[0, 9],
								[0, 0],
								[16, 0],
								[16, 9]])

	calibration_mat_4_3 = np.array([[0, 3],
								[0, 0],
								[4, 0],
								[4, 3]])

	def __init__(self, points, ratio):


		if ratio == Screen.RATIO_4_3:
			calibration_mat_sq = Screen.make_sq(Screen.calibration_mat_4_3)
		elif ratio == Screen.RATIO_16_9:
			calibration_mat_sq = Screen.make_sq(Screen.calibration_mat_16_9)
		else:
			raise Exception('Unrecognized Ratio')
		
		points = np.array(points)[0:3,:]
		print("Points: ")
		print(points)

		print("\nCalibration Mat:")
		print(calibration_mat_sq)

		inv_points = np.linalg.pinv(points)
		print("\nLeft Inverse Points Mat:")
		print(inv_points)

		print("\nIdentity Mat:")
		print(np.matmul(inv_points, points))

		mapping = np.matmul(inv_points, calibration_mat_sq)
		print("\nMapping:")
		print(mapping)

		print("\nRecovered Calibration Mat (points * mapping = calibration mat):")
		print(np.matmul(points, mapping))

		self.ratio = ratio
		self.corners = points

	def make_sq(mat):
		avg = np.mean(mat)
		avg = 0
		return np.c_[mat, np.ones(4)*avg, np.ones(4)*avg]

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