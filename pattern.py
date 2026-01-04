from collections import OrderedDict
from pyexcel_ods3 import save_data
from tqdm import tqdm
import numpy as np
import time

from unravel import unravel

def rotate(rows):
	lengths = [len(row) for row in rows]
	for row in rows:
		while len(row) < max(lengths):
			row.append("")

	new_rows = []
	for i in range(max(lengths)):
		new_row = []
		for row in rows:
			new_row.append(row[i])

		new_rows.append(new_row)

	return new_rows

def split(points):
	points = np.round(points)
	points = np.unique(points, axis=0)

	start = points[0]
	stop = points[-1]

	below_x = [round(start[0])]
	below_y = [round(start[1])]
	above_x = []
	above_y = []

	for point in points:
		if point[1] < 0:
			below_x.append(round(point[0]))
			below_y.append(round(abs(point[1])))
		else:
			above_x.append(round(point[0]))
			above_y.append(round(point[1]))

	below_x.append(round(stop[0]))
	below_y.append(round(stop[1]))

	return below_x, below_y, above_x, above_y

def generate_pattern(env):
	data = OrderedDict()

	pad_splines = env.splines + [env.splines[0]]

	for i in tqdm(range(len(env.splines))):
		quads = pad_splines[i].as_quads(pad_splines[i+1])
		points = unravel(quads, env.length())
		points *= 1000 # turn into mm

		below_x, below_y, above_x, above_y = split(points)

		material_height = round(np.max(above_y) + np.max(below_y))
		centerline_height = round(np.max(below_y))

		above_y.insert(0, "Station height above station (mm)")
		above_x.insert(0, "Station distance from stern (mm)")
		below_x.insert(0, "Station distance from stern (mm)")
		below_y.insert(0, "Station height above station (mm)")

		material = ["Material height", material_height]
		centerline = ["Centerline height", centerline_height]

		table = rotate([above_y, above_x, below_x, below_y, material, centerline])
		data.update({f"Spline {i+1}": table})

	save_data("pattern.ods", data)
	print("Completed write!")
