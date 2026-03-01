from shapely import Polygon, Point
import numpy as np

def find_hull(points, width, height):
	"""
	Uses outer arbitrary coords of a shape to find the coords of each boundary
	point for simulation.
	"""

	# scale the shape to be half the height of the lattice
	hull_height = points[...,1].max() - points[...,1].min()
	scale_factor = height / (hull_height * 2.5)
	points = points.astype(float)
	points *= scale_factor

	points[...,0] *= -1

	# position the shape in the center of the lattice
	points += [width//3, height//2]

	hull = Polygon(points)

	f = lambda y, x: hull.contains(Point(x, y))
	mask = np.fromfunction(np.vectorize(f), (height, width), dtype=int)

	return mask
