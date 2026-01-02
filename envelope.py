from tabulate import tabulate
from typing import Optional
import numpy as np

from spline import Spline
from config import (
		AIR_DENSITY,
		H2_DENSITY,
		ENVELOPE_DENSITY,
		ENVELOPE_THICKNESS
	)

class Envelope():
	def __init__(self, seg: int = 6):
		self.bow = [[3, 0]]
		self.stern = [[-3, 0]]

		self.seg = seg
		self.splines = [
				Spline(self.stern + [[-0.83, 0.83], [1.602, 1.408]] + self.bow, a)
				for a in np.linspace(0, 360, seg, endpoint=False)
			]

		from unravel import unravel

		unravel(self.splines[0].as_quads(self.splines[1]))

	def as_quads(self):
		quads = []

		pad_splines = self.splines + [self.splines[0]]
		for i in range(self.seg):
			quads += pad_splines[i].as_quads(pad_splines[i+1])

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
		h2_weight = AIR_DENSITY - H2_DENSITY
		mylar_weight = AIR_DENSITY - ENVELOPE_DENSITY

		area = self.area(quads=quads)
		volume = self.volume(quads=quads)

		length = self.bow[0][0] - self.stern[0][0]

		skin_volume = area * ENVELOPE_THICKNESS
		dry_mass = skin_volume * ENVELOPE_DENSITY
		seg_area = area / self.seg
		seg_dry_mass = dry_mass / self.seg

		h2_mass = H2_DENSITY * volume
		total_lift = (h2_weight * volume) + (skin_volume * mylar_weight)

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
		return f"ETERNAL\n\n{geometry}\n\n{material}"
