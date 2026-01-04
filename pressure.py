import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

from config import (
		MAX_PRESSURE,
		AIR_PRESSURE,
		ENVELOPE_THICKNESS,
		ENVELOPE_ELASTICITY
	)

GRAPH_RESOLUTION = 100

def pressure_volume(env, pressure):
	points = [spline.points() for spline in env.splines]
	points = np.array(points)
	points = np.average(points, axis=0)[1:]

	x, r = points[...,0], points[...,1]
	r = r[:-1]

	p_i = pressure - AIR_PRESSURE # internal pressure
	t = ENVELOPE_THICKNESS # thickness
	E = ENVELOPE_ELASTICITY # Youngs modulus

	O_t = (p_i * r) / t # circuferencial stress

	l = np.array([x[i] - x[i+1] for i in range(len(x)-1)]) # lengths
	a = l * 2 * r # cross-section of cylinder

	T = a * O_t # tensile force in wall
	e = T / E # strain

	c = np.pi * 2 * r # circumferance
	dc = e / c # change in circumferance at strain
	dr = np.pi / (dc * 2) # change in radius at strain

	v_a = np.pi * (r ** 2) * l # approximate volume
	v_a = np.sum(v_a) # approximate volume summed

	"""
		Working on the assumtion that
		v_r = v_a * s

		where:
			v_a is the approximate volume
			v_r is the real volume
			s is a scaling factor
	"""

	v_r = env.volume() # real volume
	s = v_r / v_a # scaling factor

	v_ax = np.pi * ((r + dr) ** 2) * l # approximate expanded volume
	v_ax = np.sum(v_ax) # approximate expanded volume summed

	v_rx = s * v_ax # real expanded volume

	return v_rx
