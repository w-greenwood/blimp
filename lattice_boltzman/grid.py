import numpy as np
import threading

from cv2 import namedWindow, imshow, waitKey, WINDOW_NORMAL

from .utils import find_hull, color_map

"""
Helpful article:
https://vanhunteradams.com/DE1/Lattice_Boltzmann/Lattice_Boltzmann.html

They keep their directions in seperate arrays which are all 1 dimentional. We
use a 4D array for a 4-10x speedup

The grid is 4 dimentional with a shape of (HEIGHT, WIDTH, 3, 3). The shape of
the grid at x, y looks like:

   [[NW | N | NE]
    ----|---|----
    [ W | C | E ]
    ----|---|----
    [SW | S | SE]]
"""

HEIGHT = 64
WIDTH = 256
VISCOSITY = 0.002				# viscosity
OMEGA = 1./(3*VISCOSITY + 0.5)	# relaxation parameter
U0 = 0.1						# initial in-flow speed (eastward)

np.seterr(all="ignore")

class Grid():
	def __init__(self):
		self.state = np.zeros((HEIGHT, WIDTH, 3, 3), dtype=np.float16)
		self.mask = np.zeros((HEIGHT, WIDTH), dtype=int) # the mask of the shape
		self.lock = threading.Lock()

		self.reset()

	def reset(self):
		"""
		During this stage we initialize the lattice with the in-flow speed
		directional to the required flow. Because the side points of the lattice
		stay the same, flow is continuous.
		"""
		# null vector
		u02 = U0 ** 2.
		self.state[...,1,1] += (4/9) * (1 - (1.5*u02))

		# cardinal
		self.state[...,0,1] = (1/9) * (1 - (1.5*u02)) # N
		self.state[...,2,1] = (1/9) * (1 - (1.5*u02)) # S
		self.state[...,1,2] = (1/9) * (1 + (3*U0) + (4.5*u02) - (1.5*u02)) # E
		self.state[...,1,0] = (1/9) * (1 - (3*U0) + (4.5*u02) - (1.5*u02)) # W

		# diagonal
		self.state[...,0,2] = (1/36) * (1 + (3*U0) + (4.5*u02) - (1.5*u02)) # NE
		self.state[...,2,2] = (1/36) * (1 + (3*U0) + (4.5*u02) - (1.5*u02)) # SE
		self.state[...,0,0] = (1/36) * (1 - (3*U0) + (4.5*u02) - (1.5*u02)) # NW
		self.state[...,2,0] = (1/36) * (1 - (3*U0) + (4.5*u02) - (1.5*u02)) # SW

	def update_boundary(self, points):
		"""
		Thread safe update boundary condition (external call).
		Points assumed to be centered around (0,0) but can have arbitrary scale
		"""
		#with self.lock:
		self.mask = find_hull(points, WIDTH, HEIGHT)

	def stream(self):
		"""
		During this stage, the directions of each cell all move outward in their
		own directions, replacing the density of the cell they move into. The
		outer cells are ignored, but densities are moved into them, and boundary
		cells are not treated specially.
		"""
		# cardinal movements
		self.state[1:-1,:][:,...,0,1] = self.state[2:,:][:,...,0,1] # N
		self.state[1:-1,:][:,...,2,1] = self.state[:-2,:][:,...,2,1] # S
		self.state[:,1:-1][:,...,1,2] = self.state[:,:-2][:,...,1,2] # E
		self.state[:,1:-1][:,...,1,0] = self.state[:,2:][:,...,1,0] # W

		# diagonal movements
		self.state[1:-1,1:-1][:,...,0,0] = self.state[2:,2:][:,...,0,0] # NW
		self.state[1:-1,1:-1][:,...,2,2] = self.state[:-2,:-2][:,...,2,2] # SE
		self.state[1:-1,1:-1][:,...,0,2] = self.state[2:,:-2][:,...,0,2] # NE
		self.state[1:-1,1:-1][:,...,2,0] = self.state[:-2,2:][:,...,2,0] # SW

	def bounce(self):
		"""
		During this stage, all boundary condition cells expell all the densities
		moved into them, reversing the direction they came in.
		"""
		if not self.mask.any:
			return

		# cardinal movements
		self.state[2:,1:-1,2,1] = np.where(self.mask[1:-1,1:-1], self.state[1:-1,1:-1,0,1], self.state[2:,1:-1,2,1])
		self.state[:-2,1:-1,0,1] = np.where(self.mask[1:-1,1:-1], self.state[1:-1,1:-1,2,1], self.state[:-2,1:-1,0,1])
		self.state[1:-1,:-2,1,0] = np.where(self.mask[1:-1,1:-1], self.state[1:-1,1:-1,1,2], self.state[1:-1,:-2,1,0])
		self.state[1:-1,2:,1,2] = np.where(self.mask[1:-1,1:-1], self.state[1:-1,1:-1,1,0], self.state[1:-1,2:,1,2])

		# diagonal movements
		self.state[2:,2:,2,2] = np.where(self.mask[1:-1,1:-1], self.state[1:-1,1:-1,0,0], self.state[2:,2:,2,2])
		self.state[:-2,:-2,0,0] = np.where(self.mask[1:-1,1:-1], self.state[1:-1,1:-1,2,2], self.state[:-2,:-2,0,0])
		self.state[2:,:-2,2,0] = np.where(self.mask[1:-1,1:-1], self.state[1:-1,1:-1,0,2], self.state[2:,:-2,2,0])
		self.state[:-2,2:,0,2] = np.where(self.mask[1:-1,1:-1], self.state[1:-1,1:-1,2,0], self.state[:-2,2:,0,2])

		# figure out how to zero the boundaries
		self.state[self.mask] *= 0.

	def collide(self):
		"""
		During this stage we do some maths. Think there is an error here
		"""
		w = np.s_[1:-1,1:-1] # working area

		rho = np.sum(self.state, axis=(-1, -2))[w]	# compute density
		mask = (rho == 0.)

		ux = np.zeros(rho.shape, rho.dtype)
		vx = np.sum(self.state, axis=-2)[w]
		ux[~mask] = (vx[~mask,2]-vx[~mask,0]) * (1-(rho[~mask]-1)+((rho[~mask]-1)**2.))	# compute x velo

		uy = np.zeros(rho.shape, rho.dtype)
		vy = np.sum(self.state, axis=-1)[w]
		uy[~mask] = (vy[~mask,0]-vy[~mask,2]) * (1-(rho[~mask]-1)+((rho[~mask]-1)**2.))	# compute y velo

		# constants
		rho9 = rho / 9
		rho36 = rho / 36

		vx3 = 3 * ux
		vy3 = 3 * uy

		vx2 = ux * ux
		vy2 = uy * uy

		vxvy2 = 2 * ux * uy
		self.v2 = v2 = vx2 + vy2

		v215 = 1.5 * v2

		ca = (3 * uy) + ((9/2) * (uy ** 2))
		cb = (3 * ux) + ((9/2) * (ux ** 2))
		cc = (3/2) * ((ux ** 2) + (uy ** 2))

		# relax cardinals
		self.state[1:-1,1:-1,...,1,2] += OMEGA * ((rho9 * (1 + vx3 + 4.5*vx2 - v215)) - self.state[1:-1,1:-1,...,1,2]) # E
		self.state[1:-1,1:-1,...,1,0] += OMEGA * ((rho9 * (1 - vx3 + 4.5*vx2 - v215)) - self.state[1:-1,1:-1,...,1,0]) # W
		self.state[1:-1,1:-1,...,0,1] += OMEGA * ((rho9 * (1 + vy3 + 4.5*vy2 - v215)) - self.state[1:-1,1:-1,...,0,1]) # N
		self.state[1:-1,1:-1,...,2,1] += OMEGA * ((rho9 * (1 - vy3 + 4.5*vy2 - v215)) - self.state[1:-1,1:-1,...,2,1]) # S

		# relax diagonals
		self.state[1:-1,1:-1,...,0,2] += OMEGA * ((rho36 * (1 + vx3 + vy3 + 4.5*(v2+vxvy2) - v215)) - self.state[1:-1,1:-1,...,0,2])
		self.state[1:-1,1:-1,...,0,0] += OMEGA * ((rho36 * (1 - vx3 + vy3 + 4.5*(v2-vxvy2) - v215)) - self.state[1:-1,1:-1,...,0,0])
		self.state[1:-1,1:-1,...,2,2] += OMEGA * ((rho36 * (1 + vx3 - vy3 + 4.5*(v2-vxvy2) - v215)) - self.state[1:-1,1:-1,...,2,2])
		self.state[1:-1,1:-1,...,2,0] += OMEGA * ((rho36 * (1 - vx3 - vy3 + 4.5*(v2+vxvy2) - v215)) - self.state[1:-1,1:-1,...,2,0])

		# null vector equal to the mass loss
		self.state[1:-1,1:-1,1,1] = rho - (np.sum(self.state, axis=(-1, -2))[w] - self.state[1:-1,1:-1,1,1])

	def update(self):
		# function to run one itteration of the cycle
		self.stream()
		#with self.lock: # only bounce uses the boundary condition
		self.bounce()
		self.collide()

	def run(self):
		namedWindow("LBM Air-flow visualization", WINDOW_NORMAL)

		while True:
			self.update()
			imshow("LBM Air-flow visualization", self.visualization())
			waitKey(1)

	def visualization(self):
		# get the current visualization of the lattice
		image = color_map(self.v2)

		image[self.overlay()] *= 0
		image[self.overlay()] += 255

		return image

	def overlay(self):
		return self.mask[1:-1,1:-1]










