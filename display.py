from typing import Optional
import numpy as np
import pygame_gui
import threading
import pygame
import time

from pattern import generate_pattern
from envelope import Envelope
from utils import rotate
from lattice_boltzman.grid import Grid

WIDTH = 800
HEIGHT = 600

WIDGET_SCALE = 30

THICKNESS = 1

MOVE_SPEED = 5
ZOOM_SPEED = 0.5

RIB_GAP = 4 # should be divisible by RES

class Display():
	def __init__(self, env):
		self.env = env

		pygame.init()
		self.gui = pygame_gui.UIManager((WIDTH, HEIGHT))

		icon = pygame.image.load('example.png')

		pygame.display.set_caption("Bang!")
		pygame.display.set_icon(icon)

		self.clock = pygame.time.Clock()
		self.screen = pygame.display.set_mode([WIDTH, HEIGHT])

		# lattice boltzmann setup
		self.grid = Grid()
		self.grid.update_boundary(self.env.cross_section())
		thread = threading.Thread(target=self.grid.run, daemon=True)
		thread.start()

		# fonts
		fonts = pygame.font.init()
		default = pygame.font.get_default_font()

		monospaced = None
		for font in pygame.font.get_fonts():
			if "mono" in font:
				monospaced = pygame.font.match_font(font)
				break

		self.font = pygame.font.Font(default, 8)
		self.monospaced = pygame.font.Font(monospaced, 10)

		# vectors to move stuff into the middle of its section
		self.pv = [WIDTH*0.25, HEIGHT*0.25]
		self.tv = [WIDTH*0.75, HEIGHT*0.25]
		self.sv = [WIDTH*0.25, HEIGHT*0.75]

		self.resolution = 20
		self.scale = 60
		self.pitch = 45
		self.roll = 0
		self.yaw = 45

		self.transparent = False

	def draw_project(self):
		rib_points = []

		for s in self.env.splines:
			points = s.project(self.yaw,self.pitch,self.roll)
			rib_points.append(points[::RIB_GAP])

			points *= self.scale
			points += self.pv

			pygame.draw.lines(self.screen, "black", False, points, THICKNESS)

		rib_points = np.array(rib_points)
		rib_points = np.rot90(rib_points, 1, axes=(0,1))

		for rib in rib_points:
			pygame.draw.lines(self.screen, "black", True, rib, THICKNESS)

	def draw_project_arrow(self):
		start = np.array(self.env.bow[0] + [0])
		end = np.array(self.env.bow[0] + [0]) + [2,0,0]

		points = [start, end, end-[0.1, 0.1, 0], end, end-[0.1,-0.1,0]]

		points = rotate(points, self.yaw, self.pitch, self.roll)[...,1:]
		points *= self.scale
		points += self.pv

		pygame.draw.lines(self.screen, "red", False, points, THICKNESS)

	def draw_solid(self, quads, a: Optional[int] = None):
		def draw_quad(screen, quad, a=255):
			color = quad.light() * 225

			points = quad.rotated[...,1:]
			points *= self.scale
			points += self.pv
			pygame.draw.polygon(screen, (color,color,color,a), points, width=0)

		front = []
		for quad in quads:
			quad.rotated = rotate(quad.points, self.yaw, self.pitch, self.roll)
			b, c = quad.rotated[1:] - quad.rotated[0]
			u = np.cross(b, c) # ortagonal vector

			if u[0] >= 0: front.append(quad)

		if a is not None:
			screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
			for quad in front:
				draw_quad(screen, quad, a)
			self.screen.blit(screen, (0,0))

		else:
			for quad in front:
				draw_quad(self.screen, quad)


	def draw_top(self):
		self.screen.blit(self.monospaced.render("TOP VIEW", False, (0,0,0)), [WIDTH//2+10,10])
		for s in self.env.splines:
			points = s.top()
			points *= self.scale
			points += self.tv

			pygame.draw.polygon(self.screen, "white", points)

		for s in self.env.splines:
			points = s.top()
			points *= self.scale
			points += self.tv

			pygame.draw.lines(self.screen, "black", False, points, THICKNESS)

	def draw_side(self):
		# draw on the side view
		self.screen.blit(self.monospaced.render("SIDE VIEW", False, (0,0,0)), [10,HEIGHT//2+10])
		for s in self.env.splines:
			points = s.side()
			points *= self.scale
			points += self.sv

			pygame.draw.polygon(self.screen, "white", points)
			pygame.draw.lines(self.screen, "black", False, points, THICKNESS)

	def draw_widget(self):
		def put_text(text, color, point):
			point = transform([point]) + [0,-4]
			self.screen.blit(self.font.render(text, False, color), point[0])

		def transform(points):
			points = rotate(points, self.yaw, self.pitch, self.roll)[...,1:]

			points *= WIDGET_SCALE
			points += [WIDGET_SCALE+20,WIDGET_SCALE+20]

			return points

		x_points = [
				[0,0,0],
				[1,0,0],
				[0.9,0.1,0],
				[1,0,0],
				[0.9,-0.1,0],
			]
		y_points = [
				[0,0,0],
				[0,1,0],
				[0.1,0.9,0],
				[0,1,0],
				[-0.1,0.9,0],
			]
		z_points = [
				[0,0,0],
				[0,0,1],
				[0,0.1,0.9],
				[0,0,1],
				[0,-0.1,0.9],
			]

		pygame.draw.lines(self.screen, "red", False, transform(x_points), THICKNESS)
		pygame.draw.lines(self.screen, "yellow", False, transform(y_points), THICKNESS)
		pygame.draw.lines(self.screen, "green", False, transform(z_points), THICKNESS)

		put_text("x", (255,0,0), [1.2,0,0])
		put_text("y", (255,255,0), [0,1.2,0])
		put_text("z", (0,255,0), [0,0,1.2])

	def draw_table(self):
		table = self.env.table()
		x = WIDTH//2+10
		y = HEIGHT//2+10
		h = 12 # line height

		for (i, line) in enumerate(table.split("\n")):
			self.screen.blit(
				self.monospaced.render(line, False, (0,0,0)), [x, y+(i*h)]
				)

	def check_keys(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_MINUS]:
			self.scale -= ZOOM_SPEED
		elif keys[pygame.K_EQUALS]:
			self.scale += ZOOM_SPEED

		elif keys[pygame.K_UP]:
			self.pitch -= MOVE_SPEED
		elif keys[pygame.K_DOWN]:
			self.pitch += MOVE_SPEED
		elif keys[pygame.K_LEFT]:
			self.yaw -= MOVE_SPEED
		elif keys[pygame.K_RIGHT]:
			self.yaw += MOVE_SPEED

		elif keys[pygame.K_PAGEUP]:
			self.roll -= MOVE_SPEED
		elif keys[pygame.K_PAGEDOWN]:
			self.roll += MOVE_SPEED

	def run(self):
		done = False
		while not done:
			time_delta = self.clock.tick(50)
			self.gui.update(time_delta)

			# DO THE GUI

			# trasparency and generate button

			def f_transparent():
				self.transparent = not self.transparent
			transparent_button = pygame_gui.elements.ui_button.UIButton(
				relative_rect=pygame.Rect(((WIDTH//2)-200, (HEIGHT//2)-20), (100, 20)),
				text="Draw mode",
				command=f_transparent
				)

			def f_generate():
				thread = threading.Thread(target=generate_pattern, args=(self.env,), daemon=True)
				thread.start()
			generate_button = pygame_gui.elements.ui_button.UIButton(
				relative_rect=pygame.Rect(((WIDTH//2)-100, (HEIGHT//2)-20), (100, 20)),
				text="Generate",
				command=f_generate
				)

			# control surface

			spline_picker = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(
				relative_rect=pygame.Rect((WIDTH//2, 0), (WIDTH//4, 20)),
				options_list=[f"Spline {i}" for i in range(4)],
				starting_option="Spline 0"
				)
			point_picker = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(
				relative_rect=pygame.Rect((WIDTH*0.75, 0), (WIDTH//4, 20)),
				options_list=[f"Point {i}" for i in range(4)],
				starting_option="Point 0"
				)

			point_x = pygame_gui.elements.ui_horizontal_slider.UIHorizontalSlider(
				relative_rect=pygame.Rect((WIDTH//2, 40), (WIDTH//2, 20)),
				start_value=0, value_range=range(-3000,3000,1),
				click_increment=1
				)
			label_x = pygame_gui.elements.ui_label.UILabel(
				relative_rect=pygame.Rect((WIDTH//2, 20), (WIDTH//2, 20)),
				text=f"x: {point_x.get_current_value()}"
				)
			point_y = pygame_gui.elements.ui_horizontal_slider.UIHorizontalSlider(
				relative_rect=pygame.Rect((WIDTH//2, 80), (WIDTH//2, 20)),
				start_value=0, value_range=range(-3000,3000,1),
				click_increment=1
				)
			label_y = pygame_gui.elements.ui_label.UILabel(
				relative_rect=pygame.Rect((WIDTH//2, 60), (WIDTH//2, 20)),
				text=f"y: {point_y.get_current_value()}"
				)

			# GUI ENDS

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					done = True

				self.gui.process_events(event)

			self.check_keys()

			self.screen.fill("blue")

			start = round(time.time() * 1000)

			quads = self.env.as_quads()

			if self.transparent:
				self.draw_project()
				self.draw_solid(quads, 120)
			else:
				self.draw_solid(quads)

			self.draw_project_arrow()
			#self.draw_top()
			self.draw_side()
			self.draw_table()

			self.draw_widget()

			total = round(time.time() * 1000 - start)

			self.screen.blit(self.monospaced.render(f"{total} ms / 20 ms (50 Hz)", False, (0,0,0)), [10,HEIGHT//2-10])

			self.gui.draw_ui(self.screen)

			pygame.display.flip()

		pygame.quit()
		pygame.font.quit()
