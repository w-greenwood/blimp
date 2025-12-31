from tabulate import tabulate
from typing import Optional
import numpy as np

from shapes import quad, Triangle
from spline import Spline
from config import (
		AIR_DENSITY,
		H2_DENSITY,
		ENVELOPE_DENSITY,
		ENVELOPE_THICKNESS
	)

class Envelope():
	def __init__(self, seg: int = 10):
		self.bow = [[3, 0]]
		self.stern = [[-3, 0]]

		self.seg = seg
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

	def volume(self, quads: Optional[iter]):
		if quads is None: quads = self.as_quads()
		volumes = [quad.volume() for quad in quads]

		return sum(volumes)

	def area(self, quads: Optional[iter]):
		if quads is None: quads = self.as_quads()
		areas = [quad.area() for quad in quads]

		return sum(areas)

	def table(self):
		quads =  self.as_quads()

		# define and calculate all useful data
		h2_weight = H2_DENSITY - AIR_DENSITY
		mylar_weight = ENVELOPE_DENSITY - AIR_DENSITY

		area = self.area(quads=quads)
		volume = self.volume(quads=quads)

		length = self.bow[0][0] - self.stern[0][0]

		skin_volume = area * ENVELOPE_THICKNESS
		dry_mass = skin_volume * ENVELOPE_DENSITY
		seg_area = area / self.seg
		seg_dry_mass = dry_mass / self.seg

		h2_mass = H2_DENSITY * volume
		air_mass = (volume + skin_volume) * AIR_DENSITY
		total_lift = (h2_mass + dry_mass) - air_mass

		# generate and return plaintext tables
		geometry_data = [
				["Dry weight", f"{round(dry_mass, 4)} kg", f"{round(seg_dry_mass, 4)} kg"],
				["Area", f"{round(area, 4)} m^2", f"{round(seg_area, 4)} m^2"],
				["Volume", f"{round(volume, 4)} m^3", "-"],
				["Upthrust", f"{round(total_lift, 4)} kg", "-"],
				["Length", f"{round(length, 4)} m", "-"]
			]
		material_data = [
				["Air", f"{AIR_DENSITY} kg/m^3", "-", "-"],
				["Hydrogen", f"{H2_DENSITY} kg/m^3", f"{round(h2_weight, 4)} kg/m^3", "-"],
				["Mylar", f"{ENVELOPE_DENSITY} kg/m^3", f"{round(mylar_weight, 4)} kg/m^3", f"{ENVELOPE_THICKNESS*1000} mm"],
			]
		geometry = tabulate(geometry_data, headers=["", "Envelope", "Segment"])
		material = tabulate(material_data, headers=["Material", "Density", "Upthrust", "Thickness"])
		return f"{geometry}\n\n{material}"
