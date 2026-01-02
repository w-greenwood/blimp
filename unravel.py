import numpy as np

def unravel(quads):
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
	# quit()

	return np.array([])
