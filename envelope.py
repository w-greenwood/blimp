import numpy as np

from spline import Spline
from shapes import quad, Triangle

class Envelope():
	def __init__(self, seg: int = 10):
		self.bow = [[3, 0]]
		self.stern = [[-3, 0]]

		self.splines = [
				Spline(self.stern + [[-1, 2],[1, 4]] + self.bow, a)
				for a in np.linspace(0, 360, seg, endpoint=False)
			]

	def as_quads(self):
		quads = []

		pad_splines = self.splines + [self.splines[0]]

		for i in range(len(pad_splines)-1):
			start = pad_splines[i].vector3d()
			stop = pad_splines[i+1].vector3d()

			# add the body of the envelope to the quads list
			for j in range(len(start)-3):
				# offset by 3 to allow groups of 2 as well as 1 buffer at ends
				j += 1

				points = np.array([start[j], stop[j], start[j+1], stop[j+1]])
				quads += quad(points)

			points = np.array([start[0], stop[1], start[1]])
			quads.append(Triangle(points))

			points = np.array([start[-1], stop[-2], start[-2]])
			quads.append(Triangle(points))

		return quads

	def volume(self):
		quads = self.as_quads()
		volumes = [quad.volume() for quad in quads]

		return sum(volumes)

	def area(self):
		quads = self.as_quads()
		areas = [quad.area() for quad in quads]

		return sum(areas)

