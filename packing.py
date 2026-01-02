import numpy as np

from config import MATERIAL_WIDTH
from unravel import unravel

def pack_length(quads, seg):
	points = unravel(quads)
	angle = pack_angle(points)

	# something to turn the angle into the amount of material used

	return 0

def pack_angle(points):

	# something to get the maximum angle that the points can be rotated to fit
	# within the material width

	return 0

