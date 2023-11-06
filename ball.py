from define import *
import hitbox

import pygame as pg
import math

class Ball:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.radius = BALL_RADIUS
		self.color = BALL_COLOR
		self.sprite = pg.image.load("imgs/ball.png")
		self.hitbox = hitbox.Hitbox(self.x, self.y, HITBOX_BALL_COLOR)
		self.hitbox.addPoint(0, -18.5)
		self.hitbox.addPoint(11.5, - 14.5)
		self.hitbox.addPoint(18.5, - 5.5)
		self.hitbox.addPoint(17.5, 7.5)
		self.hitbox.addPoint(11.5, 15.5)
		self.hitbox.addPoint(0, 18.5)
		self.hitbox.addPoint(-10.5, 15.5)
		self.hitbox.addPoint(-16.5, 6.5)
		self.hitbox.addPoint(-16.5, -6.5)
		self.hitbox.addPoint(-9.5, -13.5)
		self.speed = 0
		self.direction = [0, 0]
		self.lastPositions = [(self.x, self.y) for _ in range(BALL_TRAIL_LENGTH)]
		self.lastColors = [BALL_COLOR for _ in range(BALL_TRAIL_LENGTH)]
		self.inWaiting = False


	def draw(self, win):
		if self.inWaiting:
			return

		for i in range(BALL_TRAIL_LENGTH):
			gradiant = i / BALL_TRAIL_LENGTH
			color = (int(self.lastColors[i][0] * BALL_TRAIL_OPACITY),
					int(self.lastColors[i][1] * BALL_TRAIL_OPACITY),
					int(self.lastColors[i][2] * BALL_TRAIL_OPACITY))
			pg.draw.circle(win, color, self.lastPositions[i], self.radius * gradiant)

		win.blit(self.sprite, (self.x - self.radius, self.y - self.radius))
		if DRAW_HITBOX:
			self.hitbox.draw(win)


	def affecteDirection(self, mousePos):
		if self.inWaiting:
			return

		dx = mousePos[0] - self.x
		dy = mousePos[1] - self.y
		norm = math.sqrt(dx**2 + dy**2)

		if norm != 0:
			self.speed += norm
			if self.speed > BALL_MAX_SPEED:
				self.speed = BALL_MAX_SPEED

			self.direction[0] += dx / norm
			self.direction[1] += dy / norm

			norm = math.sqrt(self.direction[0]**2 + self.direction[1]**2)
			self.direction[0] /= norm
			self.direction[1] /= norm


	def updatePosition(self, delta):
		if self.inWaiting:
			return

		# Store last positions
		for i in range (1, BALL_TRAIL_LENGTH):
			self.lastPositions[i - 1] = self.lastPositions[i]
		self.lastPositions[-1] = (self.x, self.y)

		# Store last colors
		for i in range (1, BALL_TRAIL_LENGTH):
			self.lastColors[i - 1] = self.lastColors[i]
		self.lastColors[-1] = self.color

		# Check position along direction and speed
		deltaSpeed = self.speed * delta
		dx = self.x + self.direction[0] * deltaSpeed
		dy = self.y + self.direction[1] * deltaSpeed

		# Collision with x walls
		if dx - self.radius < AREA_RECT[0] or dx + self.radius > AREA_RECT[0] + AREA_RECT[2]:
			self.inWaiting = True

		# Collision with wall up
		if dy - self.radius < AREA_RECT[1]:
			dy += AREA_BORDER_RECT[3]
		elif dy + self.radius > AREA_RECT[1] + AREA_RECT[3]:
			dy -= AREA_BORDER_RECT[3]

		# Affect position along direction and
		self.x = dx
		self.y = dy

		self.hitbox.setPos(self.x, self.y)


		if self.speed < BALL_MAX_SPEED / 2:
			green_gradient = 1 - self.speed / BALL_MAX_SPEED
			blue_gradient = 1 - self.speed / BALL_MAX_SPEED
		else:
			green_gradient = self.speed / BALL_MAX_SPEED
			blue_gradient = 1 - self.speed / BALL_MAX_SPEED
		self.color =	(BALL_COLOR[0],
						BALL_COLOR[1] * green_gradient,
						BALL_COLOR[2] * blue_gradient)

		# Friction
		if self.speed > 0:
			self.speed -= max(BALL_MINIMUM_FRICTION, (self.speed * BALL_FRICTION_STRENGTH)) * delta
			if self.speed < 0:
				self.speed = 0
