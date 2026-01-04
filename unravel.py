from scipy.spatial.transform import Rotation as R
import numpy as np

from shapes import Triangle

import matplotlib.pyplot as plt

def unit(v):
	v /= np.linalg.norm(v)
	return v

def orthagonal(points):
	a, b = points[1:] - points[0]
	return np.cross(a, b) # ortagonal vector

def angle_between(v1, v2):
	v1 = unit(v1)
	v2 = unit(v2)

	angle = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))
	return angle

def index_of(points, point):
	# could probably make this more efficient
	diff = points - point
	diff = np.abs(diff)
	diff = np.sum(diff, axis=1)
	i = np.argmin(diff)
	return i

def match_rotate(moved, new):
	u1 = orthagonal(moved.points)
	u2 = orthagonal(new.points)

	# get the angle between the orthagonals
	angle = angle_between(u1, u2)

	# get the orthagonal of the othagonals to get the rotation axis
	points = np.stack(([0,0,0], u2, u1))

	rot = orthagonal(points)
	rot = unit(rot)

	# apply the rotation vector
	rot *= angle
	r = R.from_rotvec(rot)

	rotated = Triangle(r.apply(new.points))

	return rotated

def match_move(origional, moved, new, rotated):
	"""

	This probably needs a tidy up its a little bit messy!!!

	"""
	all_points = np.concat((origional.points, new.points), axis=0)
	unique, counts = np.unique(all_points, return_counts=True, axis=0)

	_, _, e1, e2 = np.argsort(counts)

	e1i_moved = index_of(origional.points, unique[e1])
	e2i_moved = index_of(origional.points, unique[e2])
	e1i_rotated = index_of(new.points, unique[e1])
	e2i_rotated = index_of(new.points, unique[e2])
	match_e1_moved = np.copy(moved.points[e1i_moved])
	match_e1_rotated = np.copy(rotated.points[e1i_rotated])

	moved.points -= match_e1_moved
	rotated.points -= match_e1_rotated

	# rotate it around the point we just matched up

	v1 = rotated.points[e1i_rotated] - rotated.points[e2i_rotated]
	v2 = moved.points[e1i_moved] - moved.points[e2i_moved]

	angle = angle_between(v1, v2)
	rot = orthagonal(moved.points)
	rot = unit(rot)
	rot *= angle

	r = R.from_rotvec(rot)

	rotated.points = r.apply(rotated.points)

	moved.points += match_e1_moved
	rotated.points += match_e1_moved

def match_quad(origional, moved, new):
	rotated = match_rotate(moved, new) # has to return new quad
	match_move(origional, moved, new, rotated) # opperates in place

	return rotated

def unravel(quads, length):
	rotated = [quads[0]]
	for i in range(1, len(quads)):
		quad = match_quad(quads[i-1], rotated[-1], quads[i])
		rotated.append(quad)

	# ==========================================================================
	if False:
		fig = plt.figure()
		ax = fig.add_subplot(projection='3d')

		for quad in quads:
			_plot_quad(ax, quad, "blue")

		for quad in rotated:
			_plot_quad(ax, quad, "red")

		plt.show()
	# ==========================================================================

	# rotate all the points so the othagonals line up with the x axis

	u = orthagonal(rotated[0].points)
	angle = angle_between(u, np.array([1., 0., 0.]))

	points = np.stack(([0.,0.,0.], u, [1., 0., 0.]))
	rot = orthagonal(points)
	rot = unit(rot)
	rot *= angle

	r = R.from_rotvec(rot)

	all_points = np.concat([quad.points for quad in rotated], axis=0)
	all_points = np.unique(all_points, axis=0)
	all_points = r.apply(all_points)[...,1:]

	# rotate all the points so that the length of the segment lines up with y

	length = all_points[-1] - all_points[0]
	angle = np.arctan2(length[1], length[0])

	sin = np.sin(angle)
	cos = np.cos(angle)

	x = (all_points[...,0] * cos) + (all_points[...,1] * sin)
	y = (all_points[...,0] * -sin) + (all_points[...,1] * cos)

	# cetner to start at x=0
	x -= x.min()

	# sort the points into above/below the line
	all_points = np.stack((x, y), axis=-1)

	# spin around the points to create a continuous hull
	# x -= x.max() / 2
	# angles = np.arctan2(y, x)
	# i = np.argsort(angles)
	# all_points = np.stack((x, y), axis=-1)[i]

	return all_points











# Plotting functions

def _plot_quad(ax, quad, color="black"):
	points = quad.points
	loop_points = np.concat((points, [points[0]]), axis=0)

	x = loop_points[...,0]
	y = loop_points[...,1]
	z = loop_points[...,2]

	ax.plot(x, y, z, color=color)

	u = orthagonal(points)
	center = np.average(points, axis=0)
	u_points = np.stack((center, center+u))

	x = u_points[...,0]
	y = u_points[...,1]
	z = u_points[...,2]

	ax.plot(x, y, z, color="yellow")

def _plot_points(ax, points):
	x = points[...,0]
	y = points[...,1]
	z = points[...,2]

	ax.scatter(x, y, z, color="yellow")