if __name__ == "__main__":
	import matplotlib.animation as animation
	import matplotlib.pyplot as plt
	import time

	grid = Grid()

	top = np.array([
		[ 3.        ,  0.        ],
		[ 2.77085931,  0.20606444],
		[ 2.52566672,  0.38063741],
		[ 2.26555591,  0.52523575],
		[ 1.99166059,  0.64137629],
		[ 1.70511445,  0.73057589],
		[ 1.40705117,  0.79435136],
		[ 1.09860446,  0.83421957],
		[ 0.780908  ,  0.85169733],
		[ 0.45509549,  0.8483015 ],
		[ 0.12230063,  0.82554891],
		[-0.21634291,  0.78495641],
		[-0.55970141,  0.72804082],
		[-0.9066412 ,  0.656319  ],
		[-1.25602858,  0.57130777],
		[-1.60672984,  0.47452398],
		[-1.95761131,  0.36748447],
		[-2.30753929,  0.25170608],
		[-2.65538008,  0.12870564],
		[-3.        ,  0.        ]
		])

	bottom = np.array([
		[ 3.        , -0.        ],
		[ 2.77085931, -0.20606444],
		[ 2.52566672, -0.38063741],
		[ 2.26555591, -0.52523575],
		[ 1.99166059, -0.64137629],
		[ 1.70511445, -0.73057589],
		[ 1.40705117, -0.79435136],
		[ 1.09860446, -0.83421957],
		[ 0.780908  , -0.85169733],
		[ 0.45509549, -0.8483015 ],
		[ 0.12230063, -0.82554891],
		[-0.21634291, -0.78495641],
		[-0.55970141, -0.72804082],
		[-0.9066412 , -0.656319  ],
		[-1.25602858, -0.57130777],
		[-1.60672984, -0.47452398],
		[-1.95761131, -0.36748447],
		[-2.30753929, -0.25170608],
		[-2.65538008, -0.12870564],
		[-3.        , -0.        ]
		])[::-1]

	envelope = np.concat((top, bottom), axis=0)

	grid.update_boundary(envelope)

	# Frames per second, and number of seconds
	fps = 600
	nSeconds = 10

	# First set up the figure, the axis, and the plot element we want to animate
	fig, ax = plt.subplots(figsize=(20,5))
	ax.set_title('ETERNAL (Lattice-Boltzmann)')

	grid.update()
	im = plt.imshow(grid.visualization())

	plt.ion()

	while True:
		grid.update()
		masked = np.ma.masked_where(grid.overlay(), grid.v2)
		plt.imshow(masked, cmap="turbo")
		plt.draw()
		plt.pause(0.0001)
		plt.clf()

	quit()
	# ===

	def f(_):
		grid.update()
		grid.drag()
		masked = np.ma.masked_where(grid.overlay(), grid.visualization())
		im.set_array(masked)
		return [im]

	anim = animation.FuncAnimation(
		fig,
		f,
		frames = nSeconds * fps,
		interval = 1000 / fps, # in ms
		)

	print('Done!')

	# Generate an mp4 video of the animation
	f = r"./animation4.mp4"
	writervideo = animation.FFMpegWriter(fps=600)
	anim.save(f, writer=writervideo)


