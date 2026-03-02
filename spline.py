import numpy as np
import math

from shapes import quad, Triangle
from utils import rotate

RES = 20

class Spline():
	def __init__(self, vertexes, angle):
		self.vertexes = np.array(vertexes)
		self.angle = angle

	# my reimplementation of an arbirary debgree polynomial spline bc the
	# python splines library is so shit its shocking
	def points(self):
		def f(ver, dis):
			if ver.shape[0] == 1:
				return ver[0]

			mid = ver[1:] + ((ver[:-1] - ver[1:]) * dis)
			return f(mid, dis)

		curve = [f(self.vertexes, dis) for dis in np.linspace(0, 1, RES)]
		return np.array(curve)

	# view functions to get the spline points under different conditions

	def top(self): # distance from the datum in the top position
		points = self.points()
		points[...,1] *= math.sin(math.radians(self.angle))
		return points

	def side(self): # distance from the datum in the side position
		points = self.points()
		points[...,1] *= math.cos(math.radians(self.angle))
		return points

	def front(self): # highest point from the front
		return self.points()[...,1].max()

	def vector3d(self):
		points = self.points()
		x = points[...,0]
		y = points[...,1] * math.sin(math.radians(self.angle))
		z = points[...,1] * math.cos(math.radians(self.angle))

		points = np.stack((x, y, z), axis=-1)

		return points

	def project(self, yaw, pitch, roll):
		points = self.vector3d()

		points = rotate(points, yaw, pitch, roll)[...,1:]

		return points

	def as_quads(self, next_spline):
		quads = []

		# get the 3d point pairs
		spline_a = self.vector3d()
		spline_b = next_spline.vector3d()

		pair_splines = np.stack((spline_a, spline_b))

		for i in range(1, RES-2):
			points = pair_splines[:,i:i+2,:].reshape((4,3), order="C")
			quads += quad(points)

		# add the Triangles for the front and back

		# THIS BIT ISNT WORKING FOR SOME REASON
		points = pair_splines[:,0:2,:].reshape((4,3), order="C")[1:4][::-1]
		quads.insert(0, Triangle(points))

		points = pair_splines[:,-2:,:].reshape((4,3), order="C")[:3]
		quads.append(Triangle(points))

		return quads

