from scipy.spatial.transform import Rotation as R
import numpy as np

def orthagonal(a, b, c):
	b -= a
	c -= a
	return np.cross(b, c) # ortagonal vector

def move_point(a, b, c, d):
	"""
		Takes 4 3d vectors
		  b
		 /|\
		a | d
		 \|/
		  c
		Moves d so that the orthagonal vector of abc is the same as that of bcd
		while maintaining all lengths between points
	"""

	u = orthagonal(a, b, c)

	print(u)

	pass

def matchup(quad1, quad2):
	"""
		quad1 is the quad in the rotated list that is already "straight"
		quad2 is the quad that we want to align to the other and we know that
			they share 2 points
	"""
	all_points = np.concat((quad1.points, quad2.points), axis=0)
	print(all_points)
	unique, index, counts = np.unique(all_points, return_index=True, return_counts=True, axis=0)
	ad1, b, c, ad2 = unique[np.argsort(counts)]

	if ad1 in quad1.points:
		a = ad1
		d = ad2
	else:
		d = ad1
		a = ad2

	d = move_point(a, b, c, d)
	quad2.points = np.array([b, c, d])

def unravel(quads):
	quads.sort(key=lambda x: x.center()[0])


	rotated = [quads[0]]
	for quad in quads[1:]:
		matchup(rotated[-1], quad)
		rotated.append(quad)

	quit()










def _unravel(quads):
	edges = []
	edge_points = []
	for quad in quads:
		quad_edges = quad.as_edges()
		edges += quad_edges
		edge_points += [edge.points for edge in quad_edges]

	edge_points = np.array(edge_points)

	"""
		We need to make sure that there are no missed same edges

		I think this might actually be impossible becuase all the triangles are
		drawn the same way round. Just incase though ive made sure that cant
		happen.

		The two points in each of the edges are ordered by their distance from
		the origin, which is annoying to do but it should be fine for
		performance since its just number moving around.

		Check if its actually possible for this to happen IDK
	"""
	edge_points_sum = np.sum(edge_points, axis=2)
	edge_points_sort = np.argsort(edge_points_sum, axis=1).flatten()

	offset = np.arange(0, len(edge_points_sort), 2, dtype=np.int64)
	offset = np.repeat(offset, 2)

	edge_points_sort += offset

	edge_points = edge_points.reshape((-1, 2, 3))
	edge_points = edge_points.reshape((-1, 3))
	edge_points = edge_points[edge_points_sort]
	edge_points = edge_points.reshape((-1, 2, 3))

	# End of messing around

	_, index, counts = np.unique(edge_points, return_index=True, return_counts=True, axis=0)

	# This is silly
	new_edges = []
	for j in range(len(index)):
		i = index[j]
		edge = edges[i]
		edge.external = counts[j] == 1
		new_edges.append(edge)

	# import matplotlib.pyplot as plt
 #
	# fig = plt.figure()
	# ax = fig.add_subplot(projection='3d')
 #
	# for edge in new_edges:
	# 	x = edge.points[...,0]
	# 	y = edge.points[...,1]
	# 	z = edge.points[...,2]
 #
	# 	if not edge.external:
	# 		ax.plot(x, y, z, color='green')
	# 	else:
	# 		ax.plot(x, y, z, color='red')
 #
	# plt.show()
 #
	quit()

	return np.array([])
