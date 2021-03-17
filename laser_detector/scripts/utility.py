import time


def get_point_between(p1, p2, percent):
	new_x = (p1[0] * (1-percent)) + (p2[0] * percent)
	new_y = (p1[1] * (1-percent)) + (p2[1] * percent)

	return [new_x, new_y]

def current_time_micros():
	return round(time.time() * 1000000)