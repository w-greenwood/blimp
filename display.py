from typing import Optional
import numpy as np
import threading
import pygame
import time

from pattern import generate_pattern
from pressure import graph_pressure
from envelope import Envelope
from utils import rotate

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

		icon = pygame.image.load('example.png')

		pygame.display.set_caption("Bang!")
		pygame.display.set_icon(icon)

		self.clock = pygame.time.Clock()
		self.screen = pygame.display.set_mode([WIDTH, HEIGHT])

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

			pygame.draw.lines(self.screen, "black", False, points, THICKNESS)

	def draw_side(self):
		self.screen.blit(self.monospaced.render("SIDE VIEW", False, (0,0,0)), [10,HEIGHT//2+10])
		for s in self.env.splines:
			points = s.side()
			points *= self.scale
			points += self.sv

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
		v = [WIDTH//2+10, HEIGHT//2+10]
		self.screen.blit(
			self.monospaced.render(table, False, (0,0,0)), v
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
			self.clock.tick(50)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					done = True

				if event.type == pygame.KEYUP:
					if event.key == pygame.K_t:
						self.transparent = not self.transparent

					# generate the pattern
					# one day this will be a button on the gui???
					elif event.key == pygame.K_g:
						thread = threading.Thread(target=generate_pattern, args=(self.env,), daemon=True)
						thread.start()

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
			self.draw_top()
			self.draw_side()
			self.draw_table()

			self.draw_widget()

			total = round(time.time() * 1000 - start)

			self.screen.blit(self.monospaced.render(f"{total} ms / 20 ms (50 Hz)", False, (0,0,0)), [10,HEIGHT//2-10])

			pygame.display.flip()

		pygame.quit()
		pygame.font.quit()
