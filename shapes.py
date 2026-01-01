import numpy as np
import math

LIGHT = [1, 1, 1] / np.linalg.norm([1, 1, 1])

def quad(points):
	return [Triangle(points[:-1]), Triangle(points[1:])]

class Triangle():
	def __init__(self, points):
		self.points = points

	def volume(self):
		# theres a 4th point that is at 0,0 but for some reason we dont actually
		# need it to do the maths right

		stack = np.dstack(self.points)
		volume = np.linalg.det(stack) / 6

		return volume[0]

	def area(self):
		# see https://math.stackexchange.com/a/1951650

		_, b, c = self.points - self.points[0]

		u = np.cross(b, c) # ortagonal vector
		area = np.linalg.norm(u) / 2

		return area

	def center(self):
		return np.average(self.points, axis=0)

	# work out the incident light on the polygon
	def light(self):
		# see https://stackoverflow.com/a/13849249
		unit = self.points / np.linalg.norm(self.points)
		p = np.dot(unit, LIGHT)
		p = np.clip(p, -1.0, 1.0)
		return np.average(np.arccos(p)) / np.pi
