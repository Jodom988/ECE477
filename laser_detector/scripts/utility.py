


def get_point_between(p1, p2, percent):
	new_x = (p1[0] * (1-percent)) + (p2[0] * percent)
	new_y = (p1[1] * (1-percent)) + (p2[1] * percent)

	return [new_x, new_y]
