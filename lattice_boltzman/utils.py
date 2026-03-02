from shapely import Polygon, Point
import numpy as np

from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, jet

def color_map(image):
	# map single uint8 to [uint8 * 3] of a color
	mapper = ScalarMappable(cmap=jet)

	return mapper.to_rgba(image, bytes=True)[...,:3]

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

def find_hull_edge(mask):
	# find the outer edge of pixels not inclusive of the masked area
	edge = np.gradient(mask.astype(int), axis=0)
	edge = np.logical_or(
		np.gradient(mask.astype(int), axis=0),
		np.gradient(mask.astype(int), axis=1)
		)
	edge = np.where(mask, False, edge)

	return edge
